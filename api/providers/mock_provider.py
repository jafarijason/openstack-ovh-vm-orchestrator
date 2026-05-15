"""
Mock provider implementation for testing.

Stores resources in memory and simulates cloud operations.
Useful for development and testing without real cloud credentials.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4
from api.providers.base import BaseProvider
from api.core.models import VM, VMStatus, Image, ImageStatus, Flavor, FlavorStatus, SSHKey
from api.core.exceptions import NotFoundError, OperationNotAllowedError


class MockProvider(BaseProvider):
    """In-memory mock provider for testing."""

    def __init__(self):
        """Initialize mock provider with empty resource storage."""
        self.vms: dict[str, VM] = {}
        self.images: dict[str, Image] = {}
        self.flavors: dict[str, Flavor] = {}
        self.ssh_keys: dict[str, SSHKey] = {}
        self._connected = True
        self._initialize_sample_images()
        self._initialize_sample_flavors()
        self._initialize_sample_ssh_keys()

    async def check_connection(self) -> bool:
        """Mock connection check always succeeds."""
        return self._connected

    # VM Operations
    async def create_vm(
        self,
        name: str,
        image_id: str,
        flavor_id: str,
        network_ids: List[str],
        key_name: Optional[str] = None,
        security_groups: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> VM:
        """Create a mock VM."""
        vm = VM(
            id=f"vm-{uuid4().hex[:8]}",
            name=name,
            status=VMStatus.BUILDING,
            image_id=image_id,
            flavor_id=flavor_id,
            network_ids=network_ids,
            key_name=key_name,
            security_groups=security_groups or [],
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        # Simulate transition to ACTIVE after creation
        vm.status = VMStatus.ACTIVE
        self.vms[vm.id] = vm
        return vm

    async def get_vm(self, vm_id: str) -> VM:
        """Get mock VM by ID."""
        if vm_id not in self.vms:
            raise NotFoundError("VM", vm_id)
        return self.vms[vm_id]

    async def list_vms(self, limit: int = 100, offset: int = 0) -> tuple[List[VM], int]:
        """List all mock VMs."""
        vms_list = list(self.vms.values())
        total = len(vms_list)
        return vms_list[offset : offset + limit], total

    async def delete_vm(self, vm_id: str) -> bool:
        """Delete a mock VM."""
        if vm_id not in self.vms:
            return False
        del self.vms[vm_id]
        return True

    async def start_vm(self, vm_id: str) -> VM:
        """Start a mock VM."""
        vm = await self.get_vm(vm_id)
        if vm.status == VMStatus.STOPPED:
            vm.status = VMStatus.ACTIVE
            vm.updated_at = datetime.utcnow()
        elif vm.status != VMStatus.ACTIVE:
            raise OperationNotAllowedError("start", vm.status.value)
        return vm

    async def stop_vm(self, vm_id: str) -> VM:
        """Stop a mock VM."""
        vm = await self.get_vm(vm_id)
        if vm.status == VMStatus.ACTIVE:
            vm.status = VMStatus.STOPPED
            vm.updated_at = datetime.utcnow()
        elif vm.status != VMStatus.STOPPED:
            raise OperationNotAllowedError("stop", vm.status.value)
        return vm

    async def reboot_vm(self, vm_id: str) -> VM:
        """Reboot a mock VM."""
        vm = await self.get_vm(vm_id)
        if vm.status != VMStatus.ACTIVE:
            raise OperationNotAllowedError("reboot", vm.status.value)
        vm.status = VMStatus.REBOOTING
        vm.updated_at = datetime.utcnow()
        # Simulate reboot completion
        vm.status = VMStatus.ACTIVE
        return vm

    # Image Operations
    def _initialize_sample_images(self):
        """Initialize mock provider with sample images."""
        sample_images = [
            Image(
                id="img-ubuntu-20-04",
                name="Ubuntu 20.04 LTS",
                status=ImageStatus.ACTIVE,
                disk_format="qcow2",
                container_format="bare",
                size_bytes=2147483648,  # 2GB
                min_disk_gb=5,
                min_ram_mb=512,
                is_public=True,
                metadata={
                    "_raw": {
                        "id": "img-ubuntu-20-04",
                        "name": "Ubuntu 20.04 LTS",
                        "status": "ACTIVE",
                        "size": 2147483648,
                        "disk_format": "qcow2",
                        "container_format": "bare",
                        "is_public": True,
                        "protected": False,
                        "min_disk": 5,
                        "min_ram": 512,
                    }
                },
                created_at=datetime.now() - timedelta(days=30),
            ),
            Image(
                id="img-ubuntu-22-04",
                name="Ubuntu 22.04 LTS",
                status=ImageStatus.ACTIVE,
                disk_format="qcow2",
                container_format="bare",
                size_bytes=3221225472,  # 3GB
                min_disk_gb=5,
                min_ram_mb=512,
                is_public=True,
                metadata={
                    "_raw": {
                        "id": "img-ubuntu-22-04",
                        "name": "Ubuntu 22.04 LTS",
                        "status": "ACTIVE",
                        "size": 3221225472,
                        "disk_format": "qcow2",
                        "container_format": "bare",
                        "is_public": True,
                        "protected": False,
                        "min_disk": 5,
                        "min_ram": 512,
                    }
                },
                created_at=datetime.now() - timedelta(days=20),
            ),
            Image(
                id="img-debian-11",
                name="Debian 11",
                status=ImageStatus.ACTIVE,
                disk_format="qcow2",
                container_format="bare",
                size_bytes=1610612736,  # 1.5GB
                min_disk_gb=5,
                min_ram_mb=512,
                is_public=True,
                metadata={
                    "_raw": {
                        "id": "img-debian-11",
                        "name": "Debian 11",
                        "status": "ACTIVE",
                        "size": 1610612736,
                        "disk_format": "qcow2",
                        "container_format": "bare",
                        "is_public": True,
                        "protected": False,
                        "min_disk": 5,
                        "min_ram": 512,
                    }
                },
                created_at=datetime.now() - timedelta(days=15),
            ),
            Image(
                id="img-centos-7",
                name="CentOS 7",
                status=ImageStatus.ACTIVE,
                disk_format="qcow2",
                container_format="bare",
                size_bytes=2684354560,  # 2.5GB
                min_disk_gb=5,
                min_ram_mb=512,
                is_public=True,
                metadata={
                    "_raw": {
                        "id": "img-centos-7",
                        "name": "CentOS 7",
                        "status": "ACTIVE",
                        "size": 2684354560,
                        "disk_format": "qcow2",
                        "container_format": "bare",
                        "is_public": True,
                        "protected": False,
                        "min_disk": 5,
                        "min_ram": 512,
                    }
                },
                created_at=datetime.now() - timedelta(days=45),
            ),
        ]
        for image in sample_images:
            self.images[image.id] = image

    async def list_images(self, limit: int = 100, offset: int = 0) -> tuple[List[Image], int]:
        """List all mock images."""
        images_list = list(self.images.values())
        total = len(images_list)
        return images_list[offset : offset + limit], total

    async def list_flavors(self, limit: int = 100, offset: int = 0) -> tuple[List[Flavor], int]:
        """List all mock flavors."""
        flavors_list = list(self.flavors.values())
        total = len(flavors_list)
        return flavors_list[offset : offset + limit], total

    def _initialize_sample_flavors(self):
        """Initialize sample flavors for testing."""
        sample_flavors = [
            Flavor(
                id="1",
                name="m1.tiny",
                status=FlavorStatus.AVAILABLE,
                vcpus=1,
                ram_mb=512,
                disk_gb=1,
                ephemeral_gb=0,
                swap_mb=0,
                rxtx_factor=1.0,
                is_public=True,
                description="Tiny flavor with 1 vCPU and 512MB RAM",
                metadata={
                    "_raw": {
                        "id": "1",
                        "name": "m1.tiny",
                        "ram": 512,
                        "disk": 1,
                        "vcpus": 1,
                        "ephemeral": 0,
                        "swap": 0,
                        "rxtx_factor": 1.0,
                        "is_public": True,
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Flavor(
                id="2",
                name="m1.small",
                status=FlavorStatus.AVAILABLE,
                vcpus=1,
                ram_mb=2048,
                disk_gb=20,
                ephemeral_gb=0,
                swap_mb=0,
                rxtx_factor=1.0,
                is_public=True,
                description="Small flavor with 1 vCPU and 2GB RAM",
                metadata={
                    "_raw": {
                        "id": "2",
                        "name": "m1.small",
                        "ram": 2048,
                        "disk": 20,
                        "vcpus": 1,
                        "ephemeral": 0,
                        "swap": 0,
                        "rxtx_factor": 1.0,
                        "is_public": True,
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Flavor(
                id="3",
                name="m1.medium",
                status=FlavorStatus.AVAILABLE,
                vcpus=2,
                ram_mb=4096,
                disk_gb=40,
                ephemeral_gb=0,
                swap_mb=0,
                rxtx_factor=1.0,
                is_public=True,
                description="Medium flavor with 2 vCPUs and 4GB RAM",
                metadata={
                    "_raw": {
                        "id": "3",
                        "name": "m1.medium",
                        "ram": 4096,
                        "disk": 40,
                        "vcpus": 2,
                        "ephemeral": 0,
                        "swap": 0,
                        "rxtx_factor": 1.0,
                        "is_public": True,
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Flavor(
                id="4",
                name="m1.large",
                status=FlavorStatus.AVAILABLE,
                vcpus=4,
                ram_mb=8192,
                disk_gb=80,
                ephemeral_gb=0,
                swap_mb=0,
                rxtx_factor=1.0,
                is_public=True,
                description="Large flavor with 4 vCPUs and 8GB RAM",
                metadata={
                    "_raw": {
                        "id": "4",
                        "name": "m1.large",
                        "ram": 8192,
                        "disk": 80,
                        "vcpus": 4,
                        "ephemeral": 0,
                        "swap": 0,
                        "rxtx_factor": 1.0,
                        "is_public": True,
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
        for flavor in sample_flavors:
            self.flavors[flavor.id] = flavor

    async def list_ssh_keys(self, limit: int = 100, offset: int = 0) -> tuple[List[SSHKey], int]:
        """List all mock SSH keys."""
        ssh_keys_list = list(self.ssh_keys.values())
        total = len(ssh_keys_list)
        return ssh_keys_list[offset : offset + limit], total

    def _initialize_sample_ssh_keys(self):
        """Initialize sample SSH keys for testing."""
        sample_keys = [
            SSHKey(
                name="my-key-1",
                public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDf+8yXZ9WQD3J7Z8K7L8M9O0P1Q2R3S4T5U6V7W8X9Y0Z1a2b3c4d5e6f7g8h9i0j1k2l3 user@laptop",
                fingerprint="aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
                type="ssh-rsa",
                comment="user@laptop",
                metadata={
                    "_raw": {
                        "name": "my-key-1",
                        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDf+8yXZ9WQD3J7Z8K7L8M9O0P1Q2R3S4T5U6V7W8X9Y0Z1a2b3c4d5e6f7g8h9i0j1k2l3 user@laptop",
                        "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
                        "created_at": "2025-05-10T10:30:00Z"
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            SSHKey(
                name="my-key-2",
                public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGf+9yXZ9WQD3J7Z8K7L8M9O0P1Q2R3S4T5U6V7W8X9Y0Z dev@workstation",
                fingerprint="SHA256:ZL0bL5L6M7N8O9P0Q1R2S3T4U5V6W7X8Y9Z0a1b2c3d",
                type="ssh-ed25519",
                comment="dev@workstation",
                metadata={
                    "_raw": {
                        "name": "my-key-2",
                        "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGf+9yXZ9WQD3J7Z8K7L8M9O0P1Q2R3S4T5U6V7W8X9Y0Z dev@workstation",
                        "fingerprint": "SHA256:ZL0bL5L6M7N8O9P0Q1R2S3T4U5V6W7X8Y9Z0a1b2c3d",
                        "created_at": "2025-05-12T14:20:00Z"
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            SSHKey(
                name="ci-deploy-key",
                public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCz+9yXZ9WQD3J7Z8K7L8M9O0P1Q2R3S4T5U6V7W8X9Y0Z1a2b3c4d5e6f7g8h9i0j1k2l3 ci@deploy",
                fingerprint="bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99:aa",
                type="ssh-rsa",
                comment="ci@deploy",
                metadata={
                    "_raw": {
                        "name": "ci-deploy-key",
                        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCz+9yXZ9WQD3J7Z8K7L8M9O0P1Q2R3S4T5U6V7W8X9Y0Z1a2b3c4d5e6f7g8h9i0j1k2l3 ci@deploy",
                        "fingerprint": "bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99:aa",
                        "created_at": "2025-05-01T08:00:00Z"
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
        for i, key in enumerate(sample_keys):
            self.ssh_keys[key.name] = key
