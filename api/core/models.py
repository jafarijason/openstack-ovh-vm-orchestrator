"""
Domain models for OpenStack VM Orchestrator.

These are pure Python dataclasses/enums that represent the core business domain,
independent of HTTP, ORM, or any other framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class VMStatus(str, Enum):
    """VM lifecycle status."""
    BUILDING = "BUILDING"
    ACTIVE = "ACTIVE"
    STOPPED = "STOPPED"
    REBOOTING = "REBOOTING"
    DELETING = "DELETING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class ImageStatus(str, Enum):
    """Image lifecycle status."""
    QUEUED = "QUEUED"
    SAVING = "SAVING"
    ACTIVE = "ACTIVE"
    KILLED = "KILLED"
    DELETED = "DELETED"
    PENDING_DELETE = "PENDING_DELETE"
    DEACTIVATED = "DEACTIVATED"
    UNKNOWN = "UNKNOWN"


class FlavorStatus(str, Enum):
    """Flavor status."""
    AVAILABLE = "AVAILABLE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Image:
    """Image domain model."""
    id: str
    name: str
    status: ImageStatus
    size_bytes: Optional[int] = None
    disk_format: Optional[str] = None  # qcow2, raw, vmdk, etc.
    container_format: Optional[str] = None  # bare, ovf, etc.
    is_public: bool = False
    is_protected: bool = False
    min_disk_gb: Optional[int] = None
    min_ram_mb: Optional[int] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class VM:
    """Virtual Machine domain model."""
    id: str
    name: str
    status: VMStatus
    image_id: str
    flavor_id: str
    network_ids: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    attached_volumes: List[str] = field(default_factory=list)  # List of volume IDs
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    key_name: Optional[str] = None
    security_groups: List[str] = field(default_factory=list)

    @property
    def is_running(self) -> bool:
        """Check if VM is in running state."""
        return self.status == VMStatus.ACTIVE

    @property
    def is_stopped(self) -> bool:
        """Check if VM is stopped."""
        return self.status == VMStatus.STOPPED


@dataclass
class Flavor:
    """Flavor domain model (VM instance type)."""
    id: str
    name: str
    status: FlavorStatus = FlavorStatus.AVAILABLE
    vcpus: Optional[int] = None
    ram_mb: Optional[int] = None
    disk_gb: Optional[int] = None
    ephemeral_gb: Optional[int] = None  # Ephemeral disk space
    swap_mb: Optional[int] = None
    rxtx_factor: Optional[float] = None
    is_public: bool = True
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SSHKey:
    """SSH Key domain model."""
    name: str
    public_key: str
    fingerprint: Optional[str] = None
    type: Optional[str] = None  # SSH key type (ssh-rsa, ssh-ed25519, etc.)
    comment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
