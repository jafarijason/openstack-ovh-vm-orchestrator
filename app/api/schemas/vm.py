"""VM-related request and response schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CreateVMRequest(BaseModel):
    """Request to create a new VM."""
    name: str = Field(..., min_length=1, max_length=255, description="VM name")
    image_id: str = Field(..., description="Image ID to boot from")
    flavor_id: str = Field(..., description="Flavor/instance type ID")
    network_ids: List[str] = Field(..., min_items=1, description="List of network IDs to attach")
    key_name: Optional[str] = Field(None, description="SSH key name for authentication")
    security_groups: List[str] = Field(default_factory=list, description="Security group names")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "my-vm",
                "image_id": "8a2d8e80-c940-43fa-afa0-d2f8024fcf0a",
                "flavor_id": "2",
                "network_ids": ["net-123"],
                "key_name": "my-key",
                "security_groups": ["default"],
                "metadata": {"env": "production"}
            }
        }
    }


class UpdateVMRequest(BaseModel):
    """Request to update VM properties."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="New VM name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Update metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "my-vm-updated",
                "metadata": {"env": "staging"}
            }
        }
    }


class VMResponse(BaseModel):
    """VM response schema."""
    id: str = Field(..., description="VM unique identifier")
    name: str = Field(..., description="VM name")
    status: str = Field(..., description="VM status (BUILDING, ACTIVE, STOPPED, etc.)")
    image_id: str = Field(..., description="Image ID")
    flavor_id: str = Field(..., description="Flavor ID")
    network_ids: List[str] = Field(..., description="Attached network IDs")
    attached_volumes: List[str] = Field(..., description="Attached volume IDs")
    key_name: Optional[str] = Field(None, description="SSH key name")
    security_groups: List[str] = Field(..., description="Security groups")
    metadata: Dict[str, Any] = Field(..., description="Custom metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "vm-12345",
                "name": "my-vm",
                "status": "ACTIVE",
                "image_id": "8a2d8e80-c940-43fa-afa0-d2f8024fcf0a",
                "flavor_id": "2",
                "network_ids": ["net-123"],
                "attached_volumes": ["vol-456"],
                "key_name": "my-key",
                "security_groups": ["default"],
                "metadata": {"env": "production"},
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    }


class VMActionRequest(BaseModel):
    """Request for VM actions (start, stop, reboot)."""
    action: str = Field(..., description="Action to perform: start, stop, reboot")

    model_config = {
        "json_schema_extra": {
            "example": {"action": "reboot"}
        }
    }


class VMActionResponse(BaseModel):
    """Response from VM action."""
    id: str = Field(..., description="VM unique identifier")
    action: str = Field(..., description="Action performed")
    message: str = Field(..., description="Action result message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "vm-12345",
                "action": "reboot",
                "message": "VM reboot initiated"
            }
        }
    }
