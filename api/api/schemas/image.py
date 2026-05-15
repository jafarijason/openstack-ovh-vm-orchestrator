"""Image request/response schemas for API."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ImageResponse(BaseModel):
    """Image response model."""
    id: str = Field(..., description="Unique image identifier")
    name: str = Field(..., description="Image name")
    status: str = Field(..., description="Image status (ACTIVE, QUEUED, SAVING, etc.)")
    size_bytes: Optional[int] = Field(None, description="Image size in bytes")
    disk_format: Optional[str] = Field(None, description="Disk format (qcow2, raw, vmdk, etc.)")
    container_format: Optional[str] = Field(None, description="Container format (bare, ovf, etc.)")
    is_public: bool = Field(False, description="Whether image is public")
    is_protected: bool = Field(False, description="Whether image is protected from deletion")
    min_disk_gb: Optional[int] = Field(None, description="Minimum disk size required in GB")
    min_ram_mb: Optional[int] = Field(None, description="Minimum RAM required in MB")
    description: Optional[str] = Field(None, description="Image description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Image metadata including _raw OpenStack object")
    created_at: Optional[datetime] = Field(None, description="Image creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "img-ubuntu-20-04",
                "name": "Ubuntu 20.04 LTS",
                "status": "ACTIVE",
                "size_bytes": 2147483648,
                "disk_format": "qcow2",
                "container_format": "bare",
                "is_public": True,
                "is_protected": False,
                "min_disk_gb": 5,
                "min_ram_mb": 512,
                "description": "Ubuntu 20.04 LTS base image",
                "metadata": {
                    "_raw": {
                        "id": "img-ubuntu-20-04",
                        "name": "Ubuntu 20.04 LTS",
                        "status": "ACTIVE",
                        "properties": {}
                    }
                },
                "created_at": "2025-05-15T10:30:00Z",
                "updated_at": "2025-05-15T10:30:00Z"
            }
        }
    }
