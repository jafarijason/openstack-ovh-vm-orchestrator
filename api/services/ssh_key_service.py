"""Service layer for SSH key operations."""

from typing import List, Tuple
from api.core.models import SSHKey
from api.providers.base import BaseProvider


class SSHKeyService:
    """SSH Key service for managing operations."""

    def __init__(self, provider: BaseProvider):
        """Initialize SSH key service with a provider.
        
        Args:
            provider: Infrastructure provider for cloud operations
        """
        self.provider = provider

    async def get_ssh_key(self, key_name: str) -> SSHKey:
        """Get SSH key by name.
        
        Args:
            key_name: SSH key name
            
        Returns:
            SSHKey object
            
        Raises:
            NotFoundError: If SSH key not found
        """
        return await self.provider.get_ssh_key(key_name)

    async def list_ssh_keys(self, limit: int = 100, offset: int = 0) -> Tuple[List[SSHKey], int]:
        """List all SSH keys.
        
        Args:
            limit: Maximum number of SSH keys to return
            offset: Number of SSH keys to skip
            
        Returns:
            Tuple of (SSH keys list, total count)
            
        Raises:
            CloudOperationError: If cloud operation fails
        """
        return await self.provider.list_ssh_keys(limit=limit, offset=offset)
