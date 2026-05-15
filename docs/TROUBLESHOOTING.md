# Troubleshooting Guide

Common issues and solutions for the OpenStack VM Orchestrator.

## Table of Contents

- [Docker Issues](#docker-issues)
- [Backend API Issues](#backend-api-issues)
- [Frontend Issues](#frontend-issues)
- [Testing Issues](#testing-issues)
- [Deployment Issues](#deployment-issues)
- [OpenStack Provider Issues](#openstack-provider-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

---

## Docker Issues

### Issue: `docker-compose up` fails with "port already in use"

**Symptoms:**
```
Error response from daemon: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solutions:**

1. **Stop existing containers:**
   ```bash
   docker-compose down
   docker ps -a  # List all containers
   docker stop <container-id>
   docker rm <container-id>
   ```

2. **Use different ports in docker-compose:**
   ```yaml
   services:
     api:
       ports:
         - "8001:8000"  # Change 8000 to 8001
     frontend:
       ports:
         - "5175:5174"  # Change 5174 to 5175
   ```

3. **Kill process on specific port (macOS/Linux):**
   ```bash
   lsof -i :8000  # Find process
   kill -9 <PID>   # Kill it
   ```

---

### Issue: `docker-compose up` fails with "Cannot find image"

**Symptoms:**
```
Error response from daemon: pull access denied for api, repository does not exist
```

**Solution:**

Build images first:
```bash
docker-compose build
docker-compose up
```

---

### Issue: Frontend cannot connect to backend in Docker

**Symptoms:**
- Frontend shows "Failed to connect to API"
- Network requests timeout or 404
- Browser console shows CORS errors

**Root Cause:** `VITE_API_URL` environment variable not set correctly

**Solutions:**

1. **Check VITE_API_URL in frontend Dockerfile:**
   ```dockerfile
   ENV VITE_API_URL=http://api:8000
   ```

2. **Verify docker-compose networking:**
   ```bash
   docker network ls
   docker network inspect <network-name>
   ```

3. **Test from frontend container:**
   ```bash
   docker exec -it <frontend-container-id> /bin/sh
   curl http://api:8000/health
   ```

4. **Check browser Network tab:**
   - Right-click → Inspect → Network tab
   - Look at request URL (should be to `http://api:8000`)
   - Check response for CORS headers

---

### Issue: Docker containers exit immediately

**Symptoms:**
```
docker ps -a  # Shows container exited immediately
docker logs <container-id>
```

**Solutions:**

1. **Check logs:**
   ```bash
   docker logs <container-id>
   ```

2. **Common issues:**
   - Missing dependencies: Rebuild with `docker-compose build --no-cache`
   - Bad environment variables: Check `.env` file
   - Port conflict: Check other containers
   - Database connection: Mock provider doesn't need database

3. **Run with interactive mode:**
   ```bash
   docker run -it <image-name> /bin/bash
   ```

---

## Backend API Issues

### Issue: API returns 502 Bad Gateway

**Symptoms:**
```
HTTP 502 Bad Gateway
```

**Solutions:**

1. **Check if API is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API logs:**
   ```bash
   # If running locally:
   python -m uvicorn api.main:app --reload
   
   # If in Docker:
   docker logs <api-container-id>
   ```

3. **Check for startup errors:**
   ```bash
   docker-compose up --build  # Rebuild to see full output
   ```

4. **Verify port is correct:**
   ```bash
   netstat -an | grep 8000  # Linux/macOS
   netstat -ano | grep 8000 # Windows
   ```

---

### Issue: API returns 500 Internal Server Error

**Symptoms:**
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Internal Server Error"
  }
}
```

**Solutions:**

1. **Check API logs for detailed error:**
   ```bash
   docker logs <api-container-id> -f  # Follow logs
   ```

2. **Enable debug logging:**
   ```bash
   export LOG_LEVEL=DEBUG
   python -m uvicorn api.main:app --reload
   ```

3. **Test endpoint directly:**
   ```bash
   curl -v http://localhost:8000/health
   ```

4. **Check Python version compatibility:**
   ```bash
   python --version  # Should be 3.11+
   ```

---

### Issue: OpenAPI docs at `/docs` not loading

**Symptoms:**
```
404 Not Found - /docs
```

**Solutions:**

1. **Verify FastAPI is configured correctly:**
   ```python
   # In api/main.py
   app = FastAPI(docs_url="/docs")
   ```

2. **Check if API is running:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Use direct URL:**
   ```
   http://localhost:8000/docs
   http://localhost:8000/redoc
   ```

---

### Issue: API endpoint returns 404

**Symptoms:**
```
404 Not Found - /vms
```

**Solutions:**

1. **Verify endpoint exists:**
   Check `api/api/routes/vm.py` for route definition

2. **Check route prefix:**
   Routes might be under `/api/v1/` or `/` depending on configuration

3. **List all available routes:**
   ```bash
   curl http://localhost:8000/openapi.json | python -m json.tool | grep -A 2 '"paths"'
   ```

4. **Verify method (GET, POST, etc.):**
   ```bash
   # Wrong method:
   curl http://localhost:8000/vms  # GET (might work)
   
   # Correct POST:
   curl -X POST http://localhost:8000/vms \
     -H "Content-Type: application/json" \
     -d '{...}'
   ```

---

### Issue: POST request returns 422 Unprocessable Entity

**Symptoms:**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solutions:**

1. **Check required fields:**
   Review endpoint request schema
   ```python
   # Example: CreateVMRequest requires: name, image_id, flavor_id, network_ids
   ```

2. **Verify JSON format:**
   ```bash
   # Bad:
   curl -X POST http://localhost:8000/vms -d "name=test"
   
   # Good:
   curl -X POST http://localhost:8000/vms \
     -H "Content-Type: application/json" \
     -d '{"name": "test", "image_id": "img", "flavor_id": "m1.small", "network_ids": ["net"]}'
   ```

3. **Check Content-Type header:**
   ```bash
   -H "Content-Type: application/json"
   ```

4. **Use curl with `--json`:**
   ```bash
   curl --json @request.json http://localhost:8000/vms
   ```

---

### Issue: Cloud provider not found / No provider configured

**Symptoms:**
```json
{
  "error": "Cloud provider 'ovh' not found"
}
```

**Solutions:**

1. **Verify clouds.yaml exists:**
   ```bash
   cat clouds.yaml  # If not, copy example:
   cp clouds.yaml.example clouds.yaml
   ```

2. **Check OS_CLOUD environment variable:**
   ```bash
   echo $OS_CLOUD  # Should output cloud name
   export OS_CLOUD=mock  # Use mock for testing
   ```

3. **Use mock provider (recommended for testing):**
   ```bash
   export OS_CLOUD=mock
   ./run.sh
   ```

4. **Verify clouds.yaml syntax:**
   ```bash
   python -c "import yaml; print(yaml.safe_load(open('clouds.yaml')))"
   ```

---

## Frontend Issues

### Issue: Frontend shows "Failed to connect to API"

**Symptoms:**
- Error message in browser
- Console shows network errors
- API requests fail

**Solutions:**

1. **Check if API is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify VITE_API_URL environment variable:**
   ```bash
   echo $VITE_API_URL  # Should be set
   ```

3. **Check .env.local file:**
   ```
   # frontend/.env.local (NOT committed to git)
   VITE_API_URL=http://localhost:8000
   ```

4. **Check browser console for errors:**
   - Open DevTools (F12)
   - Check Console tab for error messages
   - Check Network tab for failed requests

5. **Test API directly from frontend container:**
   ```bash
   docker exec -it <frontend-container-id> \
     curl http://api:8000/health
   ```

---

### Issue: TypeScript compilation errors in frontend

**Symptoms:**
```
npm run build fails with TypeScript errors
```

**Solutions:**

1. **Regenerate types from schema:**
   ```bash
   cd frontend
   npm run generate-types
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Check for type errors:**
   ```bash
   npm run type-check  # If configured
   ```

4. **Clear node_modules and reinstall:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

---

### Issue: Frontend page shows 404 or blank

**Symptoms:**
- Blank white page
- "NotFound" page displayed
- Cannot navigate between pages

**Solutions:**

1. **Check if frontend is running:**
   ```bash
   curl http://localhost:5174
   ```

2. **Check browser console for errors:**
   - F12 → Console tab
   - Look for red error messages

3. **Verify routes are defined:**
   - Check `frontend/src/main.tsx` or `App.tsx`
   - Verify route paths match URL

4. **Check if API is accessible:**
   ```bash
   curl http://localhost:8000/vms
   ```

---

### Issue: Styles not loading (TailwindCSS not working)

**Symptoms:**
- Page looks unstyled (plain HTML)
- No colors or layout
- Appears like a broken website

**Solutions:**

1. **Rebuild Tailwind:**
   ```bash
   npm run dev  # During development
   npm run build  # For production
   ```

2. **Check tailwind.config.js:**
   Verify it includes all template paths:
   ```javascript
   content: [
     "./index.html",
     "./src/**/*.{js,ts,jsx,tsx}",
   ]
   ```

3. **Clear browser cache:**
   - Ctrl+Shift+Delete (Windows/Linux)
   - Cmd+Shift+Delete (macOS)
   - Or use DevTools → Settings → Disable cache (while open)

4. **Check for CSS import:**
   In main entry file (main.tsx or index.tsx):
   ```typescript
   import "./index.css"  // Must be imported
   ```

---

## Testing Issues

### Issue: Tests fail with "ModuleNotFoundError"

**Symptoms:**
```
ModuleNotFoundError: No module named 'api'
```

**Solutions:**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov httpx
   ```

2. **Add project to PYTHONPATH:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pytest tests/
   ```

3. **Run from project root:**
   ```bash
   cd /path/to/openstack-ovh-vm-orchestrator
   pytest tests/unit/test_services.py -v
   ```

---

### Issue: Async tests fail with "no running event loop"

**Symptoms:**
```
RuntimeError: no running event loop
```

**Solutions:**

1. **Install pytest-asyncio:**
   ```bash
   pip install pytest-asyncio
   ```

2. **Mark async tests:**
   ```python
   @pytest.mark.asyncio
   async def test_something():
       pass
   ```

3. **Update pytest.ini:**
   ```ini
   [pytest]
   asyncio_mode = auto
   ```

---

### Issue: Tests fail with "connection refused" to database

**Symptoms:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solution:**

Mock provider doesn't need database - if using OpenStack provider, ensure server is running:
```bash
export OS_CLOUD=mock  # Use mock for testing
pytest tests/
```

---

### Issue: Coverage report shows 0%

**Symptoms:**
```
TOTAL                      0%
```

**Solutions:**

1. **Verify tests are running:**
   ```bash
   pytest tests/ -v  # Should show test output
   ```

2. **Add coverage flags:**
   ```bash
   pytest --cov=api --cov-report=html tests/
   ```

3. **Check .coveragerc:**
   Should exist in project root if using custom coverage configuration

4. **View HTML report:**
   ```bash
   pytest --cov=api --cov-report=html tests/
   open htmlcov/index.html
   ```

---

## Deployment Issues

### Issue: docker-compose up hangs or takes too long

**Symptoms:**
- Runs for 5+ minutes
- Shows no progress
- Eventually times out

**Solutions:**

1. **Check network connectivity:**
   ```bash
   ping docker.io  # Verify internet
   ```

2. **Rebuild from scratch:**
   ```bash
   docker-compose down -v
   docker image rm <image-ids>
   docker-compose build --no-cache
   docker-compose up
   ```

3. **Check Docker resource limits:**
   - Docker Desktop → Preferences → Resources
   - Increase CPU and Memory if needed

4. **Pull base images manually:**
   ```bash
   docker pull python:3.11-slim
   docker pull node:20-slim
   ```

---

### Issue: "Cannot assign requested address" when accessing localhost:8000

**Symptoms:**
```
curl: (7) Failed to connect to localhost port 8000: Cannot assign requested address
```

**Solutions:**

1. **Check if service is bound to 127.0.0.1 only:**
   ```bash
   netstat -tlnp | grep 8000
   ```

2. **Use 0.0.0.0 instead of localhost in Dockerfile:**
   ```bash
   CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Try 127.0.0.1 explicitly:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

4. **In Docker, use container name:**
   ```bash
   curl http://api:8000/health  # Inside Docker
   curl http://localhost:8000/health  # From host
   ```

---

### Issue: Health check endpoint fails in Kubernetes/health check

**Symptoms:**
```
503 Service Unavailable
GET /health returns error
```

**Solutions:**

1. **Check mock provider initialization:**
   Ensure OS_CLOUD=mock is set

2. **Verify endpoint exists:**
   ```bash
   curl http://localhost:8000/health -v
   ```

3. **Check for startup errors:**
   Review container logs during startup

---

## OpenStack Provider Issues

### Issue: "Invalid OpenStack credentials"

**Symptoms:**
```
AuthenticationError: Invalid credentials
```

**Solutions:**

1. **Verify clouds.yaml format:**
   ```bash
   cat clouds.yaml | head -20
   ```

2. **Set correct OS_CLOUD:**
   ```bash
   export OS_CLOUD=ovh  # Or whatever your cloud name is
   echo $OS_CLOUD
   ```

3. **Test credentials manually:**
   ```bash
   openstack --os-cloud=ovh server list
   ```

4. **Check environment variables:**
   ```bash
   env | grep OS_  # Should show your OpenStack vars
   ```

---

### Issue: "Unable to establish connection" to OpenStack

**Symptoms:**
```
ConnectionError: Unable to establish connection to OpenStack endpoint
```

**Solutions:**

1. **Verify endpoint URL in clouds.yaml:**
   ```bash
   cat clouds.yaml | grep auth_url
   ```

2. **Test endpoint connectivity:**
   ```bash
   curl -I https://your-openstack-endpoint:5000/v3
   ```

3. **Check network access:**
   ```bash
   ping your-openstack-host
   traceroute your-openstack-host
   ```

4. **Verify SSL certificates (if HTTPS):**
   ```bash
   python -c "import ssl; print(ssl.get_default_verify_paths())"
   ```

---

### Issue: "Token expired" errors during operations

**Symptoms:**
```
AuthenticationError: Token has expired
```

**Solutions:**

1. **Token is automatically refreshed by SDK** - this is normal
2. **If persists, regenerate clouds.yaml:**
   ```bash
   rm clouds.yaml
   cp clouds.yaml.example clouds.yaml
   # Update with fresh credentials
   ```

3. **Check token expiration:**
   OpenStack tokens expire after ~24 hours

---

## Performance Issues

### Issue: API requests very slow (>2 seconds)

**Symptoms:**
- List endpoints take >2 seconds
- Create operations timeout
- High latency

**Solutions:**

1. **Check if using mock provider (should be <50ms):**
   ```bash
   export OS_CLOUD=mock
   time curl http://localhost:8000/vms
   ```

2. **If using OpenStack provider:**
   - Network latency to OpenStack cloud
   - Cloud may be overloaded
   - Check OpenStack logs: `openstack server list --debug`

3. **Check local system resources:**
   ```bash
   top  # Check CPU/Memory
   iostat  # Check disk I/O
   ```

4. **Enable timing in curl:**
   ```bash
   curl -w "@curl-format.txt" http://localhost:8000/vms
   ```

---

### Issue: Memory usage increasing over time

**Symptoms:**
- Container memory usage grows
- Eventually gets OOMKilled
- Memory leak suspected

**Solutions:**

1. **Monitor memory:**
   ```bash
   docker stats  # Live monitoring
   ```

2. **Check for memory leaks in Python:**
   ```bash
   pip install memory-profiler
   python -m memory_profiler api/main.py
   ```

3. **Check for unbounded caches:**
   Review any cache implementations in code

4. **Increase container memory limit:**
   ```yaml
   services:
     api:
       mem_limit: 512m
   ```

---

## Getting Help

### Before Creating an Issue

1. **Check this troubleshooting guide** - Most common issues are here
2. **Check existing GitHub issues** - Your problem might be already reported
3. **Review logs carefully** - Error messages often contain the solution
4. **Test with mock provider** - Isolate if issue is with OpenStack or your setup

### Creating a Detailed Bug Report

When creating an issue on GitHub, include:

```markdown
**Environment:**
- OS: (Windows/macOS/Linux)
- Docker: (version)
- Python: (version if running locally)
- Python packages: (output of `pip freeze`)

**Steps to reproduce:**
1. ...
2. ...
3. ...

**Expected behavior:**
...

**Actual behavior:**
...

**Logs/Error messages:**
```
(paste full error output)
```

**Screenshots:**
(if GUI related)
```

### Support Resources

- **GitHub Issues**: https://github.com/jafarijason/openstack-ovh-vm-orchestrator/issues
- **Documentation**: See `/docs` folder
- **API Examples**: See `docs/API_EXAMPLES.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Contributing**: See `CONTRIBUTING.md`

### Community

- Report issues professionally
- Search before posting (avoid duplicates)
- Include reproduction steps
- Include relevant logs/screenshots
- Be patient - maintainers respond when available

---

**Last Updated**: 2026-05-15  
**Version**: 0.1.0
