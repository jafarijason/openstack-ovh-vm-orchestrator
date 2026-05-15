"""
OpenStack provider implementation using openstacksdk.

This provider connects to real OpenStack clouds (like OVH) and
maps cloud operations to the provider interface.
"""

from typing import List, Optional
from datetime import datetime
from app.providers.base import BaseProvider
from app.core.models import VM, VMStatus, Volume, VolumeStatus, Snapshot, SnapshotStatus, VolumeAttachment
from app.core.exceptions import (
    CloudConnectionError,
    CloudOperationError,
    NotFoundError,
    ConflictError,
    OperationNotAllowedError,
)

try:
    from engine import OpenStackEngine
except ImportError:
    raise ImportError("OpenStackEngine not available. Install openstacksdk and configure clouds.yaml")


class OpenStackProvider(BaseProvider):
    """OpenStack provider using openstacksdk."""

    def __init__(self, cloud_name: Optional[str] = None):
        """Initialize OpenStack provider.

        Args:
            cloud_name: Name of cloud in clouds.yaml (defaults to OS_CLOUD env var)

        Raises:
            CloudConnectionError: If unable to connect to cloud
        """
        try:
            self.engine = OpenStackEngine(cloud_name=cloud_name)
        except Exception as e:
            raise CloudConnectionError(cloud_name or "default", str(e))

    async def check_connection(self) -> bool:
        """Check if connected to OpenStack cloud."""
        try:
            info = self.engine.get_cloud_info()
            return info is not None
        except Exception:
            return False

    def _map_vm_status(self, os_status: str) -> VMStatus:
        """Map OpenStack VM status to our VMStatus enum."""
        status_map = {
            "BUILDING": VMStatus.BUILDING,
            "ACTIVE": VMStatus.ACTIVE,
            "STOPPED": VMStatus.STOPPED,
            "REBOOTING": VMStatus.REBOOTING,
            "DELETING": VMStatus.DELETING,
            "ERROR": VMStatus.ERROR,
        }
        return status_map.get(os_status.upper(), VMStatus.UNKNOWN)

    def _map_volume_status(self, os_status: str) -> VolumeStatus:
        """Map OpenStack volume status to our VolumeStatus enum."""
        status_map = {
            "CREATING": VolumeStatus.CREATING,
            "AVAILABLE": VolumeStatus.AVAILABLE,
            "IN_USE": VolumeStatus.IN_USE,
            "DELETING": VolumeStatus.DELETING,
            "ERROR": VolumeStatus.ERROR,
            "BACKING_UP": VolumeStatus.BACKING_UP,
            "RESTORING_BACKUP": VolumeStatus.RESTORING_BACKUP,
        }
        return status_map.get(os_status.upper(), VolumeStatus.UNKNOWN)

    def _map_snapshot_status(self, os_status: str) -> SnapshotStatus:
        """Map OpenStack snapshot status to our SnapshotStatus enum."""
        status_map = {
            "CREATING": SnapshotStatus.CREATING,
            "AVAILABLE": SnapshotStatus.AVAILABLE,
            "DELETING": SnapshotStatus.DELETING,
            "ERROR": SnapshotStatus.ERROR,
        }
        return status_map.get(os_status.upper(), SnapshotStatus.UNKNOWN)

    def _vm_from_os(self, server) -> VM:
        """Convert OpenStack server object to our VM model."""
        return VM(
            id=server.id,
            name=server.name,
            status=self._map_vm_status(server.status),
            image_id=server.image.get("id") if server.image else "",
            flavor_id=server.flavor.get("id") if server.flavor else "",
            network_ids=list(server.networks.keys()) if server.networks else [],
            key_name=server.key_name,
            security_groups=[sg.get("name", "") for sg in (server.security_groups or [])],
            metadata=dict(server.metadata) if server.metadata else {},
            attached_volumes=[vol.get("id", "") for vol in (server.attached_volumes or [])],
            created_at=server.created_at,
            updated_at=server.updated_at,
        )

    def _volume_from_os(self, volume) -> Volume:
        """Convert OpenStack volume object to our Volume model."""
        attachments = [
            VolumeAttachment(
                attachment_id=att.get("id", ""),
                vm_id=att.get("server_id", ""),
                device=att.get("device", ""),
            )
            for att in (volume.attachments or [])
        ]
        return Volume(
            id=volume.id,
            name=volume.name,
            size_gb=volume.size,
            status=self._map_volume_status(volume.status),
            volume_type=volume.volume_type,
            description=volume.description,
            attachments=attachments,
            metadata=dict(volume.metadata) if volume.metadata else {},
            created_at=volume.created_at,
            updated_at=volume.updated_at,
        )

    def _snapshot_from_os(self, snapshot) -> Snapshot:
        """Convert OpenStack snapshot object to our Snapshot model."""
        return Snapshot(
            id=snapshot.id,
            name=snapshot.name,
            volume_id=snapshot.volume_id,
            size_gb=snapshot.size,
            status=self._map_snapshot_status(snapshot.status),
            description=snapshot.description,
            metadata=dict(snapshot.metadata) if snapshot.metadata else {},
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )

    # VM Operations
    async def create_vm(
        self,
        name: str,
        image_id: str,
        flavor_id: str,
        network_ids: List[str],
        key_name: Optional[str] = None,
        security_groups: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> VM:
        """Create a new VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            
            # Build network list
            networks = [{"uuid": nid} for nid in network_ids]
            
            # Create server
            server = compute.create_server(
                name=name,
                image_id=image_id,
                flavor_id=flavor_id,
                networks=networks,
                key_name=key_name,
                security_groups=security_groups,
                metadata=metadata or {},
                wait=False,  # Don't wait for server to fully boot
            )
            return self._vm_from_os(server)
        except Exception as e:
            raise CloudOperationError("create_vm", str(e))

    async def get_vm(self, vm_id: str) -> VM:
        """Get VM from OpenStack."""
        try:
            compute = self.engine.get_compute()
            server = compute.get_server(vm_id)
            if not server:
                raise NotFoundError("VM", vm_id)
            return self._vm_from_os(server)
        except NotFoundError:
            raise
        except Exception as e:
            raise CloudOperationError("get_vm", str(e))

    async def list_vms(self, limit: int = 100, offset: int = 0) -> tuple[List[VM], int]:
        """List VMs from OpenStack."""
        try:
            compute = self.engine.get_compute()
            servers = list(compute.servers(limit=limit, marker=offset))
            # Get total count (this is approximate)
            total = len(servers) + offset
            return [self._vm_from_os(s) for s in servers], total
        except Exception as e:
            raise CloudOperationError("list_vms", str(e))

    async def delete_vm(self, vm_id: str) -> bool:
        """Delete VM from OpenStack."""
        try:
            compute = self.engine.get_compute()
            result = compute.delete_server(vm_id, wait=False)
            return result is not False
        except Exception as e:
            if "not found" in str(e).lower():
                return False
            raise CloudOperationError("delete_vm", str(e))

    async def start_vm(self, vm_id: str) -> VM:
        """Start a stopped VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            server = await self.get_vm(vm_id)
            
            if server.status == VMStatus.STOPPED:
                compute.start_server(vm_id)
            elif server.status != VMStatus.ACTIVE:
                raise OperationNotAllowedError("start", server.status.value)
            
            # Return updated state
            updated = compute.get_server(vm_id)
            return self._vm_from_os(updated)
        except (NotFoundError, OperationNotAllowedError):
            raise
        except Exception as e:
            raise CloudOperationError("start_vm", str(e))

    async def stop_vm(self, vm_id: str) -> VM:
        """Stop a running VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            server = await self.get_vm(vm_id)
            
            if server.status == VMStatus.ACTIVE:
                compute.stop_server(vm_id)
            elif server.status != VMStatus.STOPPED:
                raise OperationNotAllowedError("stop", server.status.value)
            
            # Return updated state
            updated = compute.get_server(vm_id)
            return self._vm_from_os(updated)
        except (NotFoundError, OperationNotAllowedError):
            raise
        except Exception as e:
            raise CloudOperationError("stop_vm", str(e))

    async def reboot_vm(self, vm_id: str) -> VM:
        """Reboot a VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            server = await self.get_vm(vm_id)
            
            if server.status != VMStatus.ACTIVE:
                raise OperationNotAllowedError("reboot", server.status.value)
            
            compute.reboot_server(vm_id, reboot_type="SOFT")
            
            # Return updated state
            updated = compute.get_server(vm_id)
            return self._vm_from_os(updated)
        except (NotFoundError, OperationNotAllowedError):
            raise
        except Exception as e:
            raise CloudOperationError("reboot_vm", str(e))

    # Volume Operations
    async def create_volume(
        self,
        name: str,
        size_gb: int,
        volume_type: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Volume:
        """Create a new volume on OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            volume = block_storage.create_volume(
                name=name,
                size=size_gb,
                volume_type=volume_type,
                description=description,
                metadata=metadata or {},
                wait=False,
            )
            return self._volume_from_os(volume)
        except Exception as e:
            raise CloudOperationError("create_volume", str(e))

    async def get_volume(self, volume_id: str) -> Volume:
        """Get volume from OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            volume = block_storage.get_volume(volume_id)
            if not volume:
                raise NotFoundError("Volume", volume_id)
            return self._volume_from_os(volume)
        except NotFoundError:
            raise
        except Exception as e:
            raise CloudOperationError("get_volume", str(e))

    async def list_volumes(self, limit: int = 100, offset: int = 0) -> tuple[List[Volume], int]:
        """List volumes from OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            volumes = list(block_storage.volumes(limit=limit, marker=offset))
            total = len(volumes) + offset
            return [self._volume_from_os(v) for v in volumes], total
        except Exception as e:
            raise CloudOperationError("list_volumes", str(e))

    async def delete_volume(self, volume_id: str) -> bool:
        """Delete volume from OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            result = block_storage.delete_volume(volume_id, wait=False)
            return result is not False
        except Exception as e:
            if "not found" in str(e).lower():
                return False
            raise CloudOperationError("delete_volume", str(e))

    async def attach_volume(
        self,
        volume_id: str,
        vm_id: str,
        device: Optional[str] = None,
    ) -> Volume:
        """Attach volume to VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            compute.create_volume_attachment(
                server_id=vm_id,
                volume_id=volume_id,
                device=device,
            )
            # Return updated volume
            return await self.get_volume(volume_id)
        except Exception as e:
            raise CloudOperationError("attach_volume", str(e))

    async def detach_volume(self, volume_id: str) -> Volume:
        """Detach volume from its VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            volume = await self.get_volume(volume_id)
            
            if not volume.is_attached:
                raise ConflictError("Volume not attached", "VOLUME_NOT_ATTACHED")
            
            # Find attachment and detach
            for attachment in volume.attachments:
                compute.delete_volume_attachment(
                    attachment_id=attachment.attachment_id,
                    server_id=attachment.vm_id,
                )
            
            return await self.get_volume(volume_id)
        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            raise CloudOperationError("detach_volume", str(e))

    # Snapshot Operations
    async def create_snapshot(
        self,
        name: str,
        volume_id: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Snapshot:
        """Create a snapshot on OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            snapshot = block_storage.create_snapshot(
                name=name,
                volume_id=volume_id,
                description=description,
                metadata=metadata or {},
                wait=False,
            )
            return self._snapshot_from_os(snapshot)
        except Exception as e:
            raise CloudOperationError("create_snapshot", str(e))

    async def get_snapshot(self, snapshot_id: str) -> Snapshot:
        """Get snapshot from OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            snapshot = block_storage.get_snapshot(snapshot_id)
            if not snapshot:
                raise NotFoundError("Snapshot", snapshot_id)
            return self._snapshot_from_os(snapshot)
        except NotFoundError:
            raise
        except Exception as e:
            raise CloudOperationError("get_snapshot", str(e))

    async def list_snapshots(self, limit: int = 100, offset: int = 0) -> tuple[List[Snapshot], int]:
        """List snapshots from OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            snapshots = list(block_storage.snapshots(limit=limit, marker=offset))
            total = len(snapshots) + offset
            return [self._snapshot_from_os(s) for s in snapshots], total
        except Exception as e:
            raise CloudOperationError("list_snapshots", str(e))

    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot from OpenStack."""
        try:
            block_storage = self.engine.get_block_storage()
            result = block_storage.delete_snapshot(snapshot_id, wait=False)
            return result is not False
        except Exception as e:
            if "not found" in str(e).lower():
                return False
            raise CloudOperationError("delete_snapshot", str(e))
