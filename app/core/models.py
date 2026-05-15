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


class VolumeStatus(str, Enum):
    """Volume lifecycle status."""
    CREATING = "CREATING"
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    DELETING = "DELETING"
    ERROR = "ERROR"
    BACKING_UP = "BACKING_UP"
    RESTORING_BACKUP = "RESTORING_BACKUP"
    UNKNOWN = "UNKNOWN"


class SnapshotStatus(str, Enum):
    """Snapshot lifecycle status."""
    CREATING = "CREATING"
    AVAILABLE = "AVAILABLE"
    DELETING = "DELETING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


@dataclass
class VolumeAttachment:
    """Volume attachment to a VM."""
    attachment_id: str
    vm_id: str
    device: str  # Device path like /dev/vdb


@dataclass
class Volume:
    """Volume domain model."""
    id: str
    name: str
    size_gb: int
    status: VolumeStatus
    volume_type: Optional[str] = None
    description: Optional[str] = None
    attachments: List[VolumeAttachment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_attached(self) -> bool:
        """Check if volume is attached to any VM."""
        return len(self.attachments) > 0


@dataclass
class Snapshot:
    """Snapshot domain model."""
    id: str
    name: str
    volume_id: str
    status: SnapshotStatus
    size_gb: int
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
