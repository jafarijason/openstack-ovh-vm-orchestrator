"""VM API routes."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from api.api.schemas.common import SuccessResponse, ErrorResponse
from api.api.schemas.vm import (
    CreateVMRequest,
    UpdateVMRequest,
    VMResponse,
    VMActionRequest,
    VMActionResponse,
)
from api.services.vm_service import VMService
from api.core.exceptions import OrchestratorException
from api.core.models import VM
from api.providers.factory import create_provider

router = APIRouter(prefix="/vms", tags=["VMs"])


def get_vm_service(request: Request, cloud: Optional[str] = Query(None)) -> VMService:
    """Get VM service instance from app state or create for specified cloud.
    
    Args:
        request: FastAPI request object
        cloud: Optional cloud name to use. If not provided, uses default cloud.
    
    Returns:
        VMService instance
    """
    try:
        # Get the active cloud from app state
        active_cloud = getattr(request.app.state, 'active_cloud', None)
        
        # If cloud param matches active cloud, use the pre-initialized service from app state
        if cloud and cloud == active_cloud:
            service = request.app.state.vm_service
            if service is None:
                raise RuntimeError("VM service not initialized")
            return service
        elif cloud:
            # Create provider for specified cloud
            provider = create_provider(cloud_name=cloud)
            return VMService(provider)
        else:
            # Use default service from app state
            service = request.app.state.vm_service
            if service is None:
                raise RuntimeError("VM service not initialized")
            return service
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "INVALID_CLOUD", "message": str(e)})


def vm_to_response(vm: VM) -> VMResponse:
    """Convert domain VM model to response schema."""
    return VMResponse(
        id=vm.id,
        name=vm.name,
        status=vm.status.value,
        image_id=vm.image_id,
        flavor_id=vm.flavor_id,
        network_ids=vm.network_ids,
        attached_volumes=vm.attached_volumes,
        key_name=vm.key_name,
        security_groups=vm.security_groups,
        metadata=vm.metadata,
        created_at=vm.created_at,
        updated_at=vm.updated_at,
    )


@router.post("", response_model=SuccessResponse[VMResponse], status_code=201)
async def create_vm(
    request: CreateVMRequest,
    cloud: Optional[str] = Query(None, description="Cloud name to use for this operation"),
    service: VMService = Depends(get_vm_service),
) -> dict:
    """Create a new VM.

    Args:
        request: VM creation parameters
        service: VM service

    Returns:
        Created VM response

    Raises:
        ValidationError: If input is invalid
        CloudConnectionError: If cannot connect to cloud
        CloudOperationError: If cloud operation fails
    """
    try:
        vm = await service.create_vm(
            name=request.name,
            image_id=request.image_id,
            flavor_id=request.flavor_id,
            network_ids=request.network_ids,
            key_name=request.key_name,
            security_groups=request.security_groups,
            metadata=request.metadata,
        )
        return {
            "success": True,
            "data": vm_to_response(vm),
            "message": f"VM '{vm.name}' created successfully",
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.get("/{vm_id}", response_model=SuccessResponse[VMResponse])
async def get_vm(
    vm_id: str,
    cloud: Optional[str] = Query(None, description="Cloud name to use for this operation"),
    service: VMService = Depends(get_vm_service),
) -> dict:
    """Get VM by ID.

    Args:
        vm_id: VM unique identifier
        service: VM service

    Returns:
        VM response

    Raises:
        NotFoundError: If VM not found
    """
    try:
        vm = await service.get_vm(vm_id)
        return {
            "success": True,
            "data": vm_to_response(vm),
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.get("", response_model=dict)
async def list_vms(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    cloud: Optional[str] = Query(None, description="Cloud name to use for this operation"),
    service: VMService = Depends(get_vm_service),
) -> dict:
    """List all VMs with pagination.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        service: VM service

    Returns:
        List of VMs with pagination metadata
    """
    try:
        vms, total = await service.list_vms(limit=limit, offset=offset)
        pages = (total + limit - 1) // limit  # Ceiling division
        page = (offset // limit) + 1

        return {
            "success": True,
            "data": [vm_to_response(vm) for vm in vms],
            "pagination": {
                "total": total,
                "page": page,
                "per_page": limit,
                "pages": pages,
            },
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.delete("/{vm_id}", status_code=204)
async def delete_vm(
    vm_id: str,
    cloud: Optional[str] = Query(None, description="Cloud name to use for this operation"),
    service: VMService = Depends(get_vm_service),
) -> None:
    """Delete a VM.

    Args:
        vm_id: VM unique identifier
        service: VM service

    Raises:
        NotFoundError: If VM not found
    """
    try:
        deleted = await service.delete_vm(vm_id)
        if not deleted:
            raise HTTPException(status_code=404, detail={"code": "VM_NOT_FOUND", "message": f"VM {vm_id} not found"})
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/{vm_id}/action", response_model=SuccessResponse[VMActionResponse])
async def perform_vm_action(
    vm_id: str,
    request: VMActionRequest,
    cloud: Optional[str] = Query(None, description="Cloud name to use for this operation"),
    service: VMService = Depends(get_vm_service),
) -> dict:
    """Perform action on VM (start, stop, reboot).

    Args:
        vm_id: VM unique identifier
        request: Action parameters
        service: VM service

    Returns:
        Action response

    Raises:
        ValidationError: If action is invalid
        NotFoundError: If VM not found
        OperationNotAllowedError: If action not allowed in current state
    """
    try:
        if request.action == "start":
            vm = await service.start_vm(vm_id)
        elif request.action == "stop":
            vm = await service.stop_vm(vm_id)
        elif request.action == "reboot":
            vm = await service.reboot_vm(vm_id)
        else:
            raise HTTPException(
                status_code=400,
                detail={"code": "INVALID_ACTION", "message": f"Unknown action: {request.action}"},
            )

        return {
            "success": True,
            "data": VMActionResponse(
                id=vm.id,
                action=request.action,
                message=f"VM {request.action} initiated successfully",
            ),
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})
