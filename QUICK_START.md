# Quick Start Guide

## 30-Second Startup

```bash
# Terminal 1: Start Backend
./run.sh

# Terminal 2: Test API (after 5 seconds)
curl http://localhost:8000/health
```

Expected output: `{"status":"healthy",...}`

## Verify Both Clouds Work

```bash
# Check both clouds are available
curl http://localhost:8000/clouds

# Test OVH cloud
curl http://localhost:8000/health/cloud/ovh
curl "http://localhost:8000/vms?cloud=ovh"

# Test Mock cloud
curl http://localhost:8000/health/cloud/mock
curl "http://localhost:8000/vms?cloud=mock"
```

All should return HTTP 200 with success data.

## API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Backend Commands

```bash
# Start backend (development)
./run.sh

# With debugpy (for debugging in IDE)
./run_debug.sh
# Then F5 in VS Code → "Attach Debugpy to Backend (Port 5162)"

# Stop backend
pkill -f "uvicorn api.main"
```

## Frontend Setup

```bash
# First time only
cd frontend
npm install
npm run generate-types

# Start frontend dev server
npm run dev
```

Open: http://localhost:5173

## Troubleshooting

### Backend won't start?

Check Python:
```bash
python3 -c "import openstack; print('✅ OK')"
```

If error, see [PYTHON_SETUP.md](./PYTHON_SETUP.md)

### OVH cloud shows as unavailable?

Verify clouds.yaml has credentials:
```bash
cat clouds.yaml | grep -A 10 "^clouds:"
```

See [OVH_SETUP.md](./OVH_SETUP.md) for details.

### Need to debug?

See [DEBUG.md](./DEBUG.md) for full debugging guide.

## Common Endpoints

| Method | Endpoint | Cloud | Description |
|--------|----------|-------|-------------|
| GET | `/health` | - | API health check |
| GET | `/clouds` | - | List available clouds |
| GET | `/health/cloud/{cloud}` | both | Cloud connection test |
| GET | `/vms?cloud={cloud}` | both | List VMs |
| GET | `/volumes?cloud={cloud}` | both | List volumes |
| GET | `/snapshots?cloud={cloud}` | both | List snapshots |
| GET | `/docs` | - | API documentation |

## System Status

✅ Mock cloud - Working (for testing)
✅ OVH cloud - Working (production)
✅ All endpoints - Tested and verified
✅ Health checks - Active
✅ Documentation - Complete

## What's Fixed

- ✅ openstacksdk import error
- ✅ OVH cloud now connects successfully
- ✅ Both clouds fully operational
- ✅ All API endpoints working

## Next Steps

1. **Start backend**: `./run.sh`
2. **Test it works**: `curl http://localhost:8000/health`
3. **View API docs**: http://localhost:8000/docs
4. **Continue development**: Follow [AGENTS.md](./AGENTS.md)

---

For detailed setup, see [README.md](./README.md) and [AGENTS.md](./AGENTS.md)
