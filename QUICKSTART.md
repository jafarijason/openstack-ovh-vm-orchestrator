# Quick Start Guide

Get the OpenStack VM Orchestrator running in 5 minutes.

## Prerequisites

- Python 3.11+ OR Docker
- Node.js 18+ (for frontend)
- ~5 minutes and a terminal

## Prerequisites Setup

### Cloud Configuration

Before running the application, you need to set up your cloud configuration:

```bash
# Copy the example clouds.yaml
cp clouds.yaml.example clouds.yaml
```

The `clouds.yaml` file tells the application which cloud provider to use. By default, it's configured to use the **mock provider** (no credentials needed - perfect for development).

**For Production (Real OpenStack/OVH):**
```bash
# Edit clouds.yaml with your credentials
nano clouds.yaml

# Then set the active cloud
export OS_CLOUD=ovh  # or your cloud name
```

---

## Option 1: Local Development (Fastest)

### 1. Install Dependencies

```bash
# Backend
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend (optional)
cd frontend
npm install
cd ..
```

### 2. Prepare Cloud Configuration

```bash
# Set up clouds.yaml (uses mock provider by default)
cp clouds.yaml.example clouds.yaml
```

### 3. Start Backend

```bash
python -m uvicorn api.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 4. Start Frontend (Optional)

```bash
cd frontend
npm run dev
```

### 5. Access

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **Frontend**: http://localhost:5174 (if you ran npm run dev)

### 6. Test It

```bash
# List VMs
curl http://localhost:8000/vms

# Create VM
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-vm",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"]
  }'

# List Networks
curl http://localhost:8000/networks
```

**That's it!** You have a fully functional OpenStack VM orchestrator running with mock data.

---

## Option 2: Docker Compose (Recommended) - Easiest Way

### The Simplest Way to Run Everything

```bash
# 1. Ensure you have clouds.yaml (uses mock provider by default)
cp clouds.yaml.example clouds.yaml

# 2. Start everything with one command
docker-compose up -d

# 3. Wait for services to start (about 5 seconds)
sleep 5

# 4. Access the application
# API: http://localhost:8000
# Frontend: http://localhost:5174
# Swagger UI: http://localhost:8000/docs
```

That's it! No configuration needed. The mock provider will start automatically.

### Check Everything is Running

```bash
# View all containers
docker-compose ps

# View API logs
docker-compose logs api

# View Frontend logs
docker-compose logs frontend

# Test the API
curl http://localhost:8000/health | jq .
```

### Access the Application

- **🌐 Frontend UI**: http://localhost:5174
- **📡 API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔧 API Schema**: http://localhost:8000/openapi.json

### Using Real OpenStack Cloud

```bash
# 1. Update clouds.yaml with your credentials
nano clouds.yaml

# 2. Set the active cloud
export OS_CLOUD=ovh

# 3. Rebuild and restart
docker-compose build
docker-compose up -d
```

### Stop and Clean Up

```bash
# Stop containers (keep data)
docker-compose stop

# Stop and remove containers (clean everything)
docker-compose down

# Stop, remove containers, AND remove volumes
docker-compose down -v
```

---

## Option 3: Production (With Real OpenStack)

### 1. Set Up Cloud Credentials

```bash
# Get from OVH or your OpenStack provider
export OS_AUTH_URL=https://auth.cloud.ovh.net/v3
export OS_PROJECT_ID=your_project_id
export OS_USERNAME=your_username
export OS_PASSWORD=your_password
export OS_REGION_NAME=SBG5
```

### 2. Run with Real Cloud

```bash
export OS_CLOUD=ovh
python -m uvicorn api.main:app --reload --port 8000
```

### 3. Now Commands Affect Real Infrastructure

```bash
# This creates a REAL VM on OVH!
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-vm",
    "image_id": "real-image-id",
    "flavor_id": "m1.small",
    "network_ids": ["real-network-id"]
  }'
```

---

## Running Tests

```bash
# Unit tests only
pytest tests/unit/test_services.py -v

# With coverage
pytest --cov=api tests/unit/test_services.py

# Integration tests (requires environment)
pytest tests/integration/test_vm_endpoints.py -v
```

**Current Status**: 32/32 passing unit tests (100%), 49% coverage

---

## Key Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Examples**: [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)
- **Full README**: [README.md](README.md)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture Details**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Common Tasks

### Create a VM

```bash
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-public"],
    "key_name": "my-key",
    "security_groups": ["default"]
  }'
```

### List All VMs

```bash
curl http://localhost:8000/vms?limit=100
```

### Start/Stop a VM

```bash
# Start
curl -X POST http://localhost:8000/vms/vm-id/action \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# Stop
curl -X POST http://localhost:8000/vms/vm-id/action \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'

# Reboot
curl -X POST http://localhost:8000/vms/vm-id/action \
  -H "Content-Type: application/json" \
  -d '{"action": "reboot"}'
```

### Delete a VM

```bash
curl -X DELETE http://localhost:8000/vms/vm-id
```

### List Networks

```bash
curl http://localhost:8000/networks
```

### List Images

```bash
curl http://localhost:8000/images
```

### List Flavors

```bash
curl http://localhost:8000/flavors
```

### List SSH Keys

```bash
curl http://localhost:8000/ssh-keys
```

---

## Troubleshooting

### Port Already in Use

```bash
# Backend on different port
python -m uvicorn api.main:app --reload --port 8001

# Frontend on different port
cd frontend
npm run dev -- --port 5175
```

### Module Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Docker Issues

```bash
# Clear containers
docker-compose down -v

# Rebuild
docker-compose build --no-cache

# Run again
docker-compose up -d
```

### Tests Failing

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run with verbose output
pytest tests/unit/test_services.py -vv
```

---

## Next Steps

1. **Explore the API** - Visit http://localhost:8000/docs
2. **Read the Examples** - See [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)
3. **Understand the Architecture** - See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Contribute** - Follow [CONTRIBUTING.md](CONTRIBUTING.md)
5. **Deploy to Production** - See deployment options in [README.md](README.md)

---

## Project Status

✅ **Complete**:
- Backend API with 5 resources (VMs, Networks, Images, Flavors, SSH Keys)
- OpenAPI 3.1.0 schema with auto-generated docs
- Frontend UI with React 18 + TypeScript
- Mock provider for development (no credentials needed)
- Real OVH OpenStack integration
- Docker and docker-compose setup
- GitHub Actions CI/CD pipeline
- 23+ passing unit tests with 49% coverage
- Comprehensive documentation and diagrams

⏳ **In Progress**:
- Integration tests (30+ written, need environment)
- Production deployment guide

🔧 **Future**:
- E2E tests
- Kubernetes deployment
- Additional cloud providers
- Performance metrics

---

## Get Help

- **Issues**: https://github.com/jafarijason/openstack-ovh-vm-orchestrator/issues
- **Discussions**: https://github.com/jafarijason/openstack-ovh-vm-orchestrator/discussions
- **Email**: jason@example.com

Happy orchestrating! 🚀
