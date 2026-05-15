"""Image resource endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query
from api.api.schemas.common import ListResponse, PaginationMeta
from api.api.schemas.image import ImageResponse
from api.services.image_service import ImageService
from api.providers.factory import create_provider
from api.core.exceptions import CloudOperationError, NotFoundError

router = APIRouter(prefix="/images", tags=["Images"])


def get_image_service(request: Request, cloud: Optional[str] = Query(None)) -> ImageService:
    """Get image service for specified cloud.
    
    Args:
        request: FastAPI request object
        cloud: Cloud name from query parameter
        
    Returns:
        ImageService instance
        
    Raises:
        HTTPException: If service not available
    """
    try:
        if cloud:
            # Create provider for specified cloud
            provider = create_provider(cloud_name=cloud)
            return ImageService(provider)
        else:
            # Use default service from app state
            service = request.app.state.image_service
            if service is None:
                raise RuntimeError("Image service not initialized")
            return service
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "INVALID_CLOUD", "message": str(e)})


def image_to_response(image) -> ImageResponse:
    """Convert domain image model to response schema."""
    return ImageResponse(
        id=image.id,
        name=image.name,
        status=image.status.value,
        size_bytes=image.size_bytes,
        disk_format=image.disk_format,
        container_format=image.container_format,
        is_public=image.is_public,
        is_protected=image.is_protected,
        min_disk_gb=image.min_disk_gb,
        min_ram_mb=image.min_ram_mb,
        description=image.description,
        metadata=image.metadata,
        created_at=image.created_at,
        updated_at=image.updated_at,
    )


@router.get("", response_model=ListResponse[ImageResponse])
async def list_images(
    request: Request,
    cloud: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List available images with pagination.
    
    Args:
        request: FastAPI request
        cloud: Cloud name (query parameter)
        limit: Maximum number of results (default: 100, max: 1000)
        offset: Number of results to skip (default: 0)
        
    Returns:
        List of images with pagination info
        
    Example:
        GET /images?cloud=ovh&limit=50&offset=0
    """
    try:
        service = get_image_service(request, cloud)
        images, total = await service.list_images(limit=limit, offset=offset)
        
        return ListResponse(
            data=[image_to_response(img) for img in images],
            pagination=PaginationMeta(
                total=total,
                page=(offset // limit) + 1 if limit > 0 else 1,
                per_page=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 0,
            ),
        )
    except CloudOperationError as e:
        raise HTTPException(status_code=502, detail={"code": e.code, "message": e.message})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": str(e)})
