# Architecture & Design Patterns

This document outlines the architectural decisions, design patterns, and technical rationale behind the OpenStack VM Orchestrator project.

---

## Table of Contents

- [Overview](#overview)
- [Architectural Principles](#architectural-principles)
- [System Design](#system-design)
- [Design Patterns](#design-patterns)
- [Layered Architecture](#layered-architecture)
- [Data Models](#data-models)
- [Error Handling Strategy](#error-handling-strategy)
- [Configuration Management](#configuration-management)
- [Provider Abstraction](#provider-abstraction)
- [Async/Await Patterns](#asyncawait-patterns)
- [Dependency Injection](#dependency-injection)
- [Testing Strategy](#testing-strategy)
- [Monitoring & Observability](#monitoring--observability)
- [Future Extensibility](#future-extensibility)

---

## Overview

The OpenStack VM Orchestrator is designed with **clean architecture** principles, emphasizing:

- **Separation of Concerns**: Clear boundaries between layers
- **Testability**: Easy to test individual components
- **Extensibility**: Simple to add new providers or features
- **Maintainability**: Code is understandable and changeable
- **Scalability**: Non-blocking operations, async throughout

The system abstracts OpenStack infrastructure complexity behind a simple, intuitive REST API.

---

## Architectural Principles

### 1. Single Responsibility Principle (SRP)

Each component has one reason to change:

- **Routes**: Only handle HTTP concerns (request parsing, response formatting)
- **Services**: Only contain business logic (validation, orchestration)
- **Providers**: Only interact with infrastructure (OpenStack SDK calls)
- **Models**: Only represent data structures

**Example**:
```python
# Routes don't do business logic
@app.post("/api/v1/vms")
async def create_vm(req: CreateVMRequest):
    return await vm_service.create_vm(req)  # Delegate to service

# Services don't do HTTP
class VMService:
    async def create_vm(self, spec: CreateVMRequest) -> VM:
        # Validation, orchestration, error handling
        return await self.provider.create_server(...)

# Providers don't do business logic
class OpenStackProvider:
    async def create_server(self, spec: ServerSpec) -> Server:
        # Just call OpenStack SDK
        return self.conn.compute.create_server(...)
```

### 2. Open/Closed Principle (OCP)

Code is open for extension, closed for modification:

- Add new providers without modifying existing code
- Extend services with decorators or middleware
- Add new routes without changing core

**Example**:
```python
# Adding AWS provider doesn't change existing code
class AWSProvider(OpenStackProvider):
    async def create_server(self, spec: ServerSpec) -> Server:
        # AWS-specific implementation
        pass

# Just swap at configuration time
provider = get_provider(settings.PROVIDER)  # "openstack", "aws", "azure", etc.
```

### 3. Dependency Inversion Principle (DIP)

Depend on abstractions, not concrete implementations:

- Services depend on `OpenStackProvider` (abstract), not concrete provider
- Routes depend on services via dependency injection
- Configuration is injected at startup

**Example**:
```python
# Service depends on abstract provider
class VMService:
    def __init__(self, provider: OpenStackProvider):  # Abstract!
        self.provider = provider

# Inject mock for testing
test_service = VMService(MockOpenStackProvider())

# Inject real for production
prod_service = VMService(RealOpenStackProvider())
```

### 4. Interface Segregation Principle (ISP)

Clients should not depend on interfaces they don't use:

- Provider interface is focused on compute operations
- Future storage interface separate from compute
- Networking interface independent

---

## System Design

### Overall Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (HTTP)                            │
│              curl, Python requests, SDKs                    │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   API Routes Layer                                  │   │
│  │   - Request validation (Pydantic)                   │   │
│  │   - Response serialization                          │   │
│  │   - OpenAPI documentation                           │   │
│  │   - HTTP error mapping                              │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │ Dependency Injection              │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │   Service Layer (Business Logic)                    │   │
│  │   - VMService: VM lifecycle orchestration           │   │
│  │   - VolumeService: Storage operations               │   │
│  │   - Validation and error handling                   │   │
│  │   - State management and transitions                │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │ Abstraction                       │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │   Provider Abstraction Layer                        │   │
│  │   - Abstract base interface (OpenStackProvider)     │   │
│  │   - Defines provider contract                       │   │
│  │   - Maps domain models to provider models           │   │
│  └──────────────────────┬───────────────────────────────┘   │
│              ┌──────────┴──────────┐                        │
│              │                     │                        │
│  ┌───────────▼──────────┐  ┌──────▼─────────────────────┐   │
│  │  Mock Provider       │  │  OpenStack Provider        │   │
│  │  - In-memory storage │  │  - Real OpenStack SDK      │   │
│  │  - No dependencies   │  │  - OVH Public Cloud        │   │
│  │  - Perfect for tests │  │  - Production use          │   │
│  └──────────────────────┘  └────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                             │
           ┌─────────────────┴─────────────────┐
           │                                   │
      ┌────▼────────────┐           ┌──────────▼──────┐
      │   Local Dev     │           │  OVH OpenStack  │
      │  (Mock Data)    │           │  (Real Cloud)   │
      └─────────────────┘           └─────────────────┘
```

### Request/Response Flow

```
1. HTTP Request arrives
   POST /api/v1/vms { "name": "web-server-01", ... }
   
2. FastAPI Route Handler
   - Pydantic validates and parses request
   - Creates CreateVMRequest object
   - Calls vm_service.create_vm(request)
   
3. Service Layer (VMService)
   - Validates business rules
   - Checks duplicate names
   - Validates image_id, flavor_id exist
   - Calls provider.create_server(spec)
   - Catches exceptions, converts to HTTP errors
   
4. Provider Layer
   
   Mock Provider:
   ├─ Checks if VM name already exists
   ├─ Generates unique ID
   ├─ Creates in-memory VM object
   └─ Returns VM
   
   OpenStack Provider:
   ├─ Calls openstacksdk
   ├─ Handles retries on network failure
   ├─ Maps OpenStack server to domain Server
   └─ Returns domain Server object
   
5. Service returns VM object
   
6. Route serializes VM to VMResponse (Pydantic)
   
7. FastAPI returns 201 Created + JSON body
```

---

## Design Patterns

### 1. Provider Pattern (Strategy Pattern)

**Purpose**: Decouple business logic from infrastructure specifics

**Implementation**:
```python
# Abstract interface
class OpenStackProvider(ABC):
    @abstractmethod
    async def create_server(self, spec: ServerSpec) -> Server: ...
    @abstractmethod
    async def list_servers(self) -> List[Server]: ...
    # ... etc

# Mock implementation
class MockOpenStackProvider(OpenStackProvider):
    def __init__(self):
        self.servers = {}
    
    async def create_server(self, spec: ServerSpec) -> Server:
        server = Server(id=uuid4(), **spec.dict())
        self.servers[server.id] = server
        return server

# Real implementation
class RealOpenStackProvider(OpenStackProvider):
    def __init__(self, conn):
        self.conn = conn
    
    async def create_server(self, spec: ServerSpec) -> Server:
        os_server = self.conn.compute.create_server(**spec.dict())
        return Server.from_openstack(os_server)
```

**Benefits**:
- ✅ Test with mock, deploy with real
- ✅ Easy to add new providers
- ✅ Business logic doesn't change

### 2. Service Pattern (Facade)

**Purpose**: Provide unified interface to complex subsystems

**Implementation**:
```python
class VMService:
    def __init__(self, provider: OpenStackProvider):
        self.provider = provider
    
    async def create_vm(self, spec: CreateVMRequest) -> VM:
        """Orchestrate VM creation with validation"""
        # 1. Validate
        if await self._vm_exists(spec.name):
            raise VMAlreadyExistsError(spec.name)
        
        # 2. Call provider
        server = await self.provider.create_server(spec)
        
        # 3. Map to domain model
        return VM.from_server(server)
    
    async def _vm_exists(self, name: str) -> bool:
        """Check if VM with name already exists"""
        servers = await self.provider.list_servers()
        return any(s.name == name for s in servers)
```

**Benefits**:
- ✅ Centralized business logic
- ✅ Testable in isolation
- ✅ Consistent error handling

### 3. Dependency Injection Pattern

**Purpose**: Inject dependencies at configuration time

**Implementation**:
```python
# At application startup
def setup_app():
    # Configuration
    settings = Settings()
    
    # Provider based on config
    provider = get_provider(settings)
    
    # Services with injected dependencies
    vm_service = VMService(provider)
    volume_service = VolumeService(provider)
    
    # FastAPI app
    app = FastAPI()
    
    # Routes can access injected services
    @app.post("/api/v1/vms")
    async def create_vm(req: CreateVMRequest):
        return await vm_service.create_vm(req)
    
    return app

def get_provider(settings: Settings) -> OpenStackProvider:
    if settings.provider == "mock":
        return MockOpenStackProvider()
    elif settings.provider == "openstack":
        conn = openstack.connect()  # From env vars
        return RealOpenStackProvider(conn)
```

**Benefits**:
- ✅ Explicit dependencies
- ✅ Easy to test (inject mocks)
- ✅ Flexible configuration

### 4. Data Transfer Object (DTO) Pattern

**Purpose**: Map between domain models and API contracts

**Implementation**:
```python
# Domain model (internal)
class VM:
    id: str
    name: str
    status: VMStatus
    created_at: datetime
    # ... internal fields

# Request DTO (API input)
class CreateVMRequest(BaseModel):
    name: str
    image_id: str
    flavor_id: str

# Response DTO (API output)
class VMResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    
# Route
@app.post("/api/v1/vms")
async def create_vm(req: CreateVMRequest) -> VMResponse:
    vm = await vm_service.create_vm(req)
    return VMResponse(**vm.dict())
```

**Benefits**:
- ✅ API contracts independent of domain models
- ✅ Easy to evolve API without changing internals
- ✅ Clear input/output validation

### 5. Repository Pattern (Implicit)

**Purpose**: Encapsulate data access logic

**Implementation**: Provider layer acts as repository
```python
class OpenStackProvider:
    # "Repository" for VMs
    async def create_server(self, spec) -> Server: ...
    async def list_servers(self) -> List[Server]: ...
    async def get_server(self, id: str) -> Server: ...
    async def delete_server(self, id: str) -> None: ...
    
    # "Repository" for volumes
    async def create_volume(self, spec) -> Volume: ...
    async def list_volumes(self) -> List[Volume]: ...
    # ... etc
```

**Benefits**:
- ✅ Consistent data access interface
- ✅ Easy to mock for testing
- ✅ Encapsulates provider details

---

## Layered Architecture

### Layer 1: API Routes (HTTP Layer)

**Responsibility**: HTTP concerns only

**Contains**:
- Request parsing and validation
- Response serialization
- Error to HTTP status code mapping
- OpenAPI documentation

**Files**:
- `app/api/routes/vms.py`
- `app/api/routes/volumes.py`

**Example**:
```python
@router.post("/vms", status_code=201, response_model=VMResponse)
async def create_vm(req: CreateVMRequest) -> VMResponse:
    """Create a new VM"""
    try:
        vm = await vm_service.create_vm(req)
        return VMResponse(**vm.dict())
    except VMAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ProviderError as e:
        raise HTTPException(status_code=503, detail="Provider error")
```

### Layer 2: Service Layer (Business Logic)

**Responsibility**: Orchestration and business rules

**Contains**:
- VM lifecycle orchestration
- Volume management logic
- Validation and error handling
- State transitions

**Files**:
- `app/services/vm_service.py`
- `app/services/volume_service.py`

**Example**:
```python
class VMService:
    def __init__(self, provider: OpenStackProvider):
        self.provider = provider
    
    async def create_vm(self, spec: CreateVMRequest) -> VM:
        # Validate
        if await self._vm_exists(spec.name):
            raise VMAlreadyExistsError(spec.name)
        
        # Orchestrate
        server = await self.provider.create_server(spec)
        
        # Return domain model
        return VM.from_server(server)
```

### Layer 3: Provider Abstraction (Infrastructure Interface)

**Responsibility**: Define contract for infrastructure operations

**Contains**:
- Abstract base class
- Provider implementations
- Model mapping

**Files**:
- `app/providers/base.py`
- `app/providers/mock_provider.py`
- `app/providers/openstack_provider.py`

**Example**:
```python
class OpenStackProvider(ABC):
    @abstractmethod
    async def create_server(self, spec: ServerSpec) -> Server: ...
    
    @abstractmethod
    async def list_servers(self) -> List[Server]: ...

class MockOpenStackProvider(OpenStackProvider):
    async def create_server(self, spec: ServerSpec) -> Server:
        # In-memory implementation
        pass

class RealOpenStackProvider(OpenStackProvider):
    async def create_server(self, spec: ServerSpec) -> Server:
        # Real OpenStack SDK implementation
        pass
```

### Layer 4: Infrastructure (External)

**Responsibility**: Actual infrastructure

**Contains**:
- OpenStack SDK
- Network calls
- Real VMs and volumes

---

## Data Models

### Domain Models (Internal)

Located in `app/core/models.py`:

```python
class VMStatus(str, Enum):
    """VM lifecycle states"""
    BUILDING = "BUILDING"      # Being created
    ACTIVE = "ACTIVE"          # Running
    STOPPED = "STOPPED"        # Stopped
    REBOOTING = "REBOOTING"    # Rebooting
    DELETING = "DELETING"      # Being deleted
    ERROR = "ERROR"            # Error state

class VM:
    """Domain model for Virtual Machine"""
    id: str
    name: str
    status: VMStatus
    image_id: str
    flavor_id: str
    network_ids: List[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime

class Volume:
    """Domain model for Storage Volume"""
    id: str
    name: str
    size_gb: int
    status: str
    volume_type: str
    attachments: List[dict]
    created_at: datetime
```

### Pydantic Schemas (API Contracts)

Located in `app/api/schemas/`:

```python
# Request schemas
class CreateVMRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    image_id: str
    flavor_id: str
    network_ids: List[str] = []
    metadata: dict = {}

# Response schemas
class VMResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "vm-123",
                "name": "web-server-01",
                "status": "ACTIVE",
                "created_at": "2024-05-14T15:30:00Z"
            }
        }
```

**Separation**:
- Domain models: Internal, change rarely
- Pydantic schemas: API contracts, can evolve independently

---

## Error Handling Strategy

### Exception Hierarchy

```
Exception (Python base)
└── OpenStackError (base for our errors)
    ├── VMError
    │   ├── VMNotFoundError (404)
    │   ├── VMAlreadyExistsError (409)
    │   ├── VMInvalidStateError (400)
    │   └── VMOperationError (500)
    ├── VolumeError
    │   ├── VolumeNotFoundError (404)
    │   ├── VolumeAlreadyAttachedError (409)
    │   └── VolumeOperationError (500)
    ├── ProviderError (503)
    │   ├── ProviderConnectionError
    │   ├── ProviderAuthError
    │   └── ProviderQuotaError
    └── ValidationError (422)
```

### Error Response Format

**Consistent error responses**:
```json
{
  "error_code": "VM_NOT_FOUND",
  "message": "VM with id 'vm-123' not found",
  "details": {
    "requested_id": "vm-123",
    "available_operations": ["create", "list"]
  },
  "timestamp": "2024-05-14T15:30:00Z"
}
```

### Error Handling in Routes

```python
@router.post("/vms")
async def create_vm(req: CreateVMRequest):
    try:
        vm = await vm_service.create_vm(req)
        return VMResponse(**vm.dict())
    
    except VMAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.dict())
    
    except ProviderError as e:
        raise HTTPException(status_code=503, detail="Provider unavailable")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

---

## Configuration Management

### Pydantic Settings

Located in `app/core/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Provider
    provider: str = "mock"  # "mock" or "openstack"
    
    # Logging
    log_level: str = "INFO"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # OpenStack (if provider=openstack)
    os_auth_url: str | None = None
    os_project_id: str | None = None
    os_project_name: str | None = None
    os_username: str | None = None
    os_password: str | None = None
    os_user_domain_name: str = "Default"
    os_project_domain_name: str = "Default"
    os_region_name: str = "SBG5"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# At startup
settings = Settings()
provider = get_provider(settings)
```

**Benefits**:
- ✅ Type-safe configuration
- ✅ Validated at startup
- ✅ 12-factor compliance (env vars)
- ✅ Easy to override per environment

---

## Provider Abstraction

### Base Interface

```python
from abc import ABC, abstractmethod

class OpenStackProvider(ABC):
    """Abstract interface for OpenStack operations"""
    
    # Compute operations
    @abstractmethod
    async def create_server(self, spec: ServerSpec) -> Server: ...
    
    @abstractmethod
    async def list_servers(self) -> List[Server]: ...
    
    @abstractmethod
    async def get_server(self, id: str) -> Server: ...
    
    @abstractmethod
    async def delete_server(self, id: str) -> None: ...
    
    @abstractmethod
    async def start_server(self, id: str) -> Server: ...
    
    @abstractmethod
    async def stop_server(self, id: str) -> Server: ...
    
    # Volume operations
    @abstractmethod
    async def create_volume(self, spec: VolumeSpec) -> Volume: ...
    
    # ... etc
```

### Mock Provider

```python
class MockOpenStackProvider(OpenStackProvider):
    """In-memory mock for testing"""
    
    def __init__(self):
        self.servers = {}
        self.volumes = {}
        self.next_server_id = 1
    
    async def create_server(self, spec: ServerSpec) -> Server:
        server_id = f"server-{self.next_server_id}"
        self.next_server_id += 1
        server = Server(
            id=server_id,
            name=spec.name,
            status="BUILDING",
            ...
        )
        self.servers[server_id] = server
        return server
```

### Real Provider

```python
class RealOpenStackProvider(OpenStackProvider):
    """Real OpenStack SDK implementation"""
    
    def __init__(self, conn):
        self.conn = conn
    
    async def create_server(self, spec: ServerSpec) -> Server:
        os_server = self.conn.compute.create_server(
            name=spec.name,
            image=spec.image_id,
            flavor=spec.flavor_id,
            networks=spec.network_ids
        )
        return Server.from_openstack(os_server)
```

---

## Async/Await Patterns

### Why Async?

1. **Scalability**: Handle thousands of concurrent requests
2. **Performance**: Non-blocking I/O, efficient CPU usage
3. **Modern**: Matches FastAPI and OpenStack SDK async operations

### Async Throughout

```python
# Routes are async
@app.post("/vms")
async def create_vm(req: CreateVMRequest):
    return await vm_service.create_vm(req)

# Services are async
class VMService:
    async def create_vm(self, spec: CreateVMRequest) -> VM:
        return await self.provider.create_server(spec)

# Providers are async
class MockOpenStackProvider(OpenStackProvider):
    async def create_server(self, spec: ServerSpec) -> Server:
        # Simulate I/O with await asyncio.sleep()
        await asyncio.sleep(0.1)
        return Server(...)
```

### Concurrent Operations

```python
# Multiple VMs created concurrently
async def create_multiple_vms(specs: List[CreateVMRequest]):
    tasks = [vm_service.create_vm(spec) for spec in specs]
    vms = await asyncio.gather(*tasks)
    return vms
```

---

## Dependency Injection

### Manual Injection (No Framework)

Simple, explicit, no magic:

```python
# At app startup
async def lifespan(app: FastAPI):
    # Setup
    settings = Settings()
    provider = get_provider(settings)
    vm_service = VMService(provider)
    volume_service = VolumeService(provider)
    
    # Make available to routes
    app.state.vm_service = vm_service
    app.state.volume_service = volume_service
    
    yield
    
    # Cleanup
    pass

app = FastAPI(lifespan=lifespan)

# In routes, access via app.state
@app.post("/vms")
async def create_vm(req: CreateVMRequest, app: FastAPI = Depends(lambda: app)):
    return await app.state.vm_service.create_vm(req)
```

**Benefits**:
- ✅ Explicit dependencies
- ✅ No framework magic
- ✅ Easy to understand

---

## Testing Strategy

### Unit Tests (Services)

Test business logic with mock provider:

```python
@pytest.fixture
def mock_provider():
    return MockOpenStackProvider()

@pytest.fixture
def vm_service(mock_provider):
    return VMService(mock_provider)

@pytest.mark.asyncio
async def test_create_vm_success(vm_service):
    """Test VM creation"""
    req = CreateVMRequest(name="test", image_id="img", flavor_id="2")
    vm = await vm_service.create_vm(req)
    assert vm.name == "test"

@pytest.mark.asyncio
async def test_create_vm_duplicate_name(vm_service):
    """Test duplicate name raises error"""
    req = CreateVMRequest(name="test", image_id="img", flavor_id="2")
    await vm_service.create_vm(req)
    
    with pytest.raises(VMAlreadyExistsError):
        await vm_service.create_vm(req)
```

### Integration Tests (API Endpoints)

Test endpoints with TestClient:

```python
def test_create_vm_endpoint():
    response = client.post("/api/v1/vms", json={
        "name": "test",
        "image_id": "img",
        "flavor_id": "2"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test"
```

### Coverage Target

**80%+ coverage** focusing on:
- Service business logic
- Error handling paths
- API response contracts
- Schema validation

---

## Monitoring & Observability

### Structured Logging

Context-rich logging:

```python
import structlog

logger = structlog.get_logger()

# Example
logger.info(
    "vm_create_started",
    vm_name="web-server-01",
    image_id="...",
    request_id="req-123"
)

logger.error(
    "vm_create_failed",
    error_code="INVALID_IMAGE",
    error_message="Image not found",
    request_id="req-123"
)
```

### Prometheus Metrics (Ready for Phase 2)

Metrics infrastructure ready:

```python
from prometheus_client import Counter, Histogram

vm_operations = Counter(
    "vm_operations_total",
    "Total VM operations",
    ["operation", "status"]
)

vm_duration = Histogram(
    "vm_operation_duration_seconds",
    "VM operation duration",
    ["operation"]
)

# Usage
vm_operations.labels(operation="create", status="success").inc()
```

---

## Future Extensibility

### Multi-Provider Support

Easy to add new cloud providers:

```python
class AWSProvider(OpenStackProvider):
    async def create_server(self, spec: ServerSpec) -> Server:
        # AWS implementation
        pass

class AzureProvider(OpenStackProvider):
    async def create_server(self, spec: ServerSpec) -> Server:
        # Azure implementation
        pass

# Just swap provider at startup
provider = get_provider(settings)  # auto-selects based on config
```

### Additional Features

Structure allows easy addition:

- **Networking**: New NeutronService class
- **Storage**: Extended VolumeService capabilities
- **Orchestration**: WorkflowService for multi-step operations
- **Workflow Queue**: Async job processing with Celery/RabbitMQ
- **Caching**: Redis integration layer
- **Auth**: JWT/OAuth2 middleware

### Versioning Strategy

Support multiple API versions:

```python
app = FastAPI()

# v1 routes
@app.include_router(vms_v1.router, prefix="/api/v1")

# v2 routes (future)
@app.include_router(vms_v2.router, prefix="/api/v2")
```

---

## Summary

This architecture provides:

✅ **Clean separation** of concerns (routes → services → providers)  
✅ **Testability** through dependency injection and interfaces  
✅ **Extensibility** via provider pattern and layered design  
✅ **Maintainability** through clear responsibilities  
✅ **Scalability** via async/await throughout  
✅ **SOLID principles** applied consistently  
✅ **Professional practices** for production code  

The design is opinionated but flexible, allowing for growth and evolution as requirements change.
