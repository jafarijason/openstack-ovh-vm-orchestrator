"""
Base provider interface (abstract base class).

All provider implementations must inherit from this class to ensure
consistent interface and behavior.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from api.core.models import VM, Volume, Snapshot, Image, Flavor


class BaseProvider(ABC):
    """Abstract base provider for infrastructure operations."""

    @abstractmethod
    async def check_connection(self) -> bool:
        """Check if connected to cloud provider.

        Returns:
            True if connected, False otherwise
        """
        pass

    # VM Operations
    @abstractmethod
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
        """Create a new virtual machine.

        Args:
            name: VM name
            image_id: Image to boot from
            flavor_id: Instance type/flavor
            network_ids: Networks to attach
            key_name: SSH key name
            security_groups: Security groups
            metadata: Custom metadata

        Returns:
            Created VM object
        """
        pass

    @abstractmethod
    async def get_vm(self, vm_id: str) -> VM:
        """Get VM by ID.

        Args:
            vm_id: VM unique identifier

        Returns:
            VM object
        """
        pass

    @abstractmethod
    async def list_vms(self, limit: int = 100, offset: int = 0) -> tuple[List[VM], int]:
        """List all VMs with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of VMs, total count)
        """
        pass

    @abstractmethod
    async def delete_vm(self, vm_id: str) -> bool:
        """Delete a VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def start_vm(self, vm_id: str) -> VM:
        """Start a stopped VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            Updated VM object
        """
        pass

    @abstractmethod
    async def stop_vm(self, vm_id: str) -> VM:
        """Stop a running VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            Updated VM object
        """
        pass

    @abstractmethod
    async def reboot_vm(self, vm_id: str) -> VM:
        """Reboot a VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            Updated VM object
        """
        pass

    # Volume Operations
    @abstractmethod
    async def create_volume(
        self,
        name: str,
        size_gb: int,
        volume_type: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Volume:
        """Create a new volume.

        Args:
            name: Volume name
            size_gb: Size in gigabytes
            volume_type: Volume type
            description: Volume description
            metadata: Custom metadata

        Returns:
            Created Volume object
        """
        pass

    @abstractmethod
    async def get_volume(self, volume_id: str) -> Volume:
        """Get volume by ID.

        Args:
            volume_id: Volume unique identifier

        Returns:
            Volume object
        """
        pass

    @abstractmethod
    async def list_volumes(self, limit: int = 100, offset: int = 0) -> tuple[List[Volume], int]:
        """List all volumes with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of volumes, total count)
        """
        pass

    @abstractmethod
    async def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume.

        Args:
            volume_id: Volume unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def attach_volume(
        self,
        volume_id: str,
        vm_id: str,
        device: Optional[str] = None,
    ) -> Volume:
        """Attach a volume to a VM.

        Args:
            volume_id: Volume unique identifier
            vm_id: VM unique identifier
            device: Device path (e.g., /dev/vdb)

        Returns:
            Updated Volume object
        """
        pass

    @abstractmethod
    async def detach_volume(self, volume_id: str) -> Volume:
        """Detach a volume from its VM.

        Args:
            volume_id: Volume unique identifier

        Returns:
            Updated Volume object
        """
        pass

    # Snapshot Operations
    @abstractmethod
    async def create_snapshot(
        self,
        name: str,
        volume_id: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Snapshot:
        """Create a volume snapshot.

        Args:
            name: Snapshot name
            volume_id: Source volume ID
            description: Snapshot description
            metadata: Custom metadata

        Returns:
            Created Snapshot object
        """
        pass

    @abstractmethod
    async def get_snapshot(self, snapshot_id: str) -> Snapshot:
        """Get snapshot by ID.

        Args:
            snapshot_id: Snapshot unique identifier

        Returns:
            Snapshot object
        """
        pass

    @abstractmethod
    async def list_snapshots(self, limit: int = 100, offset: int = 0) -> tuple[List[Snapshot], int]:
        """List all snapshots with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of snapshots, total count)
        """
        pass

    @abstractmethod
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot.

        Args:
            snapshot_id: Snapshot unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    # Image Operations
    @abstractmethod
    async def list_images(self, limit: int = 100, offset: int = 0) -> tuple[List[Image], int]:
        """List all available images with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of images, total count)
        """
        pass

    # Flavor Operations
    @abstractmethod
    async def list_flavors(self, limit: int = 100, offset: int = 0) -> tuple[List[Flavor], int]:
        """List all available flavors with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of flavors, total count)
        """
        pass
