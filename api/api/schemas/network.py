"""Network request/response schemas for API."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class NetworkResponse(BaseModel):
    """Network response model."""
    id: str = Field(..., description="Unique network identifier")
    name: str = Field(..., description="Network name")
    status: str = Field(..., description="Network status (ACTIVE, BUILD, DOWN, ERROR, UNKNOWN)")
    is_external: bool = Field(False, description="Whether network is external/provider network")
    is_shared: bool = Field(False, description="Whether network is shared across projects")
    mtu: Optional[int] = Field(None, description="Maximum transmission unit in bytes")
    description: Optional[str] = Field(None, description="Network description")
    subnets: List[str] = Field(default_factory=list, description="List of subnet IDs on this network")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Network metadata including _raw OpenStack object")
    created_at: Optional[datetime] = Field(None, description="Network creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "net-private",
                "name": "Private Network",
                "status": "ACTIVE",
                "is_external": False,
                "is_shared": False,
                "mtu": 1500,
                "description": "Private network for internal communication",
                "subnets": ["subnet-private"],
                "metadata": {
                    "_raw": {
                        "id": "net-private",
                        "name": "Private Network",
                        "status": "ACTIVE",
                        "admin_state_up": True,
                        "shared": False,
                        "external": False,
                        "mtu": 1500,
                    }
                },
                "created_at": "2025-05-15T10:30:00Z",
                "updated_at": "2025-05-15T10:30:00Z"
            }
        }
    }
