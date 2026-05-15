# API Examples

Complete examples for all OpenStack VM Orchestrator endpoints. All examples use the mock cloud provider for consistency.

## Table of Contents

- [Base URL & Authentication](#base-url--authentication)
- [VMs](#vms)
- [Images](#images)
- [Flavors](#flavors)
- [SSH Keys](#ssh-keys)
- [Networks](#networks)
- [Common Patterns](#common-patterns)
- [Error Handling](#error-handling)

---

## Base URL & Authentication

**Base URL:** `http://localhost:8000`

**Authentication:** Currently no authentication required (suitable for internal use)

**Default Cloud:** Uses `MOCK` provider (set `OS_CLOUD=ovh` for real OpenStack)

---

## VMs

### List VMs

**Endpoint:** `GET /vms`

**Query Parameters:**
- `limit` (default: 100) - Maximum number of results
- `offset` (default: 0) - Pagination offset
- `cloud` (default: mock) - Cloud provider to use

**Request:**

```bash
curl http://localhost:8000/vms
```

**With Pagination:**

```bash
curl "http://localhost:8000/vms?limit=10&offset=0"
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "id": "vm-001",
      "name": "web-server-01",
      "status": "ACTIVE",
      "image_id": "img-001",
      "flavor_id": "m1.small",
      "network_ids": ["net-public"],
      "attached_volumes": [],
      "key_name": "my-key",
      "security_groups": ["default"],
      "metadata": {},
      "created_at": "2024-05-14T10:30:00Z",
      "updated_at": "2024-05-14T10:30:00Z"
    },
    {
      "id": "vm-002",
      "name": "web-server-02",
      "status": "ACTIVE",
      "image_id": "img-001",
      "flavor_id": "m1.medium",
      "network_ids": ["net-public", "net-private"],
      "attached_volumes": ["vol-001"],
      "key_name": "my-key",
      "security_groups": ["default", "web"],
      "metadata": {"environment": "production"},
      "created_at": "2024-05-14T11:00:00Z",
      "updated_at": "2024-05-14T11:15:00Z"
    }
  ],
  "message": null
}
```

### Get VM Details

**Endpoint:** `GET /vms/{vm_id}`

**Request:**

```bash
curl http://localhost:8000/vms/vm-001
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "vm-001",
    "name": "web-server-01",
    "status": "ACTIVE",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"],
    "attached_volumes": [],
    "key_name": "my-key",
    "security_groups": ["default"],
    "metadata": {},
    "created_at": "2024-05-14T10:30:00Z",
    "updated_at": "2024-05-14T10:30:00Z"
  },
  "message": null
}
```

### Create VM

**Endpoint:** `POST /vms`

**Request Body:**

```bash
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-new-server",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"],
    "key_name": "my-key",
    "security_groups": ["default"],
    "metadata": {"env": "dev"}
  }'
```

**Required Fields:**
- `name` - VM name
- `image_id` - Image ID to use
- `flavor_id` - Flavor ID (VM size)
- `network_ids` - List of network IDs to attach

**Optional Fields:**
- `key_name` - SSH key name
- `security_groups` - Security group names
- `metadata` - Custom metadata

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "vm-003",
    "name": "my-new-server",
    "status": "BUILDING",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"],
    "attached_volumes": [],
    "key_name": "my-key",
    "security_groups": ["default"],
    "metadata": {"env": "dev"},
    "created_at": "2024-05-14T12:00:00Z",
    "updated_at": "2024-05-14T12:00:00Z"
  },
  "message": "VM created successfully"
}
```

### Start VM

**Endpoint:** `POST /vms/{vm_id}/action`

**Request:**

```bash
curl -X POST http://localhost:8000/vms/vm-001/action \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

**Valid Actions:**
- `start` - Start a stopped VM
- `stop` - Stop a running VM
- `reboot` - Reboot a VM (force reboot)

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "vm-001",
    "name": "web-server-01",
    "status": "ACTIVE",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"],
    "attached_volumes": [],
    "key_name": "my-key",
    "security_groups": ["default"],
    "metadata": {},
    "created_at": "2024-05-14T10:30:00Z",
    "updated_at": "2024-05-14T12:10:00Z"
  },
  "message": "VM started successfully"
}
```

### Stop VM

**Endpoint:** `POST /vms/{vm_id}/action`

**Request:**

```bash
curl -X POST http://localhost:8000/vms/vm-001/action \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "vm-001",
    "name": "web-server-01",
    "status": "STOPPED",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"],
    "attached_volumes": [],
    "key_name": "my-key",
    "security_groups": ["default"],
    "metadata": {},
    "created_at": "2024-05-14T10:30:00Z",
    "updated_at": "2024-05-14T12:15:00Z"
  },
  "message": "VM stopped successfully"
}
```

### Reboot VM

**Endpoint:** `POST /vms/{vm_id}/action`

**Request:**

```bash
curl -X POST http://localhost:8000/vms/vm-001/action \
  -H "Content-Type: application/json" \
  -d '{"action": "reboot"}'
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "vm-001",
    "name": "web-server-01",
    "status": "REBOOTING",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"],
    "attached_volumes": [],
    "key_name": "my-key",
    "security_groups": ["default"],
    "metadata": {},
    "created_at": "2024-05-14T10:30:00Z",
    "updated_at": "2024-05-14T12:20:00Z"
  },
  "message": "VM reboot initiated"
}
```

### Delete VM

**Endpoint:** `DELETE /vms/{vm_id}`

**Request:**

```bash
curl -X DELETE http://localhost:8000/vms/vm-001
```

**Response (204 No Content):**

```
(empty response body)
```

---

## Images

### List Images

**Endpoint:** `GET /images`

**Request:**

```bash
curl http://localhost:8000/images
```

**With Pagination:**

```bash
curl "http://localhost:8000/images?limit=10&offset=0"
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "id": "img-001",
      "name": "Ubuntu 22.04 LTS",
      "description": "Ubuntu 22.04 LTS x86_64",
      "disk_format": "qcow2",
      "container_format": "bare",
      "size": 2147483648,
      "visibility": "public",
      "status": "active",
      "created_at": "2024-01-15T08:00:00Z",
      "updated_at": "2024-01-15T08:00:00Z"
    },
    {
      "id": "img-002",
      "name": "Debian 12 Bookworm",
      "description": "Debian 12 Bookworm x86_64",
      "disk_format": "qcow2",
      "container_format": "bare",
      "size": 1073741824,
      "visibility": "public",
      "status": "active",
      "created_at": "2024-01-20T10:00:00Z",
      "updated_at": "2024-01-20T10:00:00Z"
    }
  ],
  "message": null
}
```

### Get Image Details

**Endpoint:** `GET /images/{image_id}`

**Request:**

```bash
curl http://localhost:8000/images/img-001
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "img-001",
    "name": "Ubuntu 22.04 LTS",
    "description": "Ubuntu 22.04 LTS x86_64",
    "disk_format": "qcow2",
    "container_format": "bare",
    "size": 2147483648,
    "visibility": "public",
    "status": "active",
    "created_at": "2024-01-15T08:00:00Z",
    "updated_at": "2024-01-15T08:00:00Z"
  },
  "message": null
}
```

---

## Flavors

### List Flavors

**Endpoint:** `GET /flavors`

**Request:**

```bash
curl http://localhost:8000/flavors
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "id": "m1.small",
      "name": "Small",
      "vcpus": 1,
      "ram_mb": 2048,
      "disk_gb": 20,
      "ephemeral_gb": 0
    },
    {
      "id": "m1.medium",
      "name": "Medium",
      "vcpus": 2,
      "ram_mb": 4096,
      "disk_gb": 40,
      "ephemeral_gb": 0
    },
    {
      "id": "m1.large",
      "name": "Large",
      "vcpus": 4,
      "ram_mb": 8192,
      "disk_gb": 80,
      "ephemeral_gb": 0
    }
  ],
  "message": null
}
```

### Get Flavor Details

**Endpoint:** `GET /flavors/{flavor_id}`

**Request:**

```bash
curl http://localhost:8000/flavors/m1.small
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "m1.small",
    "name": "Small",
    "vcpus": 1,
    "ram_mb": 2048,
    "disk_gb": 20,
    "ephemeral_gb": 0
  },
  "message": null
}
```

---

## SSH Keys

### List SSH Keys

**Endpoint:** `GET /ssh-keys`

**Request:**

```bash
curl http://localhost:8000/ssh-keys
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "name": "my-key",
      "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
      "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDH... user@host",
      "created_at": "2024-03-01T14:00:00Z"
    },
    {
      "name": "backup-key",
      "fingerprint": "99:88:77:66:55:44:33:22:11:00:ff:ee:dd:cc:bb:aa",
      "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQCR... backup@host",
      "created_at": "2024-03-05T09:00:00Z"
    }
  ],
  "message": null
}
```

### Get SSH Key Details

**Endpoint:** `GET /ssh-keys/{key_name}`

**Request:**

```bash
curl http://localhost:8000/ssh-keys/my-key
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "name": "my-key",
    "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
    "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDH... user@host",
    "created_at": "2024-03-01T14:00:00Z"
  },
  "message": null
}
```

---

## Networks

### List Networks

**Endpoint:** `GET /networks`

**Request:**

```bash
curl http://localhost:8000/networks
```

**With Pagination:**

```bash
curl "http://localhost:8000/networks?limit=5&offset=0"
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "id": "net-public",
      "name": "public",
      "status": "ACTIVE",
      "external": true,
      "shared": true,
      "subnets": ["subnet-public"],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "net-private",
      "name": "private",
      "status": "ACTIVE",
      "external": false,
      "shared": false,
      "subnets": ["subnet-private"],
      "created_at": "2024-02-15T10:00:00Z",
      "updated_at": "2024-02-15T10:00:00Z"
    },
    {
      "id": "net-internal",
      "name": "internal",
      "status": "DOWN",
      "external": false,
      "shared": true,
      "subnets": ["subnet-internal"],
      "created_at": "2024-03-01T08:00:00Z",
      "updated_at": "2024-05-10T12:00:00Z"
    }
  ],
  "message": null
}
```

### Get Network Details

**Endpoint:** `GET /networks/{network_id}`

**Request:**

```bash
curl http://localhost:8000/networks/net-public
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "net-public",
    "name": "public",
    "status": "ACTIVE",
    "external": true,
    "shared": true,
    "subnets": ["subnet-public"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": null
}
```

---

## Common Patterns

### Using Cloud Parameter

All endpoints support switching between cloud providers:

```bash
# Use mock provider (default)
curl http://localhost:8000/vms?cloud=mock

