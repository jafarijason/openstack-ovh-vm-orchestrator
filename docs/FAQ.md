# Frequently Asked Questions (FAQ)

Quick answers to common questions about the OpenStack VM Orchestrator.

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [API Usage](#api-usage)
- [Deployment](#deployment)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## General Questions

### Q: What is the OpenStack VM Orchestrator?

A: It's a REST API for managing OpenStack virtual machine lifecycle operations. It provides a simplified, type-safe interface for:
- Creating and managing VMs
- Managing networks
- Browsing available images and flavors
- Managing SSH key pairs
- Multi-cloud support (Mock for testing, OpenStack for production)

### Q: Is this production-ready?

A: **Yes** for version 0.1.0. It includes:
- ✅ 32/32 passing unit tests
- ✅ Type-safe with full mypy coverage
- ✅ Comprehensive error handling
- ✅ Production-grade Docker setup
- ✅ CI/CD pipeline with security scanning
- ✅ Complete documentation

However, for mission-critical workloads, we recommend:
- Adding authentication (OAuth2)
- Adding rate limiting
- Configuring monitoring and alerts
- Testing in your specific OpenStack environment

### Q: Can I use this with real OpenStack clouds (not mock)?

A: **Yes!** The project supports both:
- **Mock Provider**: For testing (no credentials needed, in-memory)
- **OpenStack Provider**: For real clouds (OVH, private clouds, etc.)

Just set `OS_CLOUD=ovh` (or your cloud name) and configure `clouds.yaml`.

### Q: What cloud providers are supported?

A: Currently supported:
- **Mock** (testing, default)
- **OpenStack** (any OpenStack-compatible cloud: OVH, Rackspace, private, etc.)

Future support planned for:
- AWS (Phase 8)
- Azure (Phase 8)
- Google Cloud (Phase 8)

### Q: How is this different from OpenStack CLI/Horizon?

A: This is a **lightweight REST API** focused on VM lifecycle. Advantages:
- Easier to integrate programmatically (REST instead of CLI)
- Type-safe (OpenAPI schema, Pydantic validation)
- Simplified interface (focused on common operations)
- Multi-cloud abstraction layer
- Modern Python/TypeScript stack
- Interactive React web UI included

### Q: Is this an official OpenStack project?

A: No, this is an **independent open-source project**. It's created as a lab assessment demonstrating enterprise software engineering practices.

### Q: Can I use this in production?

A: **Yes, with caveats:**
- ✅ API layer is production-ready
- ✅ Docker deployment is production-ready
- ⚠️ Authentication not included (add OAuth2)
- ⚠️ No built-in rate limiting (add with middleware)
- ⚠️ No persistent storage for state (uses in-memory mock)
- ⚠️ Single-node only (no clustering)

See `docs/ARCHITECTURE.md` for production deployment guidance.

---

## Installation & Setup

### Q: How do I install this?

A: Three options:

**Option 1: Docker Compose (Recommended)**
```bash
docker-compose up
# Frontend: http://localhost:5174
# API: http://localhost:8000
```

**Option 2: Local Development**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

**Option 3: Production Deployment**
See `docs/QUICKSTART.md` for detailed instructions.

### Q: Do I need Docker?

A: No, Docker is optional:
- **With Docker**: Easier setup, everything isolated
- **Without Docker**: Run directly with Python/Node.js

### Q: Do I need OpenStack installed?

A: No! The mock provider works out-of-the-box. If using real OpenStack:
- You need OpenStack credentials (cloud access)
- You need `clouds.yaml` configured
- You need network access to OpenStack API

### Q: What Python version is required?

A: Python **3.11+** (tested on 3.11, 3.12, 3.13)

### Q: Can I run this on Windows?

A: **Yes**, using Docker Desktop or WSL:
- Docker Desktop (recommended)
- WSL 2 with Linux
- Direct Python installation (need to adapt shell scripts)

### Q: What about macOS?

A: **Yes**, fully supported:
- Docker Desktop (recommended)
- Direct Python installation with Homebrew

### Q: Do I need Node.js?

A: Only if developing the frontend. For backend only, not needed.

Frontend requires: Node.js 18+ (npm or yarn)

---

## API Usage

### Q: How do I make API requests?

A: Use any HTTP client:

```bash
# curl (command line)
curl http://localhost:8000/vms

# Python
import requests
response = requests.get("http://localhost:8000/vms")

# JavaScript/TypeScript
const response = await fetch("http://localhost:8000/vms")
const data = await response.json()
```

### Q: What's the base URL?

A: Default: `http://localhost:8000`

In Docker: `http://api:8000` (from inside Docker)
In production: Your actual domain/IP

### Q: Is authentication required?

A: **Not in 0.1.0**. Authentication is planned for Phase 7.

For production, add OAuth2 or API keys (see `docs/ARCHITECTURE.md`).

### Q: What endpoints are available?

A: See `/docs` (Swagger UI) or `/redoc` (ReDoc UI).

Or check `docs/API_EXAMPLES.md` for detailed examples.

**Main endpoints:**
- `GET/POST /vms` - VM operations
- `GET/POST /networks` - Network operations
- `GET /images` - Image catalog
- `GET /flavors` - Flavor catalog
- `GET/POST /ssh-keys` - SSH key management
- `GET /health` - Health check
- `GET /clouds` - Available clouds

### Q: How do I create a VM?

A: ```bash
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-vm",
    "image_id": "img-001",
    "flavor_id": "m1.small",
    "network_ids": ["net-001"]
  }'
```

### Q: What cloud should I use?

A: **For testing**: Use `MOCK` cloud (default)
```bash
export OS_CLOUD=mock
./run.sh
```

**For production**: Use your OpenStack cloud name:
```bash
export OS_CLOUD=ovh
./run.sh
```

### Q: How do I set up clouds.yaml?

A: ```bash
cp clouds.yaml.example clouds.yaml
# Edit clouds.yaml with your cloud credentials
```

See `docs/QUICKSTART.md` for detailed setup.

### Q: What's the response format?

A: All responses follow this format:

**Success:**
```json
{
  "success": true,
  "data": { /* actual data */ },
  "message": null
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "status_code": 400
  }
}
```

### Q: Can I get API docs in OpenAPI format?

A: Yes: `http://localhost:8000/openapi.json`

This is an OpenAPI 3.1.0 schema. Use it to generate clients for any language.

### Q: How do I filter/search VMs?

A: Currently pagination is supported:
```bash
curl "http://localhost:8000/vms?limit=10&offset=0"
```

Filtering by name/status is planned for Phase 6.

### Q: Can I get real-time updates?

A: WebSocket support is planned for Phase 6.

Currently, poll the endpoint periodically:
```bash
while true; do
  curl http://localhost:8000/vms/vm-001
  sleep 2
done
```

---

## Deployment

### Q: How do I deploy to production?

A: See `docs/QUICKSTART.md` for 3 deployment options:
1. Docker Compose (simple)
2. Docker Swarm (medium)
3. Kubernetes (advanced)

### Q: Can I run on Kubernetes?

A: Yes! See `docs/QUICKSTART.md` for Kubernetes deployment.

Note: Persistent storage needed for mock provider state (or disable for stateless).

### Q: How do I set environment variables in production?

A: In Docker Compose:
```yaml
environment:
  - OS_CLOUD=ovh
  - LOG_LEVEL=INFO
```

In Kubernetes:
```yaml
env:
  - name: OS_CLOUD
    value: "ovh"
```

### Q: How do I secure the API?

A: See `docs/ARCHITECTURE.md` for security recommendations:
- Add OAuth2 authentication (Phase 7)
- Use HTTPS (reverse proxy: nginx, traefik)
- Add rate limiting
- Configure CORS properly
- Use secrets for credentials (not in .env)
- Enable audit logging
- Monitor and alert on suspicious activity

### Q: How do I monitor the API?

A: Check:
- Health endpoint: `GET /health`
- Logs (stdout/file)
- Docker monitoring: `docker stats`

Prometheus metrics coming in Phase 7.

### Q: Can I use multiple replicas?

A: Yes, with caveats:
- Use load balancer (nginx, HAProxy)
- Mock provider is in-memory (state not shared between replicas)
- For stateful operation, use OpenStack provider (stateless)
- For production, add shared cache (Redis)

---

## Development

### Q: How do I run tests?

A: ```bash
pytest tests/ -v
pytest --cov=api tests/  # With coverage
```

### Q: How do I add a new endpoint?

A: Follow the pattern:
1. Add route in `api/api/routes/`
2. Add schema in `api/api/schemas/`
3. Add service method in `api/services/`
4. Add tests in `tests/`
5. API docs auto-generate

See `CONTRIBUTING.md` for detailed guide.

### Q: How do I test against real OpenStack?

A: ```bash
# Configure clouds.yaml with your credentials
export OS_CLOUD=your-cloud-name
pytest tests/ -v
```

### Q: How do I add a new provider?

A: 1. Create class inheriting from `BaseProvider` in `api/providers/`
2. Implement all abstract methods
3. Register in factory: `api/providers/factory.py`
4. Add to `clouds.yaml` (if credential-based)

See `api/providers/openstack_provider.py` for example.

### Q: Where are the logs?

A: - **Local**: Printed to stdout
- **Docker**: `docker logs <container-id>`
- **Configure**: Set `LOG_LEVEL` environment variable

### Q: How do I debug the API?

A: ```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python -m uvicorn api.main:app --reload

# Or in Docker:
export LOG_LEVEL=DEBUG
docker-compose up
```

### Q: How do I debug the frontend?

A: - Browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls
- Check React DevTools extension

### Q: Can I use the API with other frontends?

A: **Absolutely!** The API is completely independent:
- Use with Postman, Insomnia, REST clients
- Build your own frontend (Vue, Angular, Svelte)
- Build CLI tools (Python, Go, Rust)
- Build mobile apps (React Native, Flutter)

### Q: Is there an SDK/client library?

A: Not yet (planned for Phase 8).

In the meantime, use:
- OpenAPI-generated clients (see `docs/API_EXAMPLES.md`)
- Official OpenStack SDK (works with any OpenStack)

---

## Troubleshooting

### Q: API won't start

A: Check logs:
```bash
docker logs <container-id>
# or locally:
python -m uvicorn api.main:app --reload
```

Common issues:
- Port already in use: `lsof -i :8000`
- Missing dependencies: `pip install -r requirements.txt`
- Wrong Python version: `python --version` (need 3.11+)

See `docs/TROUBLESHOOTING.md` for detailed solutions.

### Q: Frontend won't connect to API

A: Check:
- API is running: `curl http://localhost:8000/health`
- VITE_API_URL is set correctly
- No CORS errors in browser console
- Network requests are to correct URL

See `docs/TROUBLESHOOTING.md` for more.

### Q: Tests are failing

A: Try:
```bash
pip install -r requirements.txt  # Missing dependencies?
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Add to path
pytest tests/ -v  # Run with verbose output
```

### Q: Docker image is too large

A: Mock provider works fine for most use cases. For production, use OpenStack provider which doesn't need mock data.

Image sizes:
- Backend: ~580MB (Python 3.11-slim + dependencies)
- Frontend: ~120MB (Node.js 20 + dependencies)

### Q: Getting "Address already in use" error

A: Port is already in use:
```bash
# Find process using port
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port in docker-compose.yml
```

### Q: Something else isn't working

A: 1. Check `docs/TROUBLESHOOTING.md` - most issues are documented
2. Check GitHub issues - might be already reported
3. Enable debug logging - usually reveals the problem
4. Review logs carefully - error messages are usually helpful

---

## Contributing

### Q: How do I contribute?

A: See `CONTRIBUTING.md` for detailed guidelines.

Quick summary:
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and add tests
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

### Q: What should I work on?

A: Check:
- `docs/ROADMAP.md` - Planned features by phase
- GitHub Issues - Existing bugs/feature requests
- `CONTRIBUTING.md` - Good starting points for new contributors

### Q: How do I report bugs?

A: Open a GitHub issue with:
- Environment info (OS, Python version, etc.)
- Steps to reproduce
- Expected vs actual behavior
- Error logs
- Screenshots if relevant

### Q: Can I suggest features?

A: Yes! Open a GitHub issue with:
- Clear description of feature
- Use case / problem it solves
- Any suggestions for implementation
- Relevant links/references

### Q: What's the code style?

A: - Python: Follow PEP 8 (flake8 enforces)
- TypeScript: Prettier formatting
- Git commits: Conventional Commits (`feat:`, `fix:`, etc.)

See `CONTRIBUTING.md` for more details.

---

## Licensing & Legal

### Q: What license is this under?

A: **MIT License** - Free for commercial and personal use.

See `LICENSE` file for full text.

### Q: Can I use this in my commercial product?

A: Yes! MIT License allows:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ⚠️ Must include license notice

### Q: Is this affiliated with OpenStack?

A: No, this is an independent project. It's compatible with OpenStack (uses official SDK).

### Q: Do I need to contribute back?

A: No, MIT License doesn't require contributions back. But we appreciate contributions!

---

## Support & Community

### Q: Where do I get help?

A: - **Documentation**: `/docs` folder
- **GitHub Issues**: Bug reports and feature requests
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **This FAQ**: Answers common questions

### Q: How long will this be supported?

A: This is an open-source project maintained by the community. Support depends on community interest.

Core maintainer: Jason Afari (@jafarijason)

### Q: Can I contact the maintainer?

A: See GitHub profile for contact information. Please use GitHub Issues for public discussion.

### Q: Where can I see the roadmap?

A: See `docs/ROADMAP.md` for complete roadmap through Phase 9.

### Q: How often are releases made?

A: No fixed schedule. Releases happen when:
- Significant features are complete
- Critical bugs are fixed
- Community requests stability

### Q: Is there a changelog?

A: Yes! See `CHANGELOG.md` for all versions and changes.

---

## Still Have Questions?

- **Check Documentation**: Review `/docs` folder first
- **Search GitHub Issues**: Your question might be answered there
- **Create an Issue**: If not found, open a new GitHub issue
- **Read the Code**: Source code is the ultimate documentation

---

**Last Updated**: 2026-05-15  
**Project Version**: 0.1.0  
**FAQ Version**: 1.0
