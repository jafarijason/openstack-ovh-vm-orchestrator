"""VM service layer.

Orchestrates VM operations using the provider abstraction.
Contains business logic independent of HTTP framework.
"""

from typing import List, Optional
from api.providers.base import BaseProvider
from api.core.models import VM


class VMService:
    """Service for VM operations."""

    def __init__(self, provider: BaseProvider):
        """Initialize VM service.

        Args:
            provider: Infrastructure provider instance
        """
        self.provider = provider

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
        """Create a new VM.

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
        return await self.provider.create_vm(
            name=name,
            image_id=image_id,
            flavor_id=flavor_id,
            network_ids=network_ids,
            key_name=key_name,
            security_groups=security_groups,
            metadata=metadata,
        )

    async def get_vm(self, vm_id: str) -> VM:
        """Get VM by ID.

        Args:
            vm_id: VM unique identifier

        Returns:
            VM object
        """
        return await self.provider.get_vm(vm_id)

    async def list_vms(self, limit: int = 100, offset: int = 0) -> tuple[List[VM], int]:
        """List all VMs.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of VMs, total count)
        """
        return await self.provider.list_vms(limit=limit, offset=offset)

    async def delete_vm(self, vm_id: str) -> bool:
        """Delete a VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            True if deleted, False if not found
        """
        return await self.provider.delete_vm(vm_id)

    async def start_vm(self, vm_id: str) -> VM:
        """Start a stopped VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            Updated VM object
        """
        return await self.provider.start_vm(vm_id)

    async def stop_vm(self, vm_id: str) -> VM:
        """Stop a running VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            Updated VM object
        """
        return await self.provider.stop_vm(vm_id)

    async def reboot_vm(self, vm_id: str) -> VM:
        """Reboot a VM.

        Args:
            vm_id: VM unique identifier

        Returns:
            Updated VM object
        """
        return await self.provider.reboot_vm(vm_id)
