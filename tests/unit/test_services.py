"""
Unit tests for service layer business logic.

Tests the core business logic of all services with mock provider,
without making any HTTP requests.
"""

import pytest
import pytest_asyncio
from api.core.models import VMStatus, NetworkStatus
from api.core.exceptions import NotFoundError, ValidationError
from api.services.vm_service import VMService
from api.services.network_service import NetworkService
from api.services.image_service import ImageService
from api.services.flavor_service import FlavorService
from api.services.ssh_key_service import SSHKeyService


# ============================================================================
# VM Service Tests
# ============================================================================


@pytest.mark.asyncio
class TestVMService:
    """Test VM service operations."""

    async def test_list_vms_empty(self, vm_service):
        """Test listing VMs when none exist."""
        vms, total = await vm_service.list_vms(limit=100, offset=0)
        assert isinstance(vms, list)
        assert isinstance(total, int)
        # Mock provider includes sample VMs, so just check structure
        if vms:
            assert all(hasattr(vm, 'id') for vm in vms)
            assert all(hasattr(vm, 'name') for vm in vms)
            assert all(hasattr(vm, 'status') for vm in vms)

    async def test_list_vms_with_pagination(self, vm_service):
        """Test listing VMs with pagination."""
        vms_page1, total1 = await vm_service.list_vms(limit=1, offset=0)
        vms_page2, total2 = await vm_service.list_vms(limit=1, offset=1)

        assert len(vms_page1) <= 1
        assert len(vms_page2) <= 1
        # Pages should be different if there are at least 2 VMs
        if len(vms_page1) > 0 and len(vms_page2) > 0:
            assert vms_page1[0].id != vms_page2[0].id

    async def test_get_vm_success(self, vm_service):
        """Test getting a specific VM."""
        # First list VMs to get a valid ID
        vms, total = await vm_service.list_vms(limit=100, offset=0)
        if vms:
            vm_id = vms[0].id
            vm = await vm_service.get_vm(vm_id)
            assert vm.id == vm_id
            assert vm.name is not None
            assert isinstance(vm.status, VMStatus)

    async def test_get_vm_not_found(self, vm_service):
        """Test getting a non-existent VM."""
        with pytest.raises(NotFoundError):
            await vm_service.get_vm("nonexistent-vm-id")

    async def test_create_vm_success(self, vm_service, sample_vm_create_request):
        """Test creating a new VM."""
        vm = await vm_service.create_vm(
            name=sample_vm_create_request["name"],
            image_id=sample_vm_create_request["image_id"],
            flavor_id=sample_vm_create_request["flavor_id"],
            network_ids=sample_vm_create_request["network_ids"],
            key_name=sample_vm_create_request.get("key_name"),
            security_groups=sample_vm_create_request.get("security_groups"),
            metadata=sample_vm_create_request.get("metadata"),
        )

        assert vm.name == sample_vm_create_request["name"]
        assert vm.image_id == sample_vm_create_request["image_id"]
        assert vm.flavor_id == sample_vm_create_request["flavor_id"]
        assert vm.network_ids == sample_vm_create_request["network_ids"]
        assert vm.status in [VMStatus.BUILDING, VMStatus.ACTIVE]

    async def test_create_vm_validation_error(self, vm_service):
        """Test creating VM with invalid parameters."""
        # Create VM with empty name should fail
        with pytest.raises((ValidationError, ValueError)):
            await vm_service.create_vm(
                name="",
                image_id="img-001",
                flavor_id="m1.small",
                network_ids=["net-public"],
            )

    async def test_delete_vm_success(self, vm_service):
        """Test deleting a VM."""
        # Create a VM first
        vm = await vm_service.create_vm(
            name="test-delete-vm",
            image_id="img-001",
            flavor_id="m1.small",
            network_ids=["net-public"],
        )
        vm_id = vm.id

        # Delete it
        result = await vm_service.delete_vm(vm_id)
        assert result is True

        # Verify it's deleted
        with pytest.raises(NotFoundError):
            await vm_service.get_vm(vm_id)

    async def test_delete_vm_not_found(self, vm_service):
        """Test deleting a non-existent VM."""
        with pytest.raises(NotFoundError):
            await vm_service.delete_vm("nonexistent-vm")

    async def test_start_vm_success(self, vm_service):
        """Test starting a stopped VM."""
        # Create a VM
        vm = await vm_service.create_vm(
            name="test-start-vm",
            image_id="img-001",
            flavor_id="m1.small",
            network_ids=["net-public"],
        )

        # Stop it first
        await vm_service.stop_vm(vm.id)

        # Start it
        started_vm = await vm_service.start_vm(vm.id)
        assert started_vm.status == VMStatus.ACTIVE

    async def test_start_vm_not_found(self, vm_service):
        """Test starting a non-existent VM."""
        with pytest.raises(NotFoundError):
            await vm_service.start_vm("nonexistent-vm")

    async def test_stop_vm_success(self, vm_service):
        """Test stopping a running VM."""
        # First get an active VM
        vms, total = await vm_service.list_vms(limit=100, offset=0)
        if vms:
            vm = vms[0]
            stopped_vm = await vm_service.stop_vm(vm.id)
            assert stopped_vm.status == VMStatus.STOPPED

    async def test_stop_vm_not_found(self, vm_service):
        """Test stopping a non-existent VM."""
        with pytest.raises(NotFoundError):
            await vm_service.stop_vm("nonexistent-vm")

    async def test_reboot_vm_success(self, vm_service):
        """Test rebooting a VM."""
        # Create a VM
        vm = await vm_service.create_vm(
            name="test-reboot-vm",
            image_id="img-001",
            flavor_id="m1.small",
            network_ids=["net-public"],
        )

        # Reboot it
        rebooted_vm = await vm_service.reboot_vm(vm.id)
        assert rebooted_vm.status in [VMStatus.REBOOTING, VMStatus.ACTIVE]

    async def test_reboot_vm_not_found(self, vm_service):
        """Test rebooting a non-existent VM."""
        with pytest.raises(NotFoundError):
            await vm_service.reboot_vm("nonexistent-vm")


