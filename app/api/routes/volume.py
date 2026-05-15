"""Volume API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.api.schemas.common import SuccessResponse
from app.api.schemas.volume import (
    CreateVolumeRequest,
    UpdateVolumeRequest,
    AttachVolumeRequest,
    VolumeResponse,
    VolumeAttachmentResponse,
    CreateSnapshotRequest,
    SnapshotResponse,
)
from app.services.volume_service import VolumeService
from app.core.exceptions import OrchestratorException
from app.core.models import Volume, Snapshot

router = APIRouter(prefix="/volumes", tags=["Volumes"])
snapshot_router = APIRouter(prefix="/snapshots", tags=["Snapshots"])


def get_volume_service(request: Request) -> VolumeService:
    """Get volume service instance from app state."""
    service = request.app.state.volume_service
    if service is None:
        raise RuntimeError("Volume service not initialized")
    return service


def volume_to_response(vol: Volume) -> VolumeResponse:
    """Convert domain Volume model to response schema."""
    return VolumeResponse(
        id=vol.id,
        name=vol.name,
        size_gb=vol.size_gb,
        status=vol.status.value,
        volume_type=vol.volume_type,
        description=vol.description,
        attachments=[
            VolumeAttachmentResponse(
                attachment_id=att.attachment_id,
                vm_id=att.vm_id,
                device=att.device,
            )
            for att in vol.attachments
        ],
        metadata=vol.metadata,
        created_at=vol.created_at,
        updated_at=vol.updated_at,
    )


def snapshot_to_response(snap: Snapshot) -> SnapshotResponse:
    """Convert domain Snapshot model to response schema."""
    return SnapshotResponse(
        id=snap.id,
        name=snap.name,
        volume_id=snap.volume_id,
        size_gb=snap.size_gb,
        status=snap.status.value,
        description=snap.description,
        metadata=snap.metadata,
        created_at=snap.created_at,
        updated_at=snap.updated_at,
    )


# Volume Endpoints
@router.post("", response_model=SuccessResponse[VolumeResponse], status_code=201)
async def create_volume(
    request: CreateVolumeRequest,
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """Create a new volume.

    Args:
        request: Volume creation parameters
        service: Volume service

    Returns:
        Created volume response
    """
    try:
        volume = await service.create_volume(
            name=request.name,
            size_gb=request.size_gb,
            volume_type=request.volume_type,
            description=request.description,
            metadata=request.metadata,
        )
        return {
            "success": True,
            "data": volume_to_response(volume),
            "message": f"Volume '{volume.name}' created successfully",
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.get("/{volume_id}", response_model=SuccessResponse[VolumeResponse])
async def get_volume(
    volume_id: str,
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """Get volume by ID.

    Args:
        volume_id: Volume unique identifier
        service: Volume service

    Returns:
        Volume response
    """
    try:
        volume = await service.get_volume(volume_id)
        return {
            "success": True,
            "data": volume_to_response(volume),
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.get("", response_model=dict)
async def list_volumes(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """List all volumes with pagination.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        service: Volume service

    Returns:
        List of volumes with pagination metadata
    """
    try:
        volumes, total = await service.list_volumes(limit=limit, offset=offset)
        pages = (total + limit - 1) // limit
        page = (offset // limit) + 1

        return {
            "success": True,
            "data": [volume_to_response(vol) for vol in volumes],
            "pagination": {
                "total": total,
                "page": page,
                "per_page": limit,
                "pages": pages,
            },
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/{volume_id}/attach", response_model=SuccessResponse[VolumeResponse])
async def attach_volume(
    volume_id: str,
    request: AttachVolumeRequest,
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """Attach volume to VM.

    Args:
        volume_id: Volume unique identifier
        request: Attachment parameters
        service: Volume service

    Returns:
        Updated volume response
    """
    try:
        volume = await service.attach_volume(
            volume_id=volume_id,
            vm_id=request.vm_id,
            device=request.device,
        )
        return {
            "success": True,
            "data": volume_to_response(volume),
            "message": f"Volume attached to VM {request.vm_id}",
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/{volume_id}/detach", response_model=SuccessResponse[VolumeResponse])
async def detach_volume(
    volume_id: str,
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """Detach volume from VM.

    Args:
        volume_id: Volume unique identifier
        service: Volume service

    Returns:
        Updated volume response
    """
    try:
        volume = await service.detach_volume(volume_id)
        return {
            "success": True,
            "data": volume_to_response(volume),
            "message": "Volume detached successfully",
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.delete("/{volume_id}", status_code=204)
async def delete_volume(
    volume_id: str,
    service: VolumeService = Depends(get_volume_service),
) -> None:
    """Delete a volume.

    Args:
        volume_id: Volume unique identifier
        service: Volume service
    """
    try:
        deleted = await service.delete_volume(volume_id)
        if not deleted:
            raise HTTPException(status_code=404, detail={"code": "VOLUME_NOT_FOUND", "message": f"Volume {volume_id} not found"})
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


# Snapshot Endpoints
@snapshot_router.post("", response_model=SuccessResponse[SnapshotResponse], status_code=201)
async def create_snapshot(
    request: CreateSnapshotRequest,
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """Create a volume snapshot.

    Args:
        request: Snapshot creation parameters
        service: Volume service

    Returns:
        Created snapshot response
    """
    try:
        snapshot = await service.create_snapshot(
            name=request.name,
            volume_id=request.volume_id,
            description=request.description,
            metadata=request.metadata,
        )
        return {
            "success": True,
            "data": snapshot_to_response(snapshot),
            "message": f"Snapshot '{snapshot.name}' created successfully",
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@snapshot_router.get("/{snapshot_id}", response_model=SuccessResponse[SnapshotResponse])
async def get_snapshot(
    snapshot_id: str,
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """Get snapshot by ID.

    Args:
        snapshot_id: Snapshot unique identifier
        service: Volume service

    Returns:
        Snapshot response
    """
    try:
        snapshot = await service.get_snapshot(snapshot_id)
        return {
            "success": True,
            "data": snapshot_to_response(snapshot),
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@snapshot_router.get("", response_model=dict)
async def list_snapshots(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: VolumeService = Depends(get_volume_service),
) -> dict:
    """List all snapshots with pagination.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        service: Volume service

    Returns:
        List of snapshots with pagination metadata
    """
    try:
        snapshots, total = await service.list_snapshots(limit=limit, offset=offset)
        pages = (total + limit - 1) // limit
        page = (offset // limit) + 1

        return {
            "success": True,
            "data": [snapshot_to_response(snap) for snap in snapshots],
            "pagination": {
                "total": total,
                "page": page,
                "per_page": limit,
                "pages": pages,
            },
        }
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@snapshot_router.delete("/{snapshot_id}", status_code=204)
async def delete_snapshot(
    snapshot_id: str,
    service: VolumeService = Depends(get_volume_service),
) -> None:
    """Delete a snapshot.

    Args:
        snapshot_id: Snapshot unique identifier
        service: Volume service
    """
    try:
        deleted = await service.delete_snapshot(snapshot_id)
        if not deleted:
            raise HTTPException(status_code=404, detail={"code": "SNAPSHOT_NOT_FOUND", "message": f"Snapshot {snapshot_id} not found"})
    except OrchestratorException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})