# Use OVH OpenStack (requires OS_CLOUD=ovh setup)
curl http://localhost:8000/vms?cloud=ovh
```

### Pagination

All list endpoints support pagination:

```bash
# First page
curl "http://localhost:8000/vms?limit=10&offset=0"

# Second page
curl "http://localhost:8000/vms?limit=10&offset=10"

# All results (careful with large datasets)
curl "http://localhost:8000/vms?limit=1000&offset=0"
```

### Pretty-Print JSON

```bash
# Using jq (install: brew install jq)
curl http://localhost:8000/vms | jq .

# Using Python
curl http://localhost:8000/vms | python -m json.tool
```

### Save Response to File

```bash
curl http://localhost:8000/vms > vms.json
```

### Check Response Headers

```bash
curl -i http://localhost:8000/vms
```

---

## Error Handling

### 404 Not Found

**Request:**

```bash
curl http://localhost:8000/vms/nonexistent-vm
```

**Response (404 Not Found):**

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "VM not found: nonexistent-vm",
    "status_code": 404
  }
}
```

### 400 Bad Request

**Request (Invalid VM creation):**

```bash
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{"name": "incomplete-vm"}'
```

**Response (400 Bad Request):**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error: missing required fields",
    "status_code": 400
  }
}
```

### 500 Internal Server Error

**Response (500 Internal Server Error):**

```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Internal server error",
    "status_code": 500
  }
}
```

---

## Testing All Endpoints (Bash Script)

```bash
#!/bin/bash
# test_api.sh - Test all API endpoints

