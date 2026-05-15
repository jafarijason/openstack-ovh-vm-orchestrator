"""SSH Key resource endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query
from api.api.schemas.common import ListResponse, PaginationMeta
from api.api.schemas.ssh_key import SSHKeyResponse
from api.services.ssh_key_service import SSHKeyService
from api.providers.factory import create_provider
from api.core.exceptions import CloudOperationError

router = APIRouter(prefix="/ssh-keys", tags=["SSH Keys"])


def get_ssh_key_service(request: Request, cloud: Optional[str] = Query(None)) -> SSHKeyService:
    """Get SSH key service for specified cloud.
    
    Args:
        request: FastAPI request object
        cloud: Cloud name from query parameter
        
    Returns:
        SSHKeyService instance
        
    Raises:
        HTTPException: If service not available
    """
    try:
        if cloud:
            # Create provider for specified cloud
            provider = create_provider(cloud_name=cloud)
            return SSHKeyService(provider)
        else:
            # Use default service from app state
            service = request.app.state.ssh_key_service
            if service is None:
                raise RuntimeError("SSH Key service not initialized")
            return service
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "INVALID_CLOUD", "message": str(e)})


def ssh_key_to_response(ssh_key) -> SSHKeyResponse:
    """Convert domain SSH key model to response schema."""
    return SSHKeyResponse(
        name=ssh_key.name,
        public_key=ssh_key.public_key,
        fingerprint=ssh_key.fingerprint,
        type=ssh_key.type,
        comment=ssh_key.comment,
        metadata=ssh_key.metadata,
        created_at=ssh_key.created_at,
        updated_at=ssh_key.updated_at,
    )


@router.get("", response_model=ListResponse[SSHKeyResponse])
async def list_ssh_keys(
    request: Request,
    cloud: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List available SSH keys with pagination.
    
    Args:
        request: FastAPI request
        cloud: Cloud name (query parameter)
        limit: Maximum number of results (default: 100, max: 1000)
        offset: Number of results to skip (default: 0)
        
    Returns:
        List of SSH keys with pagination info
        
    Example:
        GET /ssh-keys?cloud=ovh&limit=50&offset=0
    """
    try:
        service = get_ssh_key_service(request, cloud)
        ssh_keys, total = await service.list_ssh_keys(limit=limit, offset=offset)
        
        return ListResponse(
            data=[ssh_key_to_response(k) for k in ssh_keys],
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
