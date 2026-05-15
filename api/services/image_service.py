"""Image service.

Orchestrates image operations using the provider abstraction.
Contains business logic independent of HTTP framework.
"""

from typing import List, Tuple
from api.providers.base import BaseProvider
from api.core.models import Image


class ImageService:
    """Service for image operations."""

    def __init__(self, provider: BaseProvider):
        """Initialize image service.

        Args:
            provider: Infrastructure provider instance
        """
        self.provider = provider

    async def list_images(self, limit: int = 100, offset: int = 0) -> Tuple[List[Image], int]:
        """List available images.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (list of images, total count)
        """
        return await self.provider.list_images(limit=limit, offset=offset)
