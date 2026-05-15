"""
Pytest configuration and shared fixtures for OpenStack VM Orchestrator tests.
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from api.main import app
from api.providers.mock_provider import MockProvider
from api.services.vm_service import VMService
from api.services.network_service import NetworkService
from api.services.image_service import ImageService
from api.services.flavor_service import FlavorService
from api.services.ssh_key_service import SSHKeyService
from api.core.models import VM, VMStatus, Network, NetworkStatus, Image, Flavor, SSHKey


@pytest.fixture
def client():
    """FastAPI TestClient for integration tests."""
    return TestClient(app)


@pytest_asyncio.fixture
async def mock_provider():
    """Mock cloud provider for testing."""
    return MockProvider()


@pytest_asyncio.fixture
async def vm_service(mock_provider):
    """VM service with mock provider."""
    return VMService(mock_provider)


@pytest_asyncio.fixture
async def network_service(mock_provider):
    """Network service with mock provider."""
    return NetworkService(mock_provider)


@pytest_asyncio.fixture
async def image_service(mock_provider):
    """Image service with mock provider."""
    return ImageService(mock_provider)


@pytest_asyncio.fixture
async def flavor_service(mock_provider):
    """Flavor service with mock provider."""
    return FlavorService(mock_provider)


@pytest_asyncio.fixture
async def ssh_key_service(mock_provider):
    """SSH key service with mock provider."""
    return SSHKeyService(mock_provider)


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_vm_data():
    """Sample VM data for testing."""
    return {
        "name": "test-vm",
        "image_id": "img-001",
        "flavor_id": "m1.small",
        "network_ids": ["net-public"],
        "key_name": "test-key",
        "security_groups": ["default"],
        "metadata": {"env": "test"},
    }


@pytest.fixture
def sample_vm_create_request():
    """Sample VM creation request."""
    return {
        "name": "new-test-vm",
        "image_id": "img-001",
        "flavor_id": "m1.medium",
        "network_ids": ["net-public", "net-private"],
        "key_name": "test-key",
        "security_groups": ["default", "web"],
        "metadata": {"environment": "testing"},
    }


@pytest.fixture
def sample_vm_response():
    """Sample VM API response."""
    return {
        "id": "vm-test-001",
        "name": "test-vm",
        "status": "ACTIVE",
        "image_id": "img-001",
        "flavor_id": "m1.small",
        "network_ids": ["net-public"],
        "attached_volumes": [],
        "key_name": "test-key",
        "security_groups": ["default"],
        "metadata": {"env": "test"},
        "created_at": "2024-05-14T10:00:00Z",
        "updated_at": "2024-05-14T10:00:00Z",
    }


@pytest.fixture
def sample_vm_action_request():
    """Sample VM action request."""
    return {"action": "start"}


@pytest.fixture
def sample_network_response():
    """Sample network API response."""
    return {
        "id": "net-test-001",
        "name": "test-network",
        "status": "ACTIVE",
        "external": False,
        "shared": False,
        "subnets": ["subnet-test"],
        "created_at": "2024-05-14T10:00:00Z",
        "updated_at": "2024-05-14T10:00:00Z",
    }


@pytest.fixture
def sample_image_response():
    """Sample image API response."""
    return {
        "id": "img-test-001",
        "name": "Test Image",
        "description": "Test image for unit testing",
        "disk_format": "qcow2",
        "container_format": "bare",
        "size": 2147483648,
        "visibility": "public",
        "status": "active",
        "created_at": "2024-05-14T10:00:00Z",
        "updated_at": "2024-05-14T10:00:00Z",
    }


@pytest.fixture
def sample_flavor_response():
    """Sample flavor API response."""
    return {
        "id": "m1.test",
        "name": "Test Flavor",
        "vcpus": 2,
        "ram_mb": 4096,
        "disk_gb": 40,
        "ephemeral_gb": 0,
    }


@pytest.fixture
def sample_ssh_key_response():
    """Sample SSH key API response."""
    return {
        "name": "test-key",
        "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2E... test@host",
        "created_at": "2024-05-14T10:00:00Z",
    }


# ============================================================================
# Error Response Fixtures
# ============================================================================


@pytest.fixture
def error_vm_not_found():
    """Sample 404 error response for VM not found."""
    return {
        "success": False,
        "error": {
            "code": "NOT_FOUND",
            "message": "VM not found: nonexistent-vm",
            "status_code": 404,
        },
    }


@pytest.fixture
def error_validation_error():
    """Sample 400 validation error response."""
    return {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Validation error: missing required fields",
            "status_code": 400,
        },
    }


@pytest.fixture
def error_internal_error():
    """Sample 500 internal error response."""
    return {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Internal server error",
            "status_code": 500,
        },
    }


# ============================================================================
# Pagination Fixtures
# ============================================================================


@pytest.fixture
def sample_paginated_response():
    """Sample paginated API response."""
    return {
        "success": True,
        "data": [
            {"id": "item-1", "name": "Item 1"},
            {"id": "item-2", "name": "Item 2"},
        ],
        "meta": {"limit": 10, "offset": 0, "total": 2},
    }


# ============================================================================
# Domain Model Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def domain_vm():
    """Sample VM domain model."""
    return VM(
        id="vm-model-001",
        name="test-vm",
        status=VMStatus.ACTIVE,
        image_id="img-001",
        flavor_id="m1.small",
        network_ids=["net-public"],
        attached_volumes=[],
        key_name="test-key",
        security_groups=["default"],
        metadata={},
        created_at="2024-05-14T10:00:00Z",
        updated_at="2024-05-14T10:00:00Z",
    )


@pytest_asyncio.fixture
async def domain_network():
    """Sample network domain model."""
    return Network(
        id="net-model-001",
        name="test-network",
        status=NetworkStatus.ACTIVE,
        external=False,
        shared=False,
        subnets=["subnet-test"],
        created_at="2024-05-14T10:00:00Z",
        updated_at="2024-05-14T10:00:00Z",
    )


@pytest_asyncio.fixture
async def domain_image():
    """Sample image domain model."""
    return Image(
        id="img-model-001",
        name="Test Image",
        description="Test image",
        disk_format="qcow2",
        container_format="bare",
        size=2147483648,
        visibility="public",
        status="active",
        created_at="2024-05-14T10:00:00Z",
        updated_at="2024-05-14T10:00:00Z",
    )


@pytest_asyncio.fixture
async def domain_flavor():
    """Sample flavor domain model."""
    return Flavor(
        id="m1.model",
        name="Test Flavor",
        vcpus=2,
        ram_mb=4096,
        disk_gb=40,
        ephemeral_gb=0,
    )


@pytest_asyncio.fixture
async def domain_ssh_key():
    """Sample SSH key domain model."""
    return SSHKey(
        name="test-key",
        fingerprint="aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
        public_key="ssh-rsa AAAAB3NzaC1yc2E... test@host",
        created_at="2024-05-14T10:00:00Z",
    )


# ============================================================================
# Helper Functions
# ============================================================================


def create_vm_dict(
    name="test-vm",
    image_id="img-001",
    flavor_id="m1.small",
    network_ids=None,
    key_name=None,
    security_groups=None,
    metadata=None,
):
    """Helper to create VM dictionaries with custom values."""
    return {
        "name": name,
        "image_id": image_id,
        "flavor_id": flavor_id,
        "network_ids": network_ids or ["net-public"],
        "key_name": key_name,
        "security_groups": security_groups or ["default"],
        "metadata": metadata or {},
    }


def create_vm_response(
    vm_id="vm-001",
    name="test-vm",
    status="ACTIVE",
    image_id="img-001",
    flavor_id="m1.small",
    **kwargs
):
    """Helper to create VM API response dictionaries."""
    response = {
        "id": vm_id,
        "name": name,
        "status": status,
        "image_id": image_id,
        "flavor_id": flavor_id,
        "network_ids": kwargs.get("network_ids", ["net-public"]),
        "attached_volumes": kwargs.get("attached_volumes", []),
        "key_name": kwargs.get("key_name", None),
        "security_groups": kwargs.get("security_groups", ["default"]),
        "metadata": kwargs.get("metadata", {}),
        "created_at": kwargs.get("created_at", "2024-05-14T10:00:00Z"),
        "updated_at": kwargs.get("updated_at", "2024-05-14T10:00:00Z"),
    }
    return response


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (deselect with '-m \"not asyncio\"')"
    )
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")


# ============================================================================
# Test Session Hooks
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """Automatically mark async tests."""
    for item in items:
        if "asyncio" in item.keywords:
            item.add_marker(pytest.mark.asyncio)
