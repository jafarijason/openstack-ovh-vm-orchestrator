"""
Integration tests for VM endpoints.

Tests the complete HTTP API flow including request/response validation,
error handling, and status codes.
"""

import pytest
from fastapi.testclient import TestClient
import json


class TestVMListEndpoint:
    """Test GET /vms endpoint."""

    def test_list_vms_success(self, client):
        """Test listing VMs returns 200 with valid data."""
        response = client.get("/vms")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_list_vms_default_pagination(self, client):
        """Test list VMs uses default pagination."""
        response = client.get("/vms")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)

    def test_list_vms_with_limit(self, client):
        """Test list VMs with custom limit."""
        response = client.get("/vms?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 1

    def test_list_vms_with_offset(self, client):
        """Test list VMs with offset."""
        response1 = client.get("/vms?limit=10&offset=0")
        response2 = client.get("/vms?limit=10&offset=10")

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_list_vms_response_structure(self, client):
        """Test VM list response structure."""
        response = client.get("/vms")
        data = response.json()

        # Check response wrapper
        assert "success" in data
        assert "data" in data

        # Check VM structure if VMs exist
        if data["data"]:
            vm = data["data"][0]
            assert "id" in vm
            assert "name" in vm
            assert "status" in vm
            assert "image_id" in vm
            assert "flavor_id" in vm
            assert "network_ids" in vm
            assert "created_at" in vm
            assert "updated_at" in vm


class TestVMGetEndpoint:
    """Test GET /vms/{vm_id} endpoint."""

    def test_get_vm_success(self, client):
        """Test getting a specific VM returns 200."""
        # First list VMs to get a valid ID
        list_response = client.get("/vms")
        vms = list_response.json()["data"]

        if vms:
            vm_id = vms[0]["id"]
            response = client.get(f"/vms/{vm_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["id"] == vm_id

    def test_get_vm_not_found(self, client):
        """Test getting non-existent VM returns 404."""
        response = client.get("/vms/nonexistent-vm-id")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_get_vm_response_structure(self, client):
        """Test VM get response structure."""
        list_response = client.get("/vms")
        vms = list_response.json()["data"]

        if vms:
            vm_id = vms[0]["id"]
            response = client.get(f"/vms/{vm_id}")
            data = response.json()

            # Check VM has all required fields
            vm = data["data"]
            required_fields = [
                "id",
                "name",
                "status",
                "image_id",
                "flavor_id",
                "network_ids",
                "created_at",
                "updated_at",
            ]
            for field in required_fields:
                assert field in vm, f"Missing field: {field}"


class TestVMCreateEndpoint:
    """Test POST /vms endpoint."""

    def test_create_vm_success(self, client, sample_vm_create_request):
        """Test creating VM returns 201 with VM data."""
        response = client.post("/vms", json=sample_vm_create_request)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["name"] == sample_vm_create_request["name"]

    def test_create_vm_response_contains_id(self, client, sample_vm_create_request):
        """Test created VM has an ID."""
        response = client.post("/vms", json=sample_vm_create_request)

        assert response.status_code == 201
        data = response.json()
        vm = data["data"]
        assert "id" in vm
        assert vm["id"] is not None

    def test_create_vm_with_minimal_fields(self, client):
        """Test creating VM with minimal required fields."""
        request = {
            "name": "minimal-vm",
            "image_id": "img-001",
            "flavor_id": "m1.small",
            "network_ids": ["net-public"],
        }

        response = client.post("/vms", json=request)
        assert response.status_code == 201

    def test_create_vm_missing_required_field(self, client):
        """Test creating VM without required field returns 400."""
        incomplete_request = {
            "name": "incomplete-vm",
            "image_id": "img-001",
            # Missing flavor_id and network_ids
        }

        response = client.post("/vms", json=incomplete_request)
        assert response.status_code == 422  # Unprocessable Entity

    def test_create_vm_with_all_fields(self, client, sample_vm_create_request):
        """Test creating VM with all optional fields."""
        response = client.post("/vms", json=sample_vm_create_request)

        assert response.status_code == 201
        data = response.json()
        vm = data["data"]

        # Verify all sent fields are in response
        assert vm["name"] == sample_vm_create_request["name"]
        assert vm["key_name"] == sample_vm_create_request.get("key_name")


class TestVMDeleteEndpoint:
    """Test DELETE /vms/{vm_id} endpoint."""

    def test_delete_vm_success(self, client, sample_vm_create_request):
        """Test deleting VM returns 204."""
        # Create VM
        create_response = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_response.json()["data"]["id"]

        # Delete VM
        response = client.delete(f"/vms/{vm_id}")

        assert response.status_code == 204

    def test_delete_vm_not_found(self, client):
        """Test deleting non-existent VM returns 404."""
        response = client.delete("/vms/nonexistent-vm")

        assert response.status_code == 404

    def test_delete_vm_then_get_fails(self, client, sample_vm_create_request):
        """Test VM is gone after deletion."""
        # Create VM
        create_response = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_response.json()["data"]["id"]

        # Delete VM
        client.delete(f"/vms/{vm_id}")

        # Try to get deleted VM
        response = client.get(f"/vms/{vm_id}")
        assert response.status_code == 404


class TestVMActionEndpoint:
    """Test POST /vms/{vm_id}/action endpoint."""

    def test_start_vm_success(self, client, sample_vm_create_request):
        """Test starting VM returns 200 with updated VM."""
        # Create VM
        create_response = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_response.json()["data"]["id"]

        # Stop it first
        client.post(f"/vms/{vm_id}/action", json={"action": "stop"})

        # Start it
        response = client.post(f"/vms/{vm_id}/action", json={"action": "start"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "ACTIVE"

    def test_stop_vm_success(self, client, sample_vm_create_request):
        """Test stopping VM returns 200 with STOPPED status."""
        # Create VM
        create_response = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_response.json()["data"]["id"]

        # Stop it
        response = client.post(f"/vms/{vm_id}/action", json={"action": "stop"})

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "STOPPED"

    def test_reboot_vm_success(self, client, sample_vm_create_request):
        """Test rebooting VM returns 200."""
        # Create VM
        create_response = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_response.json()["data"]["id"]

        # Reboot it
        response = client.post(f"/vms/{vm_id}/action", json={"action": "reboot"})

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] in ["REBOOTING", "ACTIVE"]

    def test_action_on_nonexistent_vm(self, client):
        """Test action on non-existent VM returns 404."""
        response = client.post(
            "/vms/nonexistent-vm/action", json={"action": "start"}
        )

        assert response.status_code == 404

    def test_invalid_action(self, client, sample_vm_create_request):
        """Test invalid action returns 400."""
        # Create VM
        create_response = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_response.json()["data"]["id"]

        # Try invalid action
        response = client.post(f"/vms/{vm_id}/action", json={"action": "invalid"})

        assert response.status_code == 400 or response.status_code == 422

    def test_action_missing_action_field(self, client, sample_vm_create_request):
        """Test action without 'action' field returns 422."""
        # Create VM
        create_response = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_response.json()["data"]["id"]

        # Try action without field
        response = client.post(f"/vms/{vm_id}/action", json={})

        assert response.status_code == 422


class TestVMEndpointErrorHandling:
    """Test error handling in VM endpoints."""

    def test_get_with_invalid_format(self, client):
        """Test GET with invalid format."""
        response = client.get("/vms?limit=invalid")
        # Should either use default or return 422
        assert response.status_code in [200, 422]

    def test_create_with_invalid_json(self, client):
        """Test POST with invalid JSON."""
        response = client.post(
            "/vms",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in [400, 422]

    def test_list_large_limit(self, client):
        """Test list with very large limit."""
        response = client.get("/vms?limit=10000")
        assert response.status_code == 200
        data = response.json()
        # Should return all available VMs or error gracefully
        assert isinstance(data["data"], list)


class TestVMEndpointIntegration:
    """Test complete VM workflows."""

    def test_create_list_get_delete_workflow(self, client, sample_vm_create_request):
        """Test complete VM lifecycle through API."""
        # Create
        create_resp = client.post("/vms", json=sample_vm_create_request)
        assert create_resp.status_code == 201
        vm_id = create_resp.json()["data"]["id"]

        # List
        list_resp = client.get("/vms")
        assert list_resp.status_code == 200
        vms = list_resp.json()["data"]
        assert any(vm["id"] == vm_id for vm in vms)

        # Get
        get_resp = client.get(f"/vms/{vm_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["id"] == vm_id

        # Delete
        delete_resp = client.delete(f"/vms/{vm_id}")
        assert delete_resp.status_code == 204

        # Verify deleted
        verify_resp = client.get(f"/vms/{vm_id}")
        assert verify_resp.status_code == 404

    def test_create_and_lifecycle_workflow(self, client, sample_vm_create_request):
        """Test VM creation and lifecycle operations."""
        # Create
        create_resp = client.post("/vms", json=sample_vm_create_request)
        assert create_resp.status_code == 201
        vm_id = create_resp.json()["data"]["id"]

        # Stop
        stop_resp = client.post(f"/vms/{vm_id}/action", json={"action": "stop"})
        assert stop_resp.status_code == 200
        assert stop_resp.json()["data"]["status"] == "STOPPED"

        # Start
        start_resp = client.post(f"/vms/{vm_id}/action", json={"action": "start"})
        assert start_resp.status_code == 200
        assert start_resp.json()["data"]["status"] == "ACTIVE"

        # Reboot
        reboot_resp = client.post(f"/vms/{vm_id}/action", json={"action": "reboot"})
        assert reboot_resp.status_code == 200

        # Cleanup
        client.delete(f"/vms/{vm_id}")


class TestVMEndpointResponseFormats:
    """Test response format consistency."""

    def test_success_response_format(self, client):
        """Test success response has correct format."""
        response = client.get("/vms")
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        # Optional but common
        assert "message" in data or "data" in data

    def test_error_response_format(self, client):
        """Test error response has correct format."""
        response = client.get("/vms/nonexistent-vm")
        data = response.json()

        assert "success" in data
        assert data["success"] is False
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "status_code" in data["error"]

    def test_created_response_status(self, client, sample_vm_create_request):
        """Test 201 response for creation."""
        response = client.post("/vms", json=sample_vm_create_request)

        assert response.status_code == 201
        assert response.json()["success"] is True

    def test_deleted_response_status(self, client, sample_vm_create_request):
        """Test 204 response for deletion."""
        # Create
        create_resp = client.post("/vms", json=sample_vm_create_request)
        vm_id = create_resp.json()["data"]["id"]

        # Delete
        delete_resp = client.delete(f"/vms/{vm_id}")

        assert delete_resp.status_code == 204
        # 204 typically has no body
        if delete_resp.content:
            assert len(delete_resp.content) == 0 or delete_resp.json() == {}
