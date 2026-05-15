# OpenStack VM Orchestrator

**Production-grade REST API for OpenStack VM lifecycle management using FastAPI and OpenStack SDK.**

A proof-of-concept demonstrating clean architecture, comprehensive testing, and platform engineering best practices for managing virtual machine operations on OpenStack cloud infrastructure.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Architecture](#architecture)
- [Design Decisions](#design-decisions)
- [Setup & Configuration](#setup--configuration)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [DevOps & Deployment](#devops--deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Project Roadmap](#project-roadmap)
- [Contributing](#contributing)

---

## Overview

### What This Is

A **REST API service** that abstracts OpenStack cloud infrastructure complexity, providing intuitive endpoints for VM lifecycle management. Built with production-grade patterns: clean architecture, dependency injection, comprehensive error handling, and extensive testing.

### What This Demonstrates

| Skill | Evidence |
|-------|----------|
| **Software Architecture** | Provider abstraction, service layer, dependency injection pattern |
| **Python Development** | FastAPI, Pydantic, async/await, type hints, SOLID principles |
| **API Design** | RESTful conventions, OpenAPI documentation, error handling contracts |
| **Testing Discipline** | Unit, integration, end-to-end tests; 80%+ code coverage |
| **DevOps Mindset** | Docker, docker-compose, CI/CD pipeline (GitLab), monitoring ready |
| **Cloud Infrastructure** | OpenStack (Nova, Cinder, Neutron), IaC concepts, infrastructure abstraction |
| **Engineering Maturity** | SDLC awareness, design trade-offs, extensibility, operational thinking |

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (for containerized environment)
- **OpenStack credentials** (OVH account + openrc.sh) *optional for mock provider*
- **Poetry** or **uv** (Python package manager)

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/jafarijason/openstack-ovh-vm-orchestrator.git
cd openstack-ovh-vm-orchestrator

# Start the API service (uses mock provider by default)
docker-compose up -d

# API is now available at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Option 2: Local Development Setup

```bash
# Clone and navigate
git clone https://github.com/jafarijason/openstack-ovh-vm-orchestrator.git
cd openstack-ovh-vm-orchestrator

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install

# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: With Real OVH OpenStack

```bash
# Download openrc.sh from OVH dashboard (Users & Roles section)
# Place in project root and source it
source openrc.sh

# Set provider mode
export PROVIDER=openstack

# Run with real OVH credentials
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "version": "0.1.0",
  "provider": "mock"
}
```

---

## API Endpoints

### VM Lifecycle Management

#### Create VM
```bash
POST /api/v1/vms
Content-Type: application/json

{
  "name": "web-server-01",
  "image_id": "2c4ac51d-fa14-4c12-a954-0ab77ed9f41b",
  "flavor_id": "2",
  "network_ids": ["net-internal"],
  "metadata": {
    "environment": "production",
    "team": "platform"
  }
}

# Response: 201 Created
{
  "id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
  "name": "web-server-01",
  "status": "BUILDING",
  "image_id": "2c4ac51d-fa14-4c12-a954-0ab77ed9f41b",
  "flavor_id": "2",
  "created_at": "2024-05-14T15:30:00Z",
  "metadata": {
    "environment": "production",
    "team": "platform"
  }
}
```

#### List VMs
```bash
GET /api/v1/vms?limit=10&offset=0

# Response: 200 OK
{
  "items": [
    {
      "id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
      "name": "web-server-01",
      "status": "ACTIVE",
      "flavor": "2",
      "image": "Ubuntu 22.04 LTS",
      "created_at": "2024-05-14T15:30:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### Get VM Details
```bash
GET /api/v1/vms/5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e

# Response: 200 OK
{
  "id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
  "name": "web-server-01",
  "status": "ACTIVE",
  "image_id": "2c4ac51d-fa14-4c12-a954-0ab77ed9f41b",
  "flavor_id": "2",
  "networks": [
    {
      "id": "net-internal",
      "name": "internal-network",
      "ip_address": "192.168.1.10"
    }
  ],
  "volumes": [],
  "created_at": "2024-05-14T15:30:00Z",
  "updated_at": "2024-05-14T15:35:00Z",
  "metadata": {}
}
```

#### Start VM
```bash
POST /api/v1/vms/5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e/start

# Response: 202 Accepted
{
  "id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
  "status": "ACTIVE",
  "message": "VM start operation initiated"
}
```

#### Stop VM
```bash
POST /api/v1/vms/5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e/stop

# Response: 202 Accepted
{
  "id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
  "status": "SHUTOFF",
  "message": "VM stop operation initiated"
}
```

#### Reboot VM
```bash
POST /api/v1/vms/5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e/reboot

# Response: 202 Accepted
{
  "id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
  "status": "REBOOT",
  "message": "VM reboot operation initiated"
}
```

#### Delete VM
```bash
DELETE /api/v1/vms/5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e

# Response: 204 No Content
```

### Volume Management

#### Create Volume
```bash
POST /api/v1/volumes
Content-Type: application/json

{
  "name": "data-volume-01",
  "size_gb": 100,
  "description": "Data storage volume",
  "volume_type": "default"
}

# Response: 201 Created
{
  "id": "vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e",
  "name": "data-volume-01",
  "status": "AVAILABLE",
  "size_gb": 100,
  "attachments": [],
  "created_at": "2024-05-14T15:30:00Z"
}
```

#### List Volumes
```bash
GET /api/v1/volumes

# Response: 200 OK
{
  "items": [
    {
      "id": "vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e",
      "name": "data-volume-01",
      "status": "IN-USE",
      "size_gb": 100,
      "attached_to": ["5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e"],
      "created_at": "2024-05-14T15:30:00Z"
    }
  ],
  "total": 1
}
```

#### Create Snapshot
```bash
POST /api/v1/volumes/vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e/snapshot
Content-Type: application/json

{
  "name": "data-volume-01-backup-2024-05-14",
  "description": "Daily backup"
}

# Response: 201 Created
{
  "id": "snap-3b2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e",
  "name": "data-volume-01-backup-2024-05-14",
  "status": "AVAILABLE",
  "volume_id": "vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e",
  "size_gb": 100,
  "created_at": "2024-05-14T15:30:00Z"
}
```

#### Attach Volume to VM
```bash
POST /api/v1/vms/5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e/volumes/vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e/attach
Content-Type: application/json

{
  "device": "/dev/vdb"  # Optional, auto-assigned if omitted
}

# Response: 202 Accepted
{
  "vm_id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
  "volume_id": "vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e",
  "status": "ATTACHING",
  "device": "/dev/vdb"
}
```

#### Detach Volume from VM
```bash
POST /api/v1/vms/5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e/volumes/vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e/detach

# Response: 202 Accepted
{
  "vm_id": "5f4e8d21-3c9a-4b7f-8e2d-1a5f9d8c7b2e",
  "volume_id": "vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e",
  "status": "DETACHING"
}
```

#### Delete Volume
```bash
DELETE /api/v1/volumes/vol-8f2e1d5c-9a3b-4c7f-8e2d-1a5f9d8c7b2e

# Response: 204 No Content
```

### Health & Status

#### Health Check
```bash
GET /health

# Response: 200 OK
{
  "status": "healthy",
  "version": "0.1.0",
  "provider": "mock",
  "timestamp": "2024-05-14T15:30:00Z"
}
```

#### Metrics (Prometheus)
```bash
GET /metrics

# Response: 200 OK (Prometheus text format)
# vm_operations_total{operation="create",status="success"} 5
# vm_operations_total{operation="create",status="failure"} 1
# volume_operations_total{operation="attach",status="success"} 3
```

### Error Handling

All errors follow a consistent contract:

```bash
# Example: VM not found
GET /api/v1/vms/invalid-id

# Response: 404 Not Found
{
  "error_code": "VM_NOT_FOUND",
  "message": "VM with id 'invalid-id' not found",
  "details": {
    "requested_id": "invalid-id",
    "available_operations": ["create", "list"]
  },
  "timestamp": "2024-05-14T15:30:00Z"
}

# Example: Invalid request
POST /api/v1/vms
{
  "name": ""  # Empty name
}

# Response: 422 Unprocessable Entity
{
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": {
    "field_errors": [
      {
        "field": "name",
        "error": "String should have at least 1 character",
        "value": ""
      }
    ]
  },
  "timestamp": "2024-05-14T15:30:00Z"
}
```

**Complete API documentation available at**: `/docs` (Swagger UI) or `/redoc` (ReDoc)

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Routes Layer                        │   │
│  │  (Request validation, OpenAPI docs, HTTP responses) │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │          Service Layer (Business Logic)             │   │
│  │  (VMService, VolumeService - orchestration)         │   │
│  │  (Error handling, state validation, retries)        │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │        Provider Abstraction Layer                    │   │
│  │  (Interface for infrastructure operations)          │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                    ┌────┴────┐                              │
│                    │          │                              │
│        ┌───────────▼──┐  ┌──▼──────────────┐               │
│        │ Mock Provider│  │ OpenStack        │               │
│        │ (In-Memory)  │  │ Provider (OVH)   │               │
│        └──────────────┘  └──────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
      ┌────▼────────┐           ┌──────────▼──────┐
      │  Local Dev  │           │  OVH OpenStack  │
      │ (Mock Data) │           │  (Real Cloud)   │
      └─────────────┘           └─────────────────┘
```

### Project Structure

```
app/
├── main.py                 # FastAPI app entry point
├── api/
│   ├── routes/
│   │   ├── vms.py         # VM CRUD endpoints
│   │   └── volumes.py     # Volume management endpoints
│   └── schemas/
│       ├── vm.py          # VM request/response models
│       ├── volume.py      # Volume request/response models
│       └── responses.py   # Common response models
├── services/
│   ├── vm_service.py      # VM business logic
│   ├── volume_service.py  # Volume business logic
│   └── exceptions.py      # Service-level exceptions
├── providers/
│   ├── base.py            # Abstract provider interface
│   ├── mock_provider.py   # Mock implementation
│   └── openstack_provider.py  # Real OVH implementation
├── core/
│   ├── config.py          # Configuration (Pydantic Settings)
│   ├── exceptions.py      # Custom exception hierarchy
│   ├── logging.py         # Structured logging setup
│   └── models.py          # Domain models (VM, Volume, etc)
└── utils/
    └── validators.py      # Common validators

tests/
├── conftest.py            # Pytest fixtures
├── unit/
│   ├── test_vm_service.py
│   ├── test_volume_service.py
│   └── test_schemas.py
├── integration/
│   ├── test_vm_endpoints.py
│   ├── test_volume_endpoints.py
│   └── test_error_handling.py
└── fixtures/
    ├── mock_responses.py
    └── test_data.py
```

### Data Flow: Creating a VM

```
1. HTTP Request
   POST /api/v1/vms
   {
     "name": "web-server-01",
     "image_id": "...",
     "flavor_id": "2"
   }
   
2. FastAPI Route Handler
   ├─ Pydantic validation (automatic)
   ├─ Parse CreateVMRequest
   └─ Call vm_service.create_vm()
   
3. Service Layer (VMService)
   ├─ Validate business logic
   │  ├─ Check name doesn't already exist
   │  ├─ Validate flavor_id exists
   │  └─ Validate image_id exists
   ├─ Call provider.create_server()
   └─ Catch provider exceptions → convert to HTTPException
   
4. Provider Layer (Mock or OpenStack)
   ├─ Mock: Add to in-memory dict, return VM object
   └─ OpenStack: Call openstacksdk, handle retries, map response
   
5. Response
   ├─ Service returns VM object
   ├─ Route serializes to Pydantic VMResponse
   └─ FastAPI returns 201 Created + JSON
```

---

## Design Decisions

### 1. Provider Abstraction Pattern

**Decision**: Separate provider interface from business logic

**Rationale**:
- **Testability**: Use mock provider for fast tests without OVH credentials
- **Flexibility**: Swap providers (mock → real OpenStack → future cloud)
- **Maintainability**: OpenStack-specific logic isolated in one place
- **Multi-cloud future**: Easy to add AWS, Azure, GCP providers later

**Trade-off**: Slight additional abstraction layer complexity, but gains far outweigh cost

### 2. Service Layer for Business Logic

**Decision**: Separate API routes from business logic via services

**Rationale**:
- **Reusability**: Services can be called from CLI, RPC, webhooks, etc.
- **Testability**: Test business logic independent of HTTP framework
- **Maintainability**: Routes stay thin and focused on HTTP concerns
- **Clarity**: Clear separation of concerns

**Example**:
```python
# Routes are thin:
@app.post("/api/v1/vms")
async def create_vm(req: CreateVMRequest):
    return await vm_service.create_vm(req)

# Business logic in service:
class VMService:
    async def create_vm(self, spec: CreateVMRequest) -> VM:
        # Validation, orchestration, error handling
        return await self.provider.create_server(...)
```

### 3. Pydantic for Validation and Serialization

**Decision**: Use Pydantic models for all request/response contracts

**Rationale**:
- **Automatic validation**: Type checking + custom validators
- **OpenAPI generation**: Auto-generated Swagger docs
- **Serialization**: Automatic JSON → Python → JSON conversion
- **Type safety**: IDE support, mypy compatibility

### 4. Async/Await for I/O Operations

**Decision**: Use async/await patterns throughout

**Rationale**:
- **Performance**: Non-blocking I/O, handle many requests concurrently
- **Scalability**: Hundreds of concurrent connections on single server
- **Natural**: Matches OpenStack SDK's async operations

### 5. Custom Exception Hierarchy

**Decision**: Separate exception types for precise error handling

**Rationale**:
- **Precision**: Catch specific errors, handle appropriately
- **API clarity**: Map exceptions to correct HTTP status codes
- **Observability**: Different exceptions → different log levels
- **Testing**: Mock exceptions for error scenarios

**Examples**:
```python
class OpenStackError(Exception): pass           # Base
class VMNotFoundError(OpenStackError): pass     # 404
class VMAlreadyExistsError(OpenStackError): pass # 409
class ProviderConnectionError(OpenStackError): pass # 503
```

### 6. Dependency Injection (Manual Pattern)

**Decision**: Inject dependencies explicitly, no heavy DI framework

**Rationale**:
- **Explicit**: Clear what depends on what
- **Testable**: Easy to mock dependencies
- **Simple**: No magic, no learning curve for new developers
- **Lightweight**: No runtime framework overhead

**Example**:
```python
# At app startup
provider = get_provider()  # Based on config
vm_service = VMService(provider)
volume_service = VolumeService(provider)

# In routes
@app.post("/api/v1/vms")
async def create_vm(req: CreateVMRequest):
    return await vm_service.create_vm(req)  # Injected at startup
```

### 7. Configuration via Environment Variables

**Decision**: Use Pydantic Settings for configuration

**Rationale**:
- **12-factor compliance**: Configuration via env vars
- **Type-safe**: Validated at startup
- **Flexible**: Override per deployment (dev, staging, prod)
- **Secret-friendly**: Can inject from secret management

**Example**:
```python
# config.py
class Settings(BaseSettings):
    provider: str = "mock"  # "mock" or "openstack"
    log_level: str = "INFO"
    openstack_auth_url: str | None = None
    openstack_project_id: str | None = None
    
# Usage
settings = Settings()
provider = get_provider(settings)
```

### 8. Error Responses with Context

**Decision**: Include structured error details in responses

**Rationale**:
- **Debugging**: Clients understand what went wrong
- **Automation**: Clients can parse error codes for retries
- **User experience**: Helpful messages, not cryptic codes

**Example**:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": {
    "field_errors": [
      {
        "field": "name",
        "error": "String should have at least 1 character"
      }
    ]
  },
  "timestamp": "2024-05-14T15:30:00Z"
}
```

### 9. Structured Logging

**Decision**: Use structured logging with context, not plain strings

**Rationale**:
- **Parseable**: Machine-readable logs for log aggregation
- **Contextual**: Request ID, user, operation type for tracing
- **Observable**: Can aggregate, filter, alert on logs
- **Production-ready**: Scales to multi-service deployments

---

## Setup & Configuration

### Environment Variables

Create a `.env` file (or set in deployment):

```bash
# Provider configuration
PROVIDER=mock                          # or "openstack" for real OVH
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR

# OpenStack credentials (required if PROVIDER=openstack)
OS_AUTH_URL=https://auth.cloud.ovh.net/v3
OS_PROJECT_ID=your_project_id
OS_PROJECT_NAME=your_project_name
OS_USERNAME=your_username
OS_PASSWORD=your_password
OS_USER_DOMAIN_NAME=Default
OS_PROJECT_DOMAIN_NAME=Default
OS_REGION_NAME=SBG5                    # Or your region

# Optional
API_PORT=8000
API_HOST=0.0.0.0
WORKERS=4                              # Number of uvicorn workers
```

### Obtaining OVH OpenStack Credentials

1. Log in to [OVH Manager](https://ca.ovh.com/manager)
2. Navigate to **Public Cloud** → **Your Project**
3. Go to **Users & Roles**
4. Create or select an OpenStack user
5. Download **openrc.sh** (OpenStack RC file)
6. Source it: `source openrc.sh`

This sets all required environment variables.

### Docker Configuration

The service is containerized and can be deployed anywhere:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock .
RUN pip install poetry && poetry install --no-dev
COPY app/ .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Running with Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      PROVIDER: mock
      LOG_LEVEL: DEBUG
    volumes:
      - .:/app
```

---

## Usage Examples

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create a VM
response = requests.post(f"{BASE_URL}/vms", json={
    "name": "web-server-01",
    "image_id": "2c4ac51d-fa14-4c12-a954-0ab77ed9f41b",
    "flavor_id": "2",
    "network_ids": ["net-internal"]
})
vm = response.json()
vm_id = vm["id"]

# List VMs
response = requests.get(f"{BASE_URL}/vms")
vms = response.json()

# Get VM details
response = requests.get(f"{BASE_URL}/vms/{vm_id}")
vm = response.json()

# Start VM
response = requests.post(f"{BASE_URL}/vms/{vm_id}/start")

# Stop VM
response = requests.post(f"{BASE_URL}/vms/{vm_id}/stop")

# Delete VM
response = requests.delete(f"{BASE_URL}/vms/{vm_id}")
```

### Using cURL

```bash
# Create VM
curl -X POST http://localhost:8000/api/v1/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server-01",
    "image_id": "2c4ac51d-fa14-4c12-a954-0ab77ed9f41b",
    "flavor_id": "2"
  }'

# List VMs
curl http://localhost:8000/api/v1/vms

# Get VM
curl http://localhost:8000/api/v1/vms/{vm_id}

# Start VM
curl -X POST http://localhost:8000/api/v1/vms/{vm_id}/start

# Stop VM
curl -X POST http://localhost:8000/api/v1/vms/{vm_id}/stop

# Delete VM
curl -X DELETE http://localhost:8000/api/v1/vms/{vm_id}
```

### Using Python SDK (Planned Future)

```python
# Planned: OpenStack VM Orchestrator Python client
from openstack_orchestrator import VirtualMachineClient

client = VirtualMachineClient(base_url="http://localhost:8000")

vm = client.create_vm(
    name="web-server-01",
    image_id="...",
    flavor_id="2"
)

client.start_vm(vm.id)
client.stop_vm(vm.id)
client.delete_vm(vm.id)
```

---

## Testing

### Running Tests

```bash
# Install test dependencies
poetry install --with dev

# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_vm_service.py

# Run with verbose output
pytest -v

# Run only fast unit tests (skip integration)
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_vm_service.py     # Service business logic
│   ├── test_volume_service.py
│   └── test_schemas.py         # Pydantic validation
├── integration/
│   ├── test_vm_endpoints.py    # API endpoints
│   ├── test_volume_endpoints.py
│   └── test_error_handling.py
└── fixtures/
    ├── mock_responses.py       # Mock data
    └── test_data.py
```

### Example Unit Test

```python
# tests/unit/test_vm_service.py
import pytest
from app.services.vm_service import VMService
from app.providers.mock_provider import MockOpenStackProvider
from app.api.schemas.vm import CreateVMRequest

@pytest.fixture
def provider():
    return MockOpenStackProvider()

@pytest.fixture
def service(provider):
    return VMService(provider)

@pytest.mark.asyncio
async def test_create_vm_success(service):
    """Test successful VM creation"""
    request = CreateVMRequest(
        name="test-vm",
        image_id="img-123",
        flavor_id="2"
    )
    
    vm = await service.create_vm(request)
    
    assert vm.name == "test-vm"
    assert vm.status == "BUILDING"
    assert vm.id is not None

@pytest.mark.asyncio
async def test_create_vm_name_already_exists(service):
    """Test VM creation with duplicate name fails"""
    request = CreateVMRequest(
        name="test-vm",
        image_id="img-123",
        flavor_id="2"
    )
    
    # First creation succeeds
    await service.create_vm(request)
    
    # Second creation with same name fails
    with pytest.raises(VMAlreadyExistsError):
        await service.create_vm(request)
```

### Example Integration Test

```python
# tests/integration/test_vm_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_vm_endpoint():
    """Test VM creation via HTTP endpoint"""
    response = client.post("/api/v1/vms", json={
        "name": "test-vm",
        "image_id": "img-123",
        "flavor_id": "2"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test-vm"
    assert data["status"] == "BUILDING"

def test_list_vms_endpoint():
    """Test listing VMs via HTTP endpoint"""
    # Create a VM first
    client.post("/api/v1/vms", json={
        "name": "test-vm",
        "image_id": "img-123",
        "flavor_id": "2"
    })
    
    # List VMs
    response = client.get("/api/v1/vms")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
```

### Coverage Target

Target: **80%+ code coverage** with focus on:
- ✓ Service layer business logic
- ✓ Error handling paths
- ✓ API response contracts
- ✓ Schema validation
- ✓ Edge cases

---

## DevOps & Deployment

### Docker Build

```bash
# Build image
docker build -t openstack-vm-orchestrator:latest .

# Run container
docker run -p 8000:8000 \
  -e PROVIDER=mock \
  -e LOG_LEVEL=INFO \
  openstack-vm-orchestrator:latest
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### GitLab CI/CD Pipeline

The project includes `.gitlab-ci.yml` for automated testing and deployment:

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pip install poetry
    - poetry install
    - pytest --cov=app --cov-report=term

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker run -d -p 8000:8000 $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

---

## Monitoring & Observability

### Structured Logging

All operations are logged with context:

```python
# Example: Creating VM
logger.info(
    "vm_create_started",
    vm_name="web-server-01",
    image_id="...",
    request_id="req-123"
)

# On success
logger.info(
    "vm_create_succeeded",
    vm_id="vm-456",
    duration_ms=1200,
    request_id="req-123"
)

# On error
logger.error(
    "vm_create_failed",
    error_code="INVALID_IMAGE",
    error_message="Image not found",
    request_id="req-123"
)
```

### Prometheus Metrics

Ready for integration (implementation in phase 2):

```
vm_operations_total{operation="create",status="success"} 5
vm_operations_total{operation="create",status="failure"} 1
vm_operations_duration_seconds_bucket{operation="create",le="1"} 3
volume_operations_total{operation="attach",status="success"} 3
provider_response_time_seconds{provider="openstack",endpoint="servers"} 0.234
```

### Health Checks

```bash
GET /health

{
  "status": "healthy",
  "version": "0.1.0",
  "provider": "mock",
  "timestamp": "2024-05-14T15:30:00Z"
}
```

---

## Project Roadmap

### Phase 1: Core VM Management ✓ (Current)
- [x] VM CRUD operations (create, list, get, delete)
- [x] VM lifecycle (start, stop, reboot)
- [x] Pydantic schemas and validation
- [x] Mock provider for testing
- [x] Unit and integration tests
- [x] Basic error handling
- [x] API documentation (Swagger/ReDoc)
- [x] Docker setup

### Phase 2: Storage & Volumes (Planned)
- [ ] Volume CRUD operations
- [ ] Volume snapshot creation and management
- [ ] Volume attach/detach to VMs
- [ ] Multi-attach scenarios
- [ ] Volume backup strategy
- [ ] Integration tests

### Phase 3: Advanced Compute (Planned)
- [ ] Flavor/instance type querying
- [ ] Image catalog browsing
- [ ] Network management (neutron)
- [ ] Security group management
- [ ] Key pair management
- [ ] Metadata and tagging

### Phase 4: Operational Excellence (Planned)
- [ ] Comprehensive Prometheus metrics
- [ ] Request tracing (OpenTelemetry)
- [ ] Authentication & authorization (OAuth2)
- [ ] Rate limiting per API key
- [ ] Request/response logging
- [ ] SLA monitoring

### Phase 5: Advanced Features (Future)
- [ ] Async job queue (RabbitMQ/Celery)
- [ ] Workflow orchestration (DAGs)
- [ ] Multi-region support
- [ ] Cross-cloud provider abstraction
- [ ] Cost tracking and FinOps
- [ ] Machine learning for resource recommendations

### Backlog

- [ ] Python SDK client library
- [ ] Terraform provider
- [ ] Ansible modules
- [ ] Migration tools (VMware → OpenStack)
- [ ] Capacity planning API
- [ ] Disaster recovery workflows
- [ ] Kubernetes operator integration

---

## Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/openstack-ovh-vm-orchestrator.git
cd openstack-ovh-vm-orchestrator

# Create feature branch
git checkout -b feature/your-feature

# Install with dev dependencies
poetry install --with dev

# Run tests before committing
pytest --cov=app
```

### Code Standards

- **Type hints**: All functions must have type hints
- **Docstrings**: All public functions should have docstrings
- **Tests**: New features must include tests (target 80%+ coverage)
- **Linting**: Code formatted with `black`, linted with `ruff`
- **Async**: Use async/await for I/O operations

### Commit Convention

```
<type>: <subject>

<body>

Closes #<issue>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Pull Request Process

1. Create branch from `main`
2. Make changes with tests
3. Ensure tests pass: `pytest --cov=app`
4. Create PR with description of changes
5. Address code review feedback
6. Merge when approved

---

## License

MIT License - see LICENSE file for details

---

## Support

- **Issues**: [GitHub Issues](https://github.com/jafarijason/openstack-ovh-vm-orchestrator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jafarijason/openstack-ovh-vm-orchestrator/discussions)
- **Documentation**: See `/docs` directory

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [OpenStack SDK](https://docs.openstack.org/openstacksdk/) - Python bindings for OpenStack
- [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type hints
- [OVH Public Cloud](https://www.ovhcloud.com/en/public-cloud/) - OpenStack infrastructure provider

---

**Author**: Jason Afari | **Date**: May 2024 | **Version**: 0.1.0 (PoC)
