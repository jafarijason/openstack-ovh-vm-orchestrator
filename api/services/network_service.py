"""Service layer for network operations."""

from typing import List, Tuple
from api.core.models import Network
from api.providers.base import BaseProvider


class NetworkService:
    """Network service for managing operations."""

    def __init__(self, provider: BaseProvider):
        """Initialize network service with a provider.
        
        Args:
            provider: Infrastructure provider for cloud operations
        """
        self.provider = provider

    async def get_network(self, network_id: str) -> Network:
        """Get network by ID.
        
        Args:
            network_id: Network unique identifier
            
        Returns:
            Network object
            
        Raises:
            NotFoundError: If network not found
            CloudOperationError: If cloud operation fails
        """
        return await self.provider.get_network(network_id)

    async def list_networks(self, limit: int = 100, offset: int = 0) -> Tuple[List[Network], int]:
        """List all available networks.
        
        Args:
            limit: Maximum number of networks to return
            offset: Number of networks to skip
            
        Returns:
            Tuple of (networks list, total count)
            
        Raises:
            CloudOperationError: If cloud operation fails
        """
        return await self.provider.list_networks(limit=limit, offset=offset)
