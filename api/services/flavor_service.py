"""Service layer for flavor operations."""

from typing import List, Tuple
from api.core.models import Flavor
from api.providers.base import BaseProvider


class FlavorService:
    """Flavor service for managing operations."""

    def __init__(self, provider: BaseProvider):
        """Initialize flavor service with a provider.
        
        Args:
            provider: Infrastructure provider for cloud operations
        """
        self.provider = provider

    async def list_flavors(self, limit: int = 100, offset: int = 0) -> Tuple[List[Flavor], int]:
        """List all available flavors.
        
        Args:
            limit: Maximum number of flavors to return
            offset: Number of flavors to skip
            
        Returns:
            Tuple of (flavors list, total count)
            
        Raises:
            CloudOperationError: If cloud operation fails
        """
        return await self.provider.list_flavors(limit=limit, offset=offset)
