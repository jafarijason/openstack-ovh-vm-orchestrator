"""SSH Key request/response schemas for API."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SSHKeyResponse(BaseModel):
    """SSH Key response model."""
    name: str = Field(..., description="SSH key name (usually filename without path)")
    public_key: str = Field(..., description="Public SSH key content (ssh-rsa, ssh-ed25519, etc.)")
    fingerprint: Optional[str] = Field(None, description="SSH key fingerprint (MD5 or SHA256)")
    type: Optional[str] = Field(None, description="SSH key type (ssh-rsa, ssh-ed25519, etc.)")
    comment: Optional[str] = Field(None, description="SSH key comment/email")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="SSH key metadata including _raw OpenStack object")
    created_at: Optional[datetime] = Field(None, description="SSH key creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "my-key",
                "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDf...",
                "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
                "type": "ssh-rsa",
                "comment": "user@example.com",
                "metadata": {
                    "_raw": {
                        "name": "my-key",
                        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDf...",
                        "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
                        "created_at": "2025-05-15T10:30:00Z"
                    }
                },
                "created_at": "2025-05-15T10:30:00Z",
                "updated_at": "2025-05-15T10:30:00Z"
            }
        }
    }
