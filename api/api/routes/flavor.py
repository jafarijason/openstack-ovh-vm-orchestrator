"""Flavor resource endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query
from api.api.schemas.common import ListResponse, PaginationMeta
from api.api.schemas.flavor import FlavorResponse
from api.services.flavor_service import FlavorService
from api.providers.factory import create_provider
from api.core.exceptions import CloudOperationError, NotFoundError

router = APIRouter(prefix="/flavors", tags=["Flavors"])


def get_flavor_service(request: Request, cloud: Optional[str] = Query(None)) -> FlavorService:
    """Get flavor service for specified cloud.
    
    Args:
        request: FastAPI request object
        cloud: Cloud name from query parameter
        
    Returns:
        FlavorService instance
        
    Raises:
        HTTPException: If service not available
    """
    try:
        if cloud:
            # Create provider for specified cloud
            provider = create_provider(cloud_name=cloud)
            return FlavorService(provider)
        else:
            # Use default service from app state
            service = request.app.state.flavor_service
            if service is None:
                raise RuntimeError("Flavor service not initialized")
            return service
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "INVALID_CLOUD", "message": str(e)})


def flavor_to_response(flavor) -> FlavorResponse:
    """Convert domain flavor model to response schema."""
    return FlavorResponse(
        id=flavor.id,
        name=flavor.name,
        status=flavor.status.value,
        vcpus=flavor.vcpus,
        ram_mb=flavor.ram_mb,
        disk_gb=flavor.disk_gb,
        ephemeral_gb=flavor.ephemeral_gb,
        swap_mb=flavor.swap_mb,
        rxtx_factor=flavor.rxtx_factor,
        is_public=flavor.is_public,
        description=flavor.description,
        metadata=flavor.metadata,
        created_at=flavor.created_at,
        updated_at=flavor.updated_at,
    )


@router.get("", response_model=ListResponse[FlavorResponse])
async def list_flavors(
    request: Request,
    cloud: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List available flavors with pagination.
    
    Args:
        request: FastAPI request
        cloud: Cloud name (query parameter)
        limit: Maximum number of results (default: 100, max: 1000)
        offset: Number of results to skip (default: 0)
        
    Returns:
        List of flavors with pagination info
        
    Example:
        GET /flavors?cloud=ovh&limit=50&offset=0
    """
    try:
        service = get_flavor_service(request, cloud)
        flavors, total = await service.list_flavors(limit=limit, offset=offset)
        
        return ListResponse(
            data=[flavor_to_response(f) for f in flavors],
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