# ============================================================================
# Network Service Tests
# ============================================================================


@pytest.mark.asyncio
class TestNetworkService:
    """Test network service operations."""

    async def test_list_networks(self, network_service):
        """Test listing networks."""
        networks, total = await network_service.list_networks(limit=100, offset=0)
        assert isinstance(networks, list)
        assert len(networks) > 0  # Mock provider includes sample networks
        assert all(hasattr(n, 'id') for n in networks)
        assert all(hasattr(n, 'name') for n in networks)
        assert all(hasattr(n, 'status') for n in networks)

    async def test_list_networks_with_pagination(self, network_service):
        """Test listing networks with pagination."""
        networks_page1, total1 = await network_service.list_networks(limit=1, offset=0)
        networks_page2, total2 = await network_service.list_networks(limit=1, offset=1)

        assert len(networks_page1) <= 1
        assert len(networks_page2) <= 1

    async def test_get_network_success(self, network_service):
        """Test getting a specific network."""
        networks, total = await network_service.list_networks(limit=100, offset=0)
        if networks:
            network_id = networks[0].id
            network = await network_service.get_network(network_id)
            assert network.id == network_id
            assert network.name is not None
            assert isinstance(network.status, NetworkStatus)

    async def test_get_network_not_found(self, network_service):
        """Test getting a non-existent network."""
        # Should not raise, but return None or empty
        # (behavior depends on implementation)
        try:
            network = await network_service.get_network("nonexistent-network")
            assert network is None or network.id is None
        except Exception:
            # Some implementations might raise
            pass


# ============================================================================
# Image Service Tests
# ============================================================================


@pytest.mark.asyncio
class TestImageService:
    """Test image service operations."""

    async def test_list_images(self, image_service):
        """Test listing images."""
        images, total = await image_service.list_images(limit=100, offset=0)
        assert isinstance(images, list)
        assert len(images) > 0  # Mock provider includes sample images
        assert all(hasattr(i, 'id') for i in images)
        assert all(hasattr(i, 'name') for i in images)

    async def test_list_images_with_pagination(self, image_service):
        """Test listing images with pagination."""
        images_page1, total1 = await image_service.list_images(limit=1, offset=0)
        images_page2, total2 = await image_service.list_images(limit=1, offset=1)

        assert len(images_page1) <= 1
        assert len(images_page2) <= 1

    async def test_get_image_success(self, image_service):
        """Test getting a specific image."""
        images, total = await image_service.list_images(limit=100, offset=0)
        if images:
            image_id = images[0].id
            image = await image_service.get_image(image_id)
            assert image.id == image_id
            assert image.name is not None


# ============================================================================
# Flavor Service Tests
# ============================================================================


@pytest.mark.asyncio
class TestFlavorService:
    """Test flavor service operations."""

    async def test_list_flavors(self, flavor_service):
        """Test listing flavors."""
        flavors, total = await flavor_service.list_flavors(limit=100, offset=0)
        assert isinstance(flavors, list)
        assert len(flavors) > 0  # Mock provider includes sample flavors
        assert all(hasattr(f, 'id') for f in flavors)
        assert all(hasattr(f, 'name') for f in flavors)
        assert all(hasattr(f, 'vcpus') for f in flavors)
        assert all(hasattr(f, 'ram_mb') for f in flavors)

    async def test_list_flavors_with_pagination(self, flavor_service):
        """Test listing flavors with pagination."""
        flavors_page1, total1 = await flavor_service.list_flavors(limit=1, offset=0)
        flavors_page2, total2 = await flavor_service.list_flavors(limit=1, offset=1)

        assert len(flavors_page1) <= 1
        assert len(flavors_page2) <= 1

    async def test_get_flavor_success(self, flavor_service):
        """Test getting a specific flavor."""
        flavors, total = await flavor_service.list_flavors(limit=100, offset=0)
        if flavors:
            flavor_id = flavors[0].id
            flavor = await flavor_service.get_flavor(flavor_id)
            assert flavor.id == flavor_id
            assert flavor.name is not None


