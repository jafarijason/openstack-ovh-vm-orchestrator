"""
OpenStack provider implementation using openstacksdk.

This provider connects to real OpenStack clouds (like OVH) and
maps cloud operations to the provider interface.
"""

from typing import List, Optional
from datetime import datetime
from api.providers.base import BaseProvider
from api.core.models import VM, VMStatus, Volume, VolumeStatus, Snapshot, SnapshotStatus, Image, ImageStatus, Flavor, FlavorStatus, SSHKey, VolumeAttachment
from api.core.exceptions import (
    CloudConnectionError,
    CloudOperationError,
    NotFoundError,
    ConflictError,
    OperationNotAllowedError,
)

try:
    from api.engine import OpenStackEngine
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
            error_msg = str(e)
            # Provide helpful error messages for common issues
            if "YOUR_" in error_msg or "Unauthorized" in error_msg or "401" in error_msg:
                error_msg = (
                    f"OpenStack cloud '{cloud_name}' authentication failed. "
                    "Please ensure credentials are configured correctly in clouds.yaml. "
                    "Check your application_credential_secret, password, or auth tokens."
                )
            raise CloudConnectionError(cloud_name or "default", error_msg)

    def _object_to_dict(self, obj) -> dict:
        """Convert OpenStack SDK object to dictionary, preserving all attributes."""
        if isinstance(obj, dict):
            return obj
        if obj is None:
            return {}
        
        result = {}
        try:
            # Try to get all attributes from the object
            if hasattr(obj, '__dict__'):
                for key, value in obj.__dict__.items():
                    if not key.startswith('_'):
                        try:
                            # Safely serialize the value
                            if isinstance(value, (str, int, float, bool, type(None))):
                                result[key] = value
                            elif isinstance(value, (list, tuple)):
                                result[key] = list(value)
                            elif isinstance(value, dict):
                                result[key] = value
                            elif hasattr(value, '__dict__'):
                                # Nested object, recursively convert
                                result[key] = self._object_to_dict(value)
                            else:
                                result[key] = str(value)
                        except (TypeError, AttributeError):
                            result[key] = str(value)
        except Exception:
            pass
        
        return result

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
        # Preserve user metadata and add full OS object as _raw
        metadata = dict(server.metadata) if server.metadata else {}
        metadata["_raw"] = self._object_to_dict(server)
        
        return VM(
            id=server.id,
            name=server.name,
            status=self._map_vm_status(server.status),
            image_id=server.image.get("id") if server.image else "",
            flavor_id=server.flavor.get("id") if server.flavor else "",
            network_ids=list(server.networks.keys()) if server.networks else [],
            key_name=server.key_name,
            security_groups=[sg.get("name", "") for sg in (server.security_groups or [])],
            metadata=metadata,
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
        # Preserve user metadata and add full OS object as _raw
        metadata = dict(volume.metadata) if volume.metadata else {}
        metadata["_raw"] = self._object_to_dict(volume)
        
        return Volume(
            id=volume.id,
            name=volume.name,
            size_gb=volume.size,
            status=self._map_volume_status(volume.status),
            volume_type=volume.volume_type,
            description=volume.description,
            attachments=attachments,
            metadata=metadata,
            created_at=volume.created_at,
            updated_at=volume.updated_at,
        )

    def _snapshot_from_os(self, snapshot) -> Snapshot:
        """Convert OpenStack snapshot object to our Snapshot model."""
        # Preserve user metadata and add full OS object as _raw
        metadata = dict(snapshot.metadata) if snapshot.metadata else {}
        metadata["_raw"] = self._object_to_dict(snapshot)
        
        return Snapshot(
            id=snapshot.id,
            name=snapshot.name,
            volume_id=snapshot.volume_id,
            size_gb=snapshot.size,
            status=self._map_snapshot_status(snapshot.status),
            description=snapshot.description,
            metadata=metadata,
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
            # Only use marker if offset is not 0 (OpenStack quirk)
            if offset > 0:
                servers = list(compute.servers(limit=limit, marker=offset))
            else:
                servers = list(compute.servers(limit=limit))
            
            # Get total count (this is approximate)
            total = len(servers) + offset
            return [self._vm_from_os(s) for s in servers], total
        except Exception as e:
            raise CloudOperationError("list_vms", str(e))

    async def delete_vm(self, vm_id: str) -> bool:
        """Delete VM from OpenStack."""
        try:
            compute = self.engine.get_compute()
            # Note: OVH OpenStack SDK doesn't support 'wait' parameter on delete_server
            result = compute.delete_server(vm_id)
            return True
        except Exception as e:
            if "not found" in str(e).lower():
                return False
            raise CloudOperationError("delete_vm", str(e))

    async def start_vm(self, vm_id: str) -> VM:
        """Start a stopped VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            server = await self.get_vm(vm_id)
            
            # Check if VM can be started
            can_start = False
            if server.status == VMStatus.STOPPED:
                can_start = True
            elif server.status == VMStatus.UNKNOWN:
                # Try to use vm_state from raw metadata as fallback
                raw_vm_state = server.metadata.get("_raw", {}).get("vm_state", "").lower()
                if raw_vm_state == "stopped":
                    can_start = True
                elif raw_vm_state not in ("active", ""):
                    # VM in transitional or error state
                    raise OperationNotAllowedError("start", f"UNKNOWN (vm_state={raw_vm_state})")
            
            if can_start:
                compute.start_server(vm_id)
            elif server.status == VMStatus.ACTIVE:
                # Already running, just return current state
                pass
            else:
                raise OperationNotAllowedError("start", server.status.value)
            
            # Return updated state
            updated = compute.get_server(vm_id)
            return self._vm_from_os(updated)
        except (NotFoundError, OperationNotAllowedError):
            raise
        except Exception as e:
            error_str = str(e).lower()
            # Handle 409 Conflict - VM may already be starting or in transitional state
            if "409" in error_str or "conflict" in error_str:
                raise ConflictError("VM may already be starting or in transitional state", "VM_CONFLICT")
            raise CloudOperationError("start_vm", str(e))

    async def stop_vm(self, vm_id: str) -> VM:
        """Stop a running VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            server = await self.get_vm(vm_id)
            
            # Check if VM can be stopped
            can_stop = False
            if server.status == VMStatus.ACTIVE:
                can_stop = True
            elif server.status == VMStatus.UNKNOWN:
                # Try to use vm_state from raw metadata as fallback
                raw_vm_state = server.metadata.get("_raw", {}).get("vm_state", "").lower()
                if raw_vm_state == "active":
                    can_stop = True
                elif raw_vm_state not in ("stopped", ""):
                    # VM in transitional or error state
                    raise OperationNotAllowedError("stop", f"UNKNOWN (vm_state={raw_vm_state})")
            
            if can_stop:
                compute.stop_server(vm_id)
            elif server.status == VMStatus.STOPPED:
                # Already stopped, just return current state
                pass
            else:
                raise OperationNotAllowedError("stop", server.status.value)
            
            # Return updated state
            updated = compute.get_server(vm_id)
            return self._vm_from_os(updated)
        except (NotFoundError, OperationNotAllowedError):
            raise
        except Exception as e:
            error_str = str(e).lower()
            # Handle 409 Conflict - VM may already be stopping or in transitional state
            if "409" in error_str or "conflict" in error_str:
                raise ConflictError("VM may already be stopping or in transitional state", "VM_CONFLICT")
            raise CloudOperationError("stop_vm", str(e))

    async def reboot_vm(self, vm_id: str) -> VM:
        """Reboot a VM on OpenStack."""
        try:
            compute = self.engine.get_compute()
            server = await self.get_vm(vm_id)
            
            # Check if VM can be rebooted (must be active)
            can_reboot = False
            if server.status == VMStatus.ACTIVE:
                can_reboot = True
            elif server.status == VMStatus.UNKNOWN:
                # Try to use vm_state from raw metadata as fallback
                raw_vm_state = server.metadata.get("_raw", {}).get("vm_state", "").lower()
                if raw_vm_state == "active":
                    can_reboot = True
                else:
                    raise OperationNotAllowedError("reboot", f"UNKNOWN (vm_state={raw_vm_state})")
            else:
                raise OperationNotAllowedError("reboot", server.status.value)
            
            if can_reboot:
                compute.reboot_server(vm_id, reboot_type="SOFT")
            
            # Return updated state
            updated = compute.get_server(vm_id)
            return self._vm_from_os(updated)
        except (NotFoundError, OperationNotAllowedError):
            raise
        except Exception as e:
            error_str = str(e).lower()
            # Handle 409 Conflict - VM may already be rebooting or in transitional state
            if "409" in error_str or "conflict" in error_str:
                raise ConflictError("VM may already be rebooting or in transitional state", "VM_CONFLICT")
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
            block_storage = self.engine.get_volume()
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
            block_storage = self.engine.get_volume()
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
            block_storage = self.engine.get_volume()
            # Only use marker if offset is not 0 (OpenStack quirk)
            if offset > 0:
                volumes = list(block_storage.volumes(limit=limit, marker=offset))
            else:
                volumes = list(block_storage.volumes(limit=limit))
            
            total = len(volumes) + offset
            return [self._volume_from_os(v) for v in volumes], total
        except Exception as e:
            raise CloudOperationError("list_volumes", str(e))

    async def delete_volume(self, volume_id: str) -> bool:
        """Delete volume from OpenStack."""
        try:
            block_storage = self.engine.get_volume()
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
            block_storage = self.engine.get_volume()
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
            block_storage = self.engine.get_volume()
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
            block_storage = self.engine.get_volume()
            # Only use marker if offset is not 0 (OpenStack quirk)
            if offset > 0:
                snapshots = list(block_storage.snapshots(limit=limit, marker=offset))
            else:
                snapshots = list(block_storage.snapshots(limit=limit))
            
            total = len(snapshots) + offset
            return [self._snapshot_from_os(s) for s in snapshots], total
        except Exception as e:
            raise CloudOperationError("list_snapshots", str(e))

    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot from OpenStack."""
        try:
            block_storage = self.engine.get_volume()
            result = block_storage.delete_snapshot(snapshot_id, wait=False)
            return result is not False
        except Exception as e:
            if "not found" in str(e).lower():
                return False
            raise CloudOperationError("delete_snapshot", str(e))

    # Image Operations
    async def list_images(self, limit: int = 100, offset: int = 0) -> tuple[List[Image], int]:
        """List images from OpenStack."""
        try:
            image = self.engine.get_image()
            # Only use marker if offset is not 0 (OpenStack quirk)
            if offset > 0:
                images = list(image.images(limit=limit, marker=offset))
            else:
                images = list(image.images(limit=limit))
            
            total = len(images) + offset
            return [self._image_from_os(img) for img in images], total
        except Exception as e:
            raise CloudOperationError("list_images", str(e))

    def _image_from_os(self, os_image) -> Image:
        """Convert OpenStack image to domain model."""
        # Preserve image properties and add full OS object as _raw
        metadata = dict(getattr(os_image, 'properties', {})) if hasattr(os_image, 'properties') else {}
        metadata["_raw"] = self._object_to_dict(os_image)
        
        return Image(
            id=os_image.id,
            name=os_image.name,
            status=ImageStatus(os_image.status.upper()) if hasattr(os_image, 'status') else ImageStatus.UNKNOWN,
            size_bytes=getattr(os_image, 'size', None),
            disk_format=getattr(os_image, 'disk_format', None),
            container_format=getattr(os_image, 'container_format', None),
            is_public=getattr(os_image, 'is_public', False),
            is_protected=getattr(os_image, 'protected', False),
            min_disk_gb=getattr(os_image, 'min_disk', None),
            min_ram_mb=getattr(os_image, 'min_ram', None),
            description=metadata.get('description'),
            metadata=metadata,
            created_at=getattr(os_image, 'created_at', None),
            updated_at=getattr(os_image, 'updated_at', None),
        )

    async def list_flavors(self, limit: int = 100, offset: int = 0) -> tuple[List[Flavor], int]:
        """List flavors from OpenStack."""
        try:
            compute = self.engine.get_compute()
            # Get all flavors and paginate manually
            all_flavors = list(compute.flavors())
            total = len(all_flavors)
            flavors_page = all_flavors[offset : offset + limit]
            return [self._flavor_from_os(f) for f in flavors_page], total
        except Exception as e:
            raise CloudOperationError("list_flavors", str(e))

    def _flavor_from_os(self, os_flavor) -> Flavor:
        """Convert OpenStack flavor to domain model."""
        # Preserve full OS object as _raw
        metadata = {}
        metadata["_raw"] = self._object_to_dict(os_flavor)
        
        return Flavor(
            id=os_flavor.id,
            name=os_flavor.name,
            status=FlavorStatus.AVAILABLE,
            vcpus=getattr(os_flavor, 'vcpus', None),
            ram_mb=getattr(os_flavor, 'ram', None),
            disk_gb=getattr(os_flavor, 'disk', None),
            ephemeral_gb=getattr(os_flavor, 'ephemeral', None),
            swap_mb=getattr(os_flavor, 'swap', None),
            rxtx_factor=getattr(os_flavor, 'rxtx_factor', None),
            is_public=getattr(os_flavor, 'is_public', True),
            description=getattr(os_flavor, 'description', None),
            metadata=metadata,
            created_at=getattr(os_flavor, 'created_at', None),
            updated_at=getattr(os_flavor, 'updated_at', None),
        )

    async def list_ssh_keys(self, limit: int = 100, offset: int = 0) -> tuple[List[SSHKey], int]:
        """List SSH keys from OpenStack."""
        try:
            compute = self.engine.get_compute()
            # Get all keypairs using OpenStack SDK
            # Note: This returns SSH keypairs configured in the OpenStack project
            all_keypairs = list(compute.keypairs())
            total = len(all_keypairs)
            keypairs_page = all_keypairs[offset : offset + limit]
            return [self._ssh_key_from_os(k) for k in keypairs_page], total
        except Exception as e:
            raise CloudOperationError("list_ssh_keys", str(e))

    def _ssh_key_from_os(self, os_keypair) -> SSHKey:
        """Convert OpenStack keypair to domain model."""
        # Preserve full OS object as _raw
        metadata = {}
        metadata["_raw"] = self._object_to_dict(os_keypair)
        
        return SSHKey(
            name=os_keypair.name,
            public_key=getattr(os_keypair, 'public_key', ''),
            fingerprint=getattr(os_keypair, 'fingerprint', None),
            type=getattr(os_keypair, 'type', None),
            comment=getattr(os_keypair, 'comment', None),
            metadata=metadata,
            created_at=getattr(os_keypair, 'created_at', None),
            updated_at=getattr(os_keypair, 'updated_at', None),
        )
