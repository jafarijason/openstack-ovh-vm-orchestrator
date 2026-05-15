"""Volume-related request and response schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CreateVolumeRequest(BaseModel):
    """Request to create a new volume."""
    name: str = Field(..., min_length=1, max_length=255, description="Volume name")
    size_gb: int = Field(..., gt=0, le=1000, description="Volume size in GB")
    volume_type: Optional[str] = Field(None, description="Volume type (standard, ssd, etc.)")
    description: Optional[str] = Field(None, max_length=255, description="Volume description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "my-volume",
                "size_gb": 100,
                "volume_type": "standard",
                "description": "Data volume",
                "metadata": {"env": "production"}
            }
        }
    }


class UpdateVolumeRequest(BaseModel):
    """Request to update volume properties."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="New volume name")
    description: Optional[str] = Field(None, max_length=255, description="New description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Update metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "my-volume-updated",
                "description": "Updated data volume"
            }
        }
    }


class AttachVolumeRequest(BaseModel):
    """Request to attach a volume to a VM."""
    vm_id: str = Field(..., description="VM to attach to")
    device: Optional[str] = Field(None, description="Device path (e.g., /dev/vdb)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "vm_id": "vm-12345",
                "device": "/dev/vdb"
            }
        }
    }


class VolumeAttachmentResponse(BaseModel):
    """Volume attachment information."""
    attachment_id: str = Field(..., description="Attachment unique identifier")
    vm_id: str = Field(..., description="VM identifier")
    device: str = Field(..., description="Device path")


class VolumeResponse(BaseModel):
    """Volume response schema."""
    id: str = Field(..., description="Volume unique identifier")
    name: str = Field(..., description="Volume name")
    size_gb: int = Field(..., description="Volume size in GB")
    status: str = Field(..., description="Volume status (AVAILABLE, IN_USE, etc.)")
    volume_type: Optional[str] = Field(None, description="Volume type")
    description: Optional[str] = Field(None, description="Volume description")
    attachments: List[VolumeAttachmentResponse] = Field(..., description="Attachments")
    metadata: Dict[str, Any] = Field(..., description="Custom metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "vol-12345",
                "name": "my-volume",
                "size_gb": 100,
                "status": "IN_USE",
                "volume_type": "standard",
                "description": "Data volume",
                "attachments": [
                    {
                        "attachment_id": "attach-123",
                        "vm_id": "vm-12345",
                        "device": "/dev/vdb"
                    }
                ],
                "metadata": {"env": "production"},
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    }


class CreateSnapshotRequest(BaseModel):
    """Request to create a snapshot."""
    name: str = Field(..., min_length=1, max_length=255, description="Snapshot name")
    volume_id: str = Field(..., description="Volume to snapshot")
    description: Optional[str] = Field(None, max_length=255, description="Snapshot description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "my-volume-snapshot",
                "volume_id": "vol-12345",
                "description": "Daily backup",
                "metadata": {"backup_type": "daily"}
            }
        }
    }


class SnapshotResponse(BaseModel):
    """Snapshot response schema."""
    id: str = Field(..., description="Snapshot unique identifier")
    name: str = Field(..., description="Snapshot name")
    volume_id: str = Field(..., description="Source volume ID")
    size_gb: int = Field(..., description="Snapshot size in GB")
    status: str = Field(..., description="Snapshot status")
    description: Optional[str] = Field(None, description="Description")
    metadata: Dict[str, Any] = Field(..., description="Custom metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "snap-12345",
                "name": "my-volume-snapshot",
                "volume_id": "vol-12345",
                "size_gb": 100,
                "status": "AVAILABLE",
                "description": "Daily backup",
                "metadata": {"backup_type": "daily"},
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    }
