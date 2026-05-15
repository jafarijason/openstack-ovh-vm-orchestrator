"""Flavor request/response schemas for API."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class FlavorResponse(BaseModel):
    """Flavor response model."""
    id: str = Field(..., description="Unique flavor identifier")
    name: str = Field(..., description="Flavor name (e.g., 'm1.small', 't2.micro')")
    status: str = Field(..., description="Flavor status (AVAILABLE, UNKNOWN)")
    vcpus: Optional[int] = Field(None, description="Number of virtual CPUs")
    ram_mb: Optional[int] = Field(None, description="RAM in megabytes")
    disk_gb: Optional[int] = Field(None, description="Root disk size in gigabytes")
    ephemeral_gb: Optional[int] = Field(None, description="Ephemeral disk size in gigabytes")
    swap_mb: Optional[int] = Field(None, description="Swap disk size in megabytes")
    rxtx_factor: Optional[float] = Field(None, description="Network receive/transmit bandwidth factor")
    is_public: bool = Field(True, description="Whether flavor is available to all projects")
    description: Optional[str] = Field(None, description="Flavor description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flavor metadata including _raw OpenStack object")
    created_at: Optional[datetime] = Field(None, description="Flavor creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "2",
                "name": "m1.small",
                "status": "AVAILABLE",
                "vcpus": 1,
                "ram_mb": 2048,
                "disk_gb": 20,
                "ephemeral_gb": 0,
                "swap_mb": 0,
                "rxtx_factor": 1.0,
                "is_public": True,
                "description": "Small flavor with 1 vCPU and 2GB RAM",
                "metadata": {
                    "_raw": {
                        "id": "2",
                        "name": "m1.small",
                        "ram": 2048,
                        "disk": 20,
                        "vcpus": 1,
                    }
                },
                "created_at": "2025-05-15T10:30:00Z",
                "updated_at": "2025-05-15T10:30:00Z"
            }
        }
    }
