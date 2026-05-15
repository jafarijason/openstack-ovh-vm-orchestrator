"""Network resource endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query, Path
from api.api.schemas.common import ListResponse, PaginationMeta, SuccessResponse
from api.api.schemas.network import NetworkResponse
from api.services.network_service import NetworkService
from api.providers.factory import create_provider
from api.core.exceptions import CloudOperationError, NotFoundError

router = APIRouter(prefix="/networks", tags=["Networks"])


def get_network_service(request: Request, cloud: Optional[str] = Query(None)) -> NetworkService:
    """Get network service for specified cloud.
    
    Args:
        request: FastAPI request object
        cloud: Cloud name from query parameter
        
    Returns:
        NetworkService instance
        
    Raises:
        HTTPException: If service not available
    """
    try:
        if cloud:
            # Create provider for specified cloud
            provider = create_provider(cloud_name=cloud)
            return NetworkService(provider)
        else:
            # Use default service from app state
            service = request.app.state.network_service
            if service is None:
                raise RuntimeError("Network service not initialized")
            return service
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "INVALID_CLOUD", "message": str(e)})


def network_to_response(network) -> NetworkResponse:
    """Convert domain network model to response schema."""
    return NetworkResponse(
        id=network.id,
        name=network.name,
        status=network.status.value,
        is_external=network.is_external,
        is_shared=network.is_shared,
        mtu=network.mtu,
        description=network.description,
        subnets=network.subnets,
        metadata=network.metadata,
        created_at=network.created_at,
        updated_at=network.updated_at,
    )


@router.get("", response_model=ListResponse[NetworkResponse])
async def list_networks(
    request: Request,
    cloud: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List available networks with pagination.
    
    Args:
        request: FastAPI request
        cloud: Cloud name (query parameter)
        limit: Maximum number of results (default: 100, max: 1000)
        offset: Number of results to skip (default: 0)
        
    Returns:
        List of networks with pagination info
        
    Example:
        GET /networks?cloud=ovh&limit=50&offset=0
    """
    try:
        service = get_network_service(request, cloud)
        networks, total = await service.list_networks(limit=limit, offset=offset)
        
        return ListResponse(
            data=[network_to_response(n) for n in networks],
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


@router.get("/{network_id}", response_model=SuccessResponse[NetworkResponse])
async def get_network(
    request: Request,
    network_id: str = Path(..., description="Network unique identifier"),
    cloud: Optional[str] = Query(None),
):
    """Get network by ID.
    
    Args:
        request: FastAPI request
        network_id: Network unique identifier
        cloud: Cloud name (query parameter)
        
    Returns:
        Network details
        
    Example:
        GET /networks/net-private?cloud=ovh
    """
    try:
        service = get_network_service(request, cloud)
        network = await service.get_network(network_id)
        return SuccessResponse(data=network_to_response(network))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail={"code": e.code, "message": e.message})
    except CloudOperationError as e:
        raise HTTPException(status_code=502, detail={"code": e.code, "message": e.message})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": str(e)})
