# Contributing to OpenStack VM Orchestrator

Thank you for your interest in contributing! This guide will help you set up your development environment and understand our development practices.

## Table of Contents

- [Quick Start for Contributors](#quick-start-for-contributors)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Making Changes](#making-changes)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Troubleshooting](#troubleshooting)

## Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/<your-username>/openstack-ovh-vm-orchestrator.git
cd openstack-ovh-vm-orchestrator
git remote add upstream https://github.com/jafarijason/openstack-ovh-vm-orchestrator.git
```

### 2. Set Up Development Environment

```bash
# Backend setup
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (optional for backend-only work)
cd frontend
npm install
cd ..
```

### 3. Start Development Servers

```bash
# Terminal 1: Backend
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend (optional)
cd frontend
npm run dev
```

### 4. Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests with coverage
pytest --cov=api tests/

# Run specific test file
pytest tests/unit/test_services.py -v
```

### 5. Make Your Changes

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes, commit, and push
git push origin feature/your-feature-name

# Open a pull request on GitHub
```

---

## Development Setup

### Backend Setup

**Requirements:**
- Python 3.11+
- pip or poetry

**Installation:**

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import uvicorn; import fastapi; print('✅ Setup successful')"
```

**Run Backend:**

```bash
# Development mode (with auto-reload)
python -m uvicorn api.main:app --reload --port 8000

# Or with specific cloud provider
OS_CLOUD=mock python -m uvicorn api.main:app --reload --port 8000
OS_CLOUD=ovh python -m uvicorn api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

**Requirements:**
- Node.js 18+
- npm or yarn

**Installation:**

```bash
cd frontend
npm install
```

**Run Frontend:**

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:5174` (or next available port)

### Docker Setup (Optional)

```bash
# Build Docker image
docker build -t openstack-orchestrator .

# Run with docker-compose
docker-compose up -d

# Check if running
curl http://localhost:8000/health
```

---

## Project Structure

**Key Backend Directories:**

```
api/
├── main.py                     # FastAPI application entry point
├── core/
│   ├── models.py              # Domain models (VM, Network, etc)
│   ├── config.py              # Configuration
│   └── exceptions.py          # Custom exception hierarchy
├── providers/
│   ├── base.py                # Abstract provider interface
│   ├── mock_provider.py       # Mock implementation for testing
│   └── openstack_provider.py  # Real OVH OpenStack integration
├── services/
│   ├── vm_service.py          # VM business logic
│   ├── network_service.py     # Network business logic
│   └── ...                    # Other services
├── api/
│   ├── routes/                # Endpoint definitions
│   │   ├── vm.py
│   │   ├── network.py
│   │   └── ...
│   └── schemas/               # Pydantic models
│       ├── vm.py
│       ├── network.py
│       └── ...
└── utils/                     # Utility functions
```

**Key Test Directories:**

```
tests/
├── conftest.py                # Pytest fixtures and configuration
├── unit/                      # Unit tests
│   ├── test_services.py       # Service layer tests
│   └── test_schemas.py        # Schema validation tests
├── integration/               # Integration tests
│   ├── test_vm_endpoints.py   # API endpoint tests
│   └── test_networks.py       # Network endpoint tests
└── fixtures/                  # Mock data and helpers
```

---

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=api tests/

# Generate HTML coverage report
pytest --cov=api --cov-report=html tests/
# Open htmlcov/index.html in browser
```

### Run Specific Tests

```bash
# Run specific test file
pytest tests/unit/test_services.py -v

# Run specific test function
pytest tests/unit/test_services.py::test_create_vm -v

# Run tests matching a pattern
pytest -k "test_vm" -v

# Run integration tests only
pytest tests/integration/ -v
```

### Test with Different Providers

```bash
# Run tests with mock provider (default)
OS_CLOUD=mock pytest tests/

# Run tests with OVH OpenStack (requires credentials)
OS_CLOUD=ovh pytest tests/
```

### Test Coverage Goals

**Target: 60-70% coverage** for quick polish

```bash
# Check coverage
pytest --cov=api --cov-report=term-missing tests/

# Expected output should show:
# - api/core/models.py       ~90% coverage
# - api/services/*.py        ~85% coverage  
# - api/api/routes/*.py      ~75% coverage
# - api/providers/*.py       ~70% coverage
```

---

## Making Changes

### Backend Changes

**Adding a New Service Method:**

1. Update `api/core/models.py` if needed
2. Add method to service in `api/services/XXX_service.py`
3. Add method to provider interface in `api/providers/base.py`
4. Implement in both `api/providers/mock_provider.py` and `api/providers/openstack_provider.py`
5. Create endpoint in `api/api/routes/XXX.py`
6. Add request/response schema in `api/api/schemas/XXX.py`
7. Write unit test in `tests/unit/test_services.py`
8. Write integration test in `tests/integration/test_XXX_endpoints.py`

**Example: Adding a "shutdown" action to VMs**

```python
# 1. api/services/vm_service.py
async def shutdown_vm(self, vm_id: str) -> VM:
    """Graceful VM shutdown"""
    return await self.provider.shutdown_server(vm_id)

# 2. api/providers/base.py
@abstractmethod
async def shutdown_server(self, server_id: str) -> Server:
    pass

# 3. api/providers/mock_provider.py & openstack_provider.py
async def shutdown_server(self, server_id: str) -> Server:
    # Implementation here

# 4. api/api/routes/vm.py
@router.post("/vms/{vm_id}/shutdown")
async def shutdown_vm(vm_id: str) -> VMResponse:
    return await vm_service.shutdown_vm(vm_id)

# 5. tests/unit/test_services.py
async def test_shutdown_vm():
    vm = await service.shutdown_vm("vm-001")
    assert vm.status == "STOPPED"
```

### Frontend Changes

**Adding a New API Client Method:**

1. Check `frontend/src/types/api.ts` for available types (auto-generated from schema.json)
2. Add method to `frontend/src/services/XXXService.ts`
3. Create component in `frontend/src/components/`
4. Use in page component in `frontend/src/pages/`
5. Update routing in `frontend/src/App.tsx` if needed

**Regenerating Types After Backend Changes:**

```bash
cd frontend
npm run generate-types  # Regenerates src/types/api.ts from backend schema.json
```

---

## Commit Guidelines

**Commit Message Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring (no behavior change)
- `test`: Adding or updating tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks

**Scope:**
- `vm`: VM-related changes
- `network`: Network-related changes
- `provider`: Provider abstraction
- `api`: API routes
- `frontend`: Frontend changes
- `tests`: Test infrastructure

**Examples:**

```
feat(vm): add shutdown VM action
test(vm): add unit tests for VM service
docs(contributing): update development setup
fix(network): handle missing networks gracefully
refactor(provider): simplify provider factory pattern
```

**Keep Commits Atomic:**
- One logical change per commit
- Commit works and passes tests
- Clear commit message explaining the "why"

---

## Pull Request Process

### Before Submitting a PR

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests locally:**
   ```bash
   pytest --cov=api tests/
   ```

3. **Check code style:**
   ```bash
   black api/
   flake8 api/
   mypy api/
   ```

4. **Update tests and docs:**
   - Add tests for new functionality
   - Update README/CONTRIBUTING if behavior changes
   - Update API_EXAMPLES.md if adding new endpoints

### Submitting a PR

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature
   ```

2. **Create PR on GitHub:**
   - Clear title: `[Type] Brief description`
   - Link related issues: `Fixes #123`
   - Describe changes in detail
   - List testing performed

3. **PR Template Example:**
   ```markdown
   ## Description
   Brief description of the change

   ## Related Issue
   Fixes #123

   ## Changes Made
   - Change 1
   - Change 2
   - Change 3

   ## Testing
   - [x] Unit tests added/updated
   - [x] Integration tests pass
   - [x] Manual testing completed
   - [x] 60%+ coverage maintained

   ## Checklist
   - [x] Code follows style guidelines
   - [x] Documentation updated
   - [x] No breaking changes
   ```

### After Submitting

- Respond to review feedback
- Push changes to address feedback (don't force push on PR branches)
- Ensure all checks pass before merge

---

## Code Style

### Python Code Style

**Use black, flake8, and mypy:**

```bash
# Format code
black api/

# Check style
flake8 api/ --max-line-length=100

# Type checking
mypy api/ --no-implicit-optional
```

**Style Guidelines:**

- Line length: 100 characters
- Use type hints everywhere
- Use async/await for I/O operations
- Docstrings for public functions/classes
- Write descriptive variable names

**Example:**

```python
from typing import Optional, List
from api.core.models import VM

async def create_vm(
    name: str,
    image_id: str,
    flavor_id: str,
    network_ids: List[str],
    key_name: Optional[str] = None
) -> VM:
    """
    Create a new virtual machine.
    
    Args:
        name: VM name
        image_id: Image ID to use
        flavor_id: Flavor ID (VM size)
        network_ids: List of network IDs to attach
        key_name: Optional SSH key name
        
    Returns:
        Created VM object
        
    Raises:
        VMCreationError: If VM creation fails
    """
    # Implementation
    pass
```

### Frontend Code Style

**Use ESLint and Prettier:**

```bash
cd frontend
npm run lint      # Check linting
npm run format    # Format code
```

---

## Troubleshooting

### Backend Issues

**Problem: `ModuleNotFoundError: No module named 'api'`**

```bash
# Ensure you're in the project root
pwd  # Should end with: openstack-ovh-vm-orchestrator

# Ensure virtual environment is activated
source .venv/bin/activate  # (or .venv\Scripts\activate on Windows)

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: `ConnectionError` when testing with OpenStack provider**

```bash
# Check credentials are set
echo $OS_CLOUD
echo $OS_AUTH_URL

# Use mock provider for development
OS_CLOUD=mock pytest tests/
```

**Problem: Tests fail with `RuntimeError: Event loop is closed`**

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Run tests with asyncio mode
pytest --asyncio-mode=auto tests/
```

### Frontend Issues

**Problem: `npm install` fails**

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

**Problem: Vite dev server not starting**

```bash
# Check if port 5174 is in use
lsof -i :5174  # Kill the process if needed

# Try running on different port
npm run dev -- --port 5175
```

### Docker Issues

**Problem: Docker image won't build**

```bash
# Check Dockerfile syntax
docker build --no-cache -t openstack-orchestrator .

# View build logs
docker build -t openstack-orchestrator . 2>&1 | tail -50
```

**Problem: docker-compose up fails**

```bash
# Check environment variables
cat .env

# View logs
docker-compose logs -f api

# Restart services
docker-compose down
docker-compose up -d
```

---

## Questions or Need Help?

- **GitHub Issues**: https://github.com/jafarijason/openstack-ovh-vm-orchestrator/issues
- **Email**: jason@example.com (see GitHub profile)
- **Check existing docs**: README.md, ARCHITECTURE.md, docs/API_EXAMPLES.md

Thank you for contributing! ❤️
