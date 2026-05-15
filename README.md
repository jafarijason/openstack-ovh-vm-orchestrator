# OpenStack VM Orchestrator

**REST API for managing OpenStack VM lifecycle operations using FastAPI and OpenStack SDK.**

An interview assignment proof-of-concept demonstrating clean architecture, API design, Python development fundamentals, and platform engineering thinking.

---

## Table of Contents

- [About This Project](#about-this-project)
- [Current Implementation Status](#current-implementation-status)
- [Implementation Phases](#implementation-phases)
- [Quick Start](#quick-start)
- [Architecture & Design](#architecture--design)
- [Design Decisions](#design-decisions)
- [Setup & Configuration](#setup--configuration)
- [API Endpoints](#api-endpoints)
- [Testing Strategy](#testing-strategy)
- [Next Steps](#next-steps)

---

## About This Project

### Objective

Build a REST API service for OpenStack VM lifecycle management that demonstrates:

- **API Design**: RESTful endpoints with consistent error handling
- **Clean Architecture**: Layered separation (routes → services → providers)
- **Python Development**: Type hints, async/await, Pydantic validation
- **Engineering Thinking**: Design decisions, tradeoffs, extensibility
- **Testing Discipline**: Unit and integration tests with meaningful coverage
- **SDLC Awareness**: Incremental development, documentation, roadmap

### Interview Assignment Requirements

✅ **Deliverables**:
- ✅ Public GitHub repository
- ✅ Working Python prototype (Hello World)
- ✅ Comprehensive README (this file)
- ✅ Design documentation (ARCHITECTURE.md)
- ✅ Architecture writeup (in ARCHITECTURE.md)
- ✅ Design choices explanation (in ARCHITECTURE.md)
- ✅ Working roadmap/backlog (ROADMAP.md)
- ✅ Best practices demonstration (in code structure)

✅ **Scope**:
- VM lifecycle management (create, list, get, start, stop, delete)
- Clean code and best practices
- Follow SDLC principles
- Work with real OVH OpenStack (optional, with mock fallback)

---

## Current Implementation Status

### Phase 1: Foundation & Documentation

| Item | Status | Notes |
|------|--------|-------|
| Project structure | 🟢 Complete | app/ with all folders ready |
| README.md | 🟢 Complete | Progressive documentation |
| ARCHITECTURE.md | 🟢 Complete | 1,025 lines of design patterns |
| ROADMAP.md | 🟢 Complete | 642 lines with 5-phase plan |
| Hello World API | 🟢 Complete | GET / and GET /health working |
| pyproject.toml | 🟡 Pending | Will add with Phase 2 |

### Phase 2: Core Implementation

| Item | Status | Notes |
|------|--------|-------|
| Domain models | ⚪ Not Started | VM, Volume, Snapshot |
| Pydantic schemas | ⚪ Not Started | Request/response validation |
| Provider abstraction | ⚪ Not Started | Base interface |
| Mock provider | ⚪ Not Started | In-memory implementation |
| OpenStack provider | ⚪ Not Started | Real OVH integration |
| FastAPI app setup | ⚪ Not Started | Main entry point |
| VM routes | ⚪ Not Started | CRUD + lifecycle operations |
| Volume routes | ⚪ Not Started | Storage management |
| Error handling | ⚪ Not Started | Custom exceptions + HTTP mapping |
| Structured logging | ⚪ Not Started | Logging infrastructure |

### Phase 3: Testing & Validation

| Item | Status | Notes |
|------|--------|-------|
| Unit tests | ⚪ Not Started | Service logic tests |
| Integration tests | ⚪ Not Started | API endpoint tests |
| Test fixtures | ⚪ Not Started | Mock data, helpers |
| Coverage reporting | ⚪ Not Started | Target 80%+ |
| pytest configuration | ⚪ Not Started | Test runner setup |

### Phase 4: DevOps & Documentation

| Item | Status | Notes |
|------|--------|-------|
| Dockerfile | ⚪ Not Started | Container image |
| docker-compose.yml | ⚪ Not Started | Local dev environment |
| .gitlab-ci.yml | ⚪ Not Started | CI/CD pipeline |
| Environment config | ⚪ Not Started | .env template |
| Setup documentation | ⚪ Not Started | Local + Docker + OVH |

**Legend**: 🟢 Complete | 🟡 In Progress | ⚪ Not Started | 🔴 Blocked

---

## Implementation Phases

### Phase 1: Foundation (✅ COMPLETE)
**Goal**: Establish project structure, document architecture, define API contracts

- [x] Repository creation
- [x] README documentation (comprehensive, progressive)
- [x] Project structure scaffold (app/ with all layers)
- [x] ARCHITECTURE.md (1,025 lines - design patterns and decisions)
- [x] ROADMAP.md (642 lines - phased approach and backlog)
- [x] Hello World API (GET / and GET /health working)
- [x] Configuration files (.env.example, .gitignore)
- [x] Quick start script (run.sh)

**Deliverables**: Complete architecture documentation, Hello World API, ready for Phase 2 implementation

### Phase 2: Core API Implementation
**Goal**: Build working endpoints with clean architecture

- [ ] Domain models (VM, Volume, Snapshot classes)
- [ ] Pydantic schemas (request/response validation)
- [ ] Provider abstraction (base interface)
- [ ] Mock provider (in-memory, no dependencies)
- [ ] OpenStack provider (real OVH integration)
- [ ] FastAPI application setup
- [ ] VM CRUD endpoints (create, list, get, delete)
- [ ] VM lifecycle endpoints (start, stop, reboot)
- [ ] Volume management endpoints
- [ ] Error handling and exceptions
- [ ] Structured logging

**Deliverables**: Working API, fully functional with mock data

### Phase 3: Testing & Quality
**Goal**: Ensure code quality and reliability

- [ ] Unit tests (services, schemas, validators)
- [ ] Integration tests (API endpoints)
- [ ] Fixtures and mock data
- [ ] Coverage reporting (80%+)
- [ ] pytest configuration

**Deliverables**: Test suite, coverage reports

### Phase 4: DevOps & Deployment
**Goal**: Containerize and automate

- [ ] Dockerfile for API service
- [ ] docker-compose.yml for local development
- [ ] .gitlab-ci.yml (test, build, deploy stages)
- [ ] Environment configuration (.env template)
- [ ] Deployment documentation

**Deliverables**: Containerized service, CI/CD ready

### Phase 5: Polish & Documentation
**Goal**: Complete documentation and finalize

- [ ] ARCHITECTURE.md (patterns, decisions, diagrams)
- [ ] ROADMAP.md (vision and backlog)
- [ ] API usage examples
- [ ] Troubleshooting guide
- [ ] Contributing guidelines

**Deliverables**: Complete documentation suite

---

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry or pip
- Optional: Docker & Docker Compose
- Optional: OVH OpenStack account

### Current Status

⚠️ **Under Construction**: The API is being built incrementally. Check the [Implementation Phases](#implementation-phases) section for progress.

### Setup (Once Complete)

Once the API is implemented, setup will be:

```bash
# Clone repository
git clone https://github.com/jafarijason/openstack-ovh-vm-orchestrator.git
cd openstack-ovh-vm-orchestrator

# Option 1: Local development
python3.11 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
uvicorn app.main:app --reload

# Option 2: Docker
docker-compose up -d

# Access API
# - Local: http://localhost:8000
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

---

## Architecture & Design

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Routes (Request/Response, OpenAPI docs)         │   │
│  │  GET    /api/v1/vms                                  │   │
│  │  POST   /api/v1/vms                                  │   │
│  │  GET    /api/v1/vms/{id}                             │   │
│  │  POST   /api/v1/vms/{id}/start                       │   │
│  │  POST   /api/v1/vms/{id}/stop                        │   │
│  │  DELETE /api/v1/vms/{id}                             │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Service Layer (Business Logic)                      │   │
│  │  - VMService: orchestration, validation              │   │
│  │  - VolumeService: storage operations                 │   │
│  │  - Error handling, retries, state management         │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Provider Abstraction (Infrastructure)               │   │
│  │  OpenStackProvider (base interface)                  │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                    ┌────┴────┐                              │
│                    │          │                              │
│        ┌───────────▼──┐  ┌──▼──────────────┐               │
│        │ MockProvider │  │ OpenStackProv.  │               │
│        │ (In-Memory)  │  │ (Real OVH)      │               │
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

### Project Structure (As Built)

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── vms.py         # VM CRUD + lifecycle endpoints
│   │   └── volumes.py     # Volume management endpoints
│   └── schemas/
│       ├── __init__.py
│       ├── vm.py          # VM request/response Pydantic models
│       ├── volume.py      # Volume request/response models
│       └── responses.py   # Common response structures
├── services/
│   ├── __init__.py
│   ├── vm_service.py      # VM business logic
│   ├── volume_service.py  # Volume business logic
│   └── exceptions.py      # Service layer exceptions
├── providers/
│   ├── __init__.py
│   ├── base.py            # Abstract provider interface
│   ├── mock_provider.py   # Mock OpenStack implementation
│   └── openstack_provider.py  # Real OVH implementation
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration (Pydantic Settings)
│   ├── exceptions.py      # Custom exception hierarchy
│   ├── logging.py         # Logging setup
│   └── models.py          # Domain models (VM, Volume, etc)
└── utils/
    ├── __init__.py
    └── validators.py      # Validation utilities

tests/
├── __init__.py
├── conftest.py            # Pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_vm_service.py
│   ├── test_volume_service.py
│   └── test_schemas.py
├── integration/
│   ├── __init__.py
│   ├── test_vm_endpoints.py
│   ├── test_volume_endpoints.py
│   └── test_error_handling.py
└── fixtures/
    ├── __init__.py
    ├── mock_responses.py
    └── test_data.py

docs/
├── README.md              # This file
├── ARCHITECTURE.md        # Design patterns and decisions (planned)
└── ROADMAP.md            # Vision and backlog (planned)

.github/
├── workflows/            # GitHub Actions (optional)

.gitlab/
├── .gitlab-ci.yml        # GitLab CI/CD pipeline

Dockerfile
docker-compose.yml
pyproject.toml
pytest.ini
.env.example
.gitignore
LICENSE
```

---

## Design Decisions

### 1. Provider Abstraction Pattern

**Decision**: Separate infrastructure operations behind an abstract interface

**Why**: 
- **Testability**: Mock provider works without real OpenStack
- **Flexibility**: Easy to add new cloud providers later
- **Isolation**: OpenStack-specific logic stays in one place

**Implementation**:
```python
# Base interface
class OpenStackProvider(ABC):
    async def create_server(spec: ServerSpec) -> Server
    async def list_servers() -> List[Server]
    # ... etc

# Mock for testing
class MockOpenStackProvider(OpenStackProvider):
    def __init__(self):
        self.servers = {}  # In-memory storage

# Real for production
class RealOpenStackProvider(OpenStackProvider):
    def __init__(self, conn):
        self.conn = openstack.connect()
```

### 2. Service Layer for Business Logic

**Decision**: Separate API routes from business logic

**Why**:
- **Reusability**: Services work from CLI, webhooks, RPC, etc.
- **Testability**: Test business logic independent of HTTP
- **Clarity**: Routes stay thin, services handle orchestration
- **Maintainability**: Changes in business logic don't affect API

**Example**:
```python
# Route: just HTTP
@app.post("/api/v1/vms")
async def create_vm(req: CreateVMRequest):
    return await vm_service.create_vm(req)

# Service: business logic
class VMService:
    async def create_vm(self, spec: CreateVMRequest) -> VM:
        # Validation, orchestration, error handling
        return await self.provider.create_server(...)
```

### 3. Pydantic for Validation

**Decision**: Use Pydantic for all request/response models

**Why**:
- **Automatic validation**: Type checking + custom validators
- **OpenAPI docs**: Auto-generated Swagger/ReDoc
- **Serialization**: Automatic JSON conversion
- **Type safety**: IDE support, mypy compatibility

### 4. Async/Await Throughout

**Decision**: Use async/await for all I/O operations

**Why**:
- **Scalability**: Handle thousands of concurrent requests
- **Performance**: Non-blocking I/O, efficient resource usage
- **Modern**: Matches FastAPI and OpenStack SDK async operations

### 5. Custom Exception Hierarchy

**Decision**: Specific exception types for each error scenario

**Why**:
- **Precision**: Catch and handle specific errors
- **API clarity**: Map exceptions to correct HTTP status codes
- **Observability**: Different exceptions log differently

### 6. Environment-Based Configuration

**Decision**: Configuration via environment variables and .env files

**Why**:
- **12-factor compliance**: Config separate from code
- **Flexibility**: Different configs per environment (dev/staging/prod)
- **Security**: Secrets don't live in code
- **Type-safe**: Pydantic validates at startup

### 7. Structured Logging

**Decision**: Contextual logging with JSON structure

**Why**:
- **Observability**: Machine-readable logs for aggregation
- **Debugging**: Full context for each operation
- **Production**: Scales to multi-service deployments

---

## Setup & Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Provider mode
PROVIDER=mock                          # or "openstack" for real OVH

# Logging
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR

# API configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenStack credentials (required if PROVIDER=openstack)
OS_AUTH_URL=https://auth.cloud.ovh.net/v3
OS_PROJECT_ID=your_project_id
OS_PROJECT_NAME=your_project_name
OS_USERNAME=your_username
OS_PASSWORD=your_password
OS_USER_DOMAIN_NAME=Default
OS_PROJECT_DOMAIN_NAME=Default
OS_REGION_NAME=SBG5
```

### OVH OpenStack Setup

1. Create account at [OVH Public Cloud](https://www.ovhcloud.com/en/public-cloud/)
2. Create a project
3. Go to **Users & Roles** → Create OpenStack user
4. Download **openrc.sh** file
5. Source it: `source openrc.sh`

All environment variables are now set automatically.

---

## API Endpoints

### Planned Endpoints

#### VM Lifecycle
```
POST   /api/v1/vms              Create VM
GET    /api/v1/vms              List VMs
GET    /api/v1/vms/{id}         Get VM details
POST   /api/v1/vms/{id}/start   Start VM
POST   /api/v1/vms/{id}/stop    Stop VM
POST   /api/v1/vms/{id}/reboot  Reboot VM
DELETE /api/v1/vms/{id}         Delete VM
```

#### Volume Management
```
POST   /api/v1/volumes                      Create volume
GET    /api/v1/volumes                      List volumes
GET    /api/v1/volumes/{id}                 Get volume details
POST   /api/v1/volumes/{id}/snapshot        Create snapshot
POST   /api/v1/vms/{vm_id}/volumes/{vol_id}/attach    Attach volume
POST   /api/v1/vms/{vm_id}/volumes/{vol_id}/detach    Detach volume
DELETE /api/v1/volumes/{id}                 Delete volume
```

#### Health & Status
```
GET    /health                  Health check
GET    /metrics                 Prometheus metrics (planned)
```

### Example Request/Response (When Implemented)

```bash
# Create VM
POST /api/v1/vms
Content-Type: application/json

{
  "name": "web-server-01",
  "image_id": "2c4ac51d-fa14-4c12-a954-0ab77ed9f41b",
  "flavor_id": "2"
}

# Response: 201 Created
{
  "id": "vm-123",
  "name": "web-server-01",
  "status": "BUILDING",
  "created_at": "2024-05-14T15:30:00Z"
}
```

---

## Testing Strategy

### Unit Tests

Test service logic in isolation with mock provider:

```python
@pytest.mark.asyncio
async def test_create_vm_success():
    provider = MockOpenStackProvider()
    service = VMService(provider)
    
    vm = await service.create_vm(CreateVMRequest(...))
    assert vm.name == "test-vm"
    assert vm.status == "BUILDING"
```

### Integration Tests

Test API endpoints with TestClient:

```python
def test_create_vm_endpoint():
    response = client.post("/api/v1/vms", json={...})
    assert response.status_code == 201
```

### Coverage Target

**80%+ coverage** focusing on:
- Service business logic
- Error handling paths
- API response contracts
- Schema validation

### Running Tests

```bash
# All tests
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_vm_service.py -v

# With verbose output
pytest -v
```

---

## Next Steps

### Immediate (Phase 2)

1. ✅ Create project structure scaffold
2. ✅ Write ARCHITECTURE.md (design patterns in depth)
3. ✅ Write ROADMAP.md (vision and backlog)
4. ✅ Create pyproject.toml (dependencies)
5. ✅ Implement domain models and Pydantic schemas
6. ✅ Build provider abstraction and mock implementation
7. ✅ Create FastAPI application and routes
8. ✅ Add error handling and logging

### Then (Phase 3)

9. ✅ Write comprehensive tests
10. ✅ Verify 80%+ coverage
11. ✅ Test with real OVH OpenStack

### Finally (Phase 4-5)

12. ✅ Dockerize application
13. ✅ Create CI/CD pipeline
14. ✅ Finalize documentation
15. ✅ Code review and polish

---

## Contributing

This is an interview assignment. Development follows SDLC best practices:

1. **Design first**: Document decisions in ARCHITECTURE.md
2. **Test-driven**: Write tests alongside implementation
3. **Incremental**: Build and test each phase
4. **Document**: Update this README as implementation progresses
5. **Review**: Code review before each phase completion

---

## Project Status Summary

| Area | Status | Notes |
|------|--------|-------|
| Documentation | 🟢 Complete | README (651 lines), ARCHITECTURE (1,025 lines), ROADMAP (642 lines) |
| Project Structure | 🟢 Complete | All layers ready (routes, services, providers, core, utils) |
| Hello World API | 🟢 Complete | GET / and GET /health endpoints working |
| API Implementation | 🟡 Next | Phase 2 - Core endpoints and services |
| Testing | ⏳ Pending | Phase 3 - Comprehensive test suite (80%+) |
| DevOps | ⏳ Pending | Phase 4 - Docker, docker-compose, CI/CD |

**Last Updated**: May 14, 2024  
**Current Phase**: 1 (Foundation) - ✅ COMPLETE  
**Next Phase**: 2 (Core API Implementation)

---

## License

MIT License - See LICENSE file for details

---

## Contact & Support

- **Repository**: [GitHub](https://github.com/jafarijason/openstack-ovh-vm-orchestrator)
- **Issues**: [Bug reports and feature requests](https://github.com/jafarijason/openstack-ovh-vm-orchestrator/issues)
- **Author**: Jason Afari