BASE_URL="http://localhost:8000"

echo "🧪 Testing OpenStack VM Orchestrator API"
echo "==========================================="

# VMs
echo -e "\n📦 Testing VMs..."
curl -s "$BASE_URL/vms" | jq .
echo "✅ List VMs: OK"

# Images
echo -e "\n🖼️  Testing Images..."
curl -s "$BASE_URL/images" | jq .
echo "✅ List Images: OK"

# Flavors
echo -e "\n⚙️  Testing Flavors..."
curl -s "$BASE_URL/flavors" | jq .
echo "✅ List Flavors: OK"

# SSH Keys
echo -e "\n🔑 Testing SSH Keys..."
curl -s "$BASE_URL/ssh-keys" | jq .
echo "✅ List SSH Keys: OK"

# Networks
echo -e "\n🌐 Testing Networks..."
curl -s "$BASE_URL/networks" | jq .
echo "✅ List Networks: OK"

echo -e "\n✨ All tests passed!"
```

Save as `test_api.sh`, then run:

```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Interactive Testing with Swagger UI

Open your browser to **http://localhost:8000/docs** for interactive API documentation and testing.

This provides:
- All available endpoints
- Request/response schemas
- "Try it out" button for live testing
- Parameter documentation
- Example responses

---

## Need More Help?

- Check the main [README.md](../README.md)
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions
- Open an issue on GitHub: https://github.com/jafarijason/openstack-ovh-vm-orchestrator/issues
