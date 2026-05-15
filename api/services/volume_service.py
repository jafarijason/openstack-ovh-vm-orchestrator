"""Volume service layer.

Orchestrates volume operations using the provider abstraction.
Contains business logic independent of HTTP framework.
"""

from typing import List, Optional
from api.providers.base import BaseProvider
from api.core.models import Volume, Snapshot


class VolumeService:
    """Service for volume and snapshot operations."""

    def __init__(self, provider: BaseProvider):
        """Initialize volume service.

        Args:
            provider: Infrastructure provider instance
        """
        self.provider = provider

    # Volume Operations
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
        return await self.provider.create_volume(
            name=name,
            size_gb=size_gb,
            volume_type=volume_type,
            description=description,
            metadata=metadata,
        )

    async def get_volume(self, volume_id: str) -> Volume:
        """Get volume by ID.

        Args:
            volume_id: Volume unique identifier

        Returns:
            Volume object
        """
        return await self.provider.get_volume(volume_id)

    async def list_volumes(self, limit: int = 100, offset: int = 0) -> tuple[List[Volume], int]:
        """List all volumes.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of volumes, total count)
        """
        return await self.provider.list_volumes(limit=limit, offset=offset)

    async def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume.

        Args:
            volume_id: Volume unique identifier

        Returns:
            True if deleted, False if not found
        """
        return await self.provider.delete_volume(volume_id)

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
        return await self.provider.attach_volume(
            volume_id=volume_id,
            vm_id=vm_id,
            device=device,
        )

    async def detach_volume(self, volume_id: str) -> Volume:
        """Detach a volume from its VM.

        Args:
            volume_id: Volume unique identifier

        Returns:
            Updated Volume object
        """
        return await self.provider.detach_volume(volume_id)

    # Snapshot Operations
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
        return await self.provider.create_snapshot(
            name=name,
            volume_id=volume_id,
            description=description,
            metadata=metadata,
        )

    async def get_snapshot(self, snapshot_id: str) -> Snapshot:
        """Get snapshot by ID.

        Args:
            snapshot_id: Snapshot unique identifier

        Returns:
            Snapshot object
        """
        return await self.provider.get_snapshot(snapshot_id)

    async def list_snapshots(self, limit: int = 100, offset: int = 0) -> tuple[List[Snapshot], int]:
        """List all snapshots.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of snapshots, total count)
        """
        return await self.provider.list_snapshots(limit=limit, offset=offset)

    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot.

        Args:
            snapshot_id: Snapshot unique identifier

        Returns:
            True if deleted, False if not found
        """
        return await self.provider.delete_snapshot(snapshot_id)
