# Quick Start Guide: OpenStack VM Orchestrator

Get the full-stack application running in minutes.

## Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **npm or yarn** (for frontend package management)

## Quick Start (2 Terminals)

### Terminal 1: Start Backend API

```bash
# From project root
./run.sh
```

The backend will start on **http://localhost:8000**

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Available clouds: {'mock': {'type': 'mock', 'authenticated': True}}
INFO:     Services initialized successfully
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "version": "0.1.0", ...}
```

**View API Documentation:**
Open http://localhost:8000/docs in your browser

---

### Terminal 2: Start Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install --legacy-peer-deps

# Start development server
npm run dev
```

The frontend will start on **http://localhost:5173**

**Expected output:**
```
VITE v8.0.13  ready in 250 ms

➜  Local:   http://localhost:5173/
```

---

## Accessing the Application

1. **Frontend UI:** http://localhost:5173
2. **Backend API:** http://localhost:8000
3. **API Documentation:** http://localhost:8000/docs
4. **OpenAPI Schema:** http://localhost:8000/openapi.json

---

## Common Commands

### Backend

```bash
# Run with mock cloud (default)
./run.sh

# Run with specific cloud
OS_CLOUD=mock ./run.sh
OS_CLOUD=ovh ./run.sh

# Manual run with uvicorn
python -m uvicorn api.main:app --reload --port 8000

# View API docs
curl http://localhost:8000/docs

# Health check
curl http://localhost:8000/health

# List clouds
curl http://localhost:8000/clouds
```

### Frontend

```bash
# Install dependencies
npm install --legacy-peer-deps

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Regenerate API types from schema.json
npm run generate-types

# Type checking
npm run tsc
```

---

## Troubleshooting

### CORS Errors

**Problem:** XMLHttpRequest CORS policy error
```
Access to XMLHttpRequest at 'http://localhost:8000/clouds' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Solution:** Backend CORS middleware is configured for:
- `http://localhost:5173` ✓
- `http://localhost:3000` ✓
- `http://127.0.0.1:5173` ✓

**Note:** Restart backend if you get this error after updating

### API Types Not Found

**Problem:** TypeScript errors about missing API types
```
error TS2305: Module '"@/types/api"' has no exported member 'VMResponse'
```

**Solution:** Regenerate types from schema.json
```bash
cd frontend
npm run generate-types
```

### Port Already in Use

**Backend port 8000 in use:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m uvicorn api.main:app --reload --port 8001
```

**Frontend port 5173 in use:**
```bash
# Vite will suggest alternative port automatically
# Or manually specify:
npm run dev -- --port 3000
```

### Dependencies Issues

**Frontend dependencies conflict:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**Backend dependencies:**
```bash
pip install -r requirements.txt
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React 18)                       │
│                   http://localhost:5173                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pages: Dashboard, VMs, Volumes, Snapshots, Settings │   │
│  │  Components: Charts, Cards, Forms, Modals           │   │
│  │  State: Zustand stores (vm, volume, snapshot, cloud) │   │
│  └────────────────┬─────────────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      │ HTTP/REST + CORS
                      │ (localhost:5173 allowed)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│                 http://localhost:8000                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Routes: /vms, /volumes, /snapshots, /clouds, /health│   │
│  │  Services: VMService, VolumeService                  │   │
│  │  Providers: MockProvider, OpenStackProvider          │   │
│  │  Engine: OpenStackEngine (SDK wrapper)               │   │
│  └────────────────┬─────────────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      │ OpenStack SDK / Mock Provider
                      │
                      ▼
        ┌──────────────────────────┐
        │  OpenStack Cloud (OVH)   │
        │  or Mock Provider (Test) │
        └──────────────────────────┘
```

---

## File Structure

```
├── api/                           # Backend
│   ├── main.py                   # FastAPI app entry
│   ├── api/
│   │   ├── routes/              # Endpoints
│   │   │   ├── vm.py
│   │   │   └── volume.py
│   │   └── schemas/             # Pydantic models
│   ├── services/                # Business logic
│   ├── providers/               # Infrastructure abstraction
│   └── core/                    # Models, config, exceptions
│
├── frontend/                      # Frontend
│   ├── src/
│   │   ├── pages/               # Route pages
│   │   ├── components/          # Reusable components
│   │   ├── services/            # API clients
│   │   ├── stores/              # Zustand state
│   │   └── types/               # Generated API types
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── schema.json                    # Generated OpenAPI spec
├── run.sh                         # Backend quick-start
├── requirements.txt               # Python deps
└── QUICKSTART.md                 # This file
```

---

## Next Steps

### 1. Explore the Application
- Create VMs in the Dashboard
- Manage volumes and snapshots
- Check cloud configuration in Settings

### 2. Development
- Add new features following the AGENTS.md guide
- Regenerate types when backend changes: `npm run generate-types`
- Frontend automatically hot-reloads on changes

### 3. Testing
- Test backend endpoints via http://localhost:8000/docs
- Test frontend UI at http://localhost:5173

### 4. Deployment
- See AGENTS.md for Docker and production setup
- Build frontend: `npm run build`
- Deploy frontend to static hosting
- Deploy backend to production server

---

## Useful Links

- **Frontend Development:** See `AGENTS.md` → "Frontend Development"
- **Backend Development:** See `AGENTS.md` → "Backend Development"
- **Cloud Configuration:** See `CLOUDS.md`
- **API Documentation:** http://localhost:8000/docs (after starting backend)
- **Architecture Patterns:** See `docs/ARCHITECTURE.md`

---

## Health Check

Verify everything is working:

```bash
# Backend health
curl http://localhost:8000/health

# Frontend is accessible
curl http://localhost:5173

# API is accessible from frontend (no CORS errors)
# Open browser console at http://localhost:5173 and check
```

---

**Ready to get started? Run these commands in order:**

```bash
# Terminal 1
./run.sh

# Terminal 2
cd frontend
npm install --legacy-peer-deps
npm run dev

# Then open http://localhost:5173 in your browser
```