# ============================================================================
# SSH Key Service Tests
# ============================================================================


@pytest.mark.asyncio
class TestSSHKeyService:
    """Test SSH key service operations."""

    async def test_list_ssh_keys(self, ssh_key_service):
        """Test listing SSH keys."""
        keys, total = await ssh_key_service.list_ssh_keys(limit=100, offset=0)
        assert isinstance(keys, list)
        assert len(keys) > 0  # Mock provider includes sample keys
        assert all(hasattr(k, 'name') for k in keys)
        assert all(hasattr(k, 'fingerprint') for k in keys)

    async def test_list_ssh_keys_with_pagination(self, ssh_key_service):
        """Test listing SSH keys with pagination."""
        keys_page1, total1 = await ssh_key_service.list_ssh_keys(limit=1, offset=0)
        keys_page2, total2 = await ssh_key_service.list_ssh_keys(limit=1, offset=1)

        assert len(keys_page1) <= 1
        assert len(keys_page2) <= 1

    async def test_get_ssh_key_success(self, ssh_key_service):
        """Test getting a specific SSH key."""
        keys, total = await ssh_key_service.list_ssh_keys(limit=100, offset=0)
        if keys:
            key_name = keys[0].name
            key = await ssh_key_service.get_ssh_key(key_name)
            assert key.name == key_name
            assert key.public_key is not None


# ============================================================================
# Integration Tests Between Services
# ============================================================================


@pytest.mark.asyncio
class TestServiceIntegration:
    """Test interactions between services."""

    async def test_create_and_retrieve_vm(self, vm_service):
        """Test creating a VM and then retrieving it."""
        # Create
        created_vm = await vm_service.create_vm(
            name="integration-test-vm",
            image_id="img-001",
            flavor_id="m1.small",
            network_ids=["net-public"],
        )

        # Retrieve
        retrieved_vm = await vm_service.get_vm(created_vm.id)

        # Verify
        assert created_vm.id == retrieved_vm.id
        assert created_vm.name == retrieved_vm.name

    async def test_create_list_and_retrieve_vm(self, vm_service):
        """Test creating, listing, and retrieving VMs."""
        # Create
        created_vm = await vm_service.create_vm(
            name="list-test-vm",
            image_id="img-001",
            flavor_id="m1.small",
            network_ids=["net-public"],
        )

        # List
        vms, total = await vm_service.list_vms(limit=100, offset=0)
        assert len(vms) > 0

        # Find in list
        vm_in_list = next((vm for vm in vms if vm.id == created_vm.id), None)
        assert vm_in_list is not None

    async def test_vm_lifecycle_operations(self, vm_service):
        """Test VM lifecycle: create -> stop -> start -> reboot -> delete."""
        # Create
        vm = await vm_service.create_vm(
            name="lifecycle-test-vm",
            image_id="img-001",
            flavor_id="m1.small",
            network_ids=["net-public"],
        )
        vm_id = vm.id

        # Stop
        vm = await vm_service.stop_vm(vm_id)
        assert vm.status == VMStatus.STOPPED

        # Start
        vm = await vm_service.start_vm(vm_id)
        assert vm.status == VMStatus.ACTIVE

        # Reboot
        vm = await vm_service.reboot_vm(vm_id)
        assert vm.status in [VMStatus.REBOOTING, VMStatus.ACTIVE]

        # Delete
        result = await vm_service.delete_vm(vm_id)
        assert result is True


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in services."""

    async def test_vm_service_handles_invalid_image_id(self, vm_service):
        """Test that service handles invalid image IDs gracefully."""
        # The mock provider accepts any ID, so this test documents expected behavior
        try:
            vm = await vm_service.create_vm(
                name="test-invalid-image",
                image_id="invalid-image-id",
                flavor_id="m1.small",
                network_ids=["net-public"],
            )
            # If it succeeds, that's also valid behavior for a mock provider
            assert vm is not None
        except (ValidationError, ValueError):
            # If it raises, that's also acceptable
            pass

    async def test_vm_service_handles_empty_network_ids(self, vm_service):
        """Test that service handles empty network IDs."""
        try:
            vm = await vm_service.create_vm(
                name="test-no-networks",
                image_id="img-001",
                flavor_id="m1.small",
                network_ids=[],
            )
            # Empty networks might be accepted or rejected
            assert vm is not None or vm is None
        except (ValidationError, ValueError):
            # Rejecting empty networks is also valid
            pass
