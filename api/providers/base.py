"""
Base provider interface (abstract base class).
All provider implementations must inherit from this class to ensure
consistent interface and behavior.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from api.core.models import VM, Image, Flavor, SSHKey, Network
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
    # Image Operations
    @abstractmethod
    async def get_image(self, image_id: str) -> Image:
        """Get image by ID.
        Args:
            image_id: Image unique identifier
        Returns:
            Image object
        """
        pass
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
    async def get_flavor(self, flavor_id: str) -> Flavor:
        """Get flavor by ID.
        Args:
            flavor_id: Flavor unique identifier
        Returns:
            Flavor object
        """
        pass
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
    # SSH Key Operations
    @abstractmethod
    async def get_ssh_key(self, key_name: str) -> SSHKey:
        """Get SSH key by name.
        Args:
            key_name: SSH key name
        Returns:
            SSHKey object
        """
        pass
    @abstractmethod
    async def list_ssh_keys(self, limit: int = 100, offset: int = 0) -> tuple[List[SSHKey], int]:
        """List all SSH keys with pagination.
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
        Returns:
            Tuple of (list of SSH keys, total count)
        """
        pass
    # Network Operations
    @abstractmethod
    async def get_network(self, network_id: str) -> Network:
        """Get network by ID.
        Args:
            network_id: Network unique identifier
        Returns:
            Network object
        """
        pass
    @abstractmethod
    async def list_networks(self, limit: int = 100, offset: int = 0) -> tuple[List[Network], int]:
        """List all networks with pagination.
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
        Returns:
            Tuple of (list of networks, total count)
        """
        pass
