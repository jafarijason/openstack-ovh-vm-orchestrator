# Agent Instructions for OpenStack VM Orchestrator

This document provides instructions for AI agents and developers working on this project. It includes guidelines for working with both backend and frontend components.

## Project Overview

**OpenStack VM Orchestrator** is a REST API for managing OpenStack virtual machine lifecycle operations. It provides:

- Multi-cloud support (Mock provider for testing, OpenStack for production)
- Complete VM management (create, list, get, delete, start, stop, reboot)
- Volume management (create, list, attach, detach, delete)
- Snapshot management (create, list, delete)
- Flexible provider abstraction layer
- Type-safe async endpoints
- Comprehensive error handling

## Backend Development

### Project Structure

```
project-root/
├── api/                           # Main API package
│   ├── main.py                    # FastAPI application entry
│   ├── api/                       # HTTP layer
│   │   ├── routes/               # Endpoint definitions
│   │   │   ├── vm.py            # VM endpoints
│   │   │   └── volume.py        # Volume & Snapshot endpoints
│   │   └── schemas/             # Pydantic request/response models
│   │       ├── common.py        # Common response wrappers
│   │       ├── vm.py            # VM schemas
│   │       └── volume.py        # Volume/Snapshot schemas
│   ├── core/                      # Core business logic
│   │   ├── config.py            # Cloud configuration loader
│   │   ├── exceptions.py        # Custom exception hierarchy
│   │   └── models.py            # Domain models
│   ├── engine/                    # Cloud SDK wrapper
│   │   └── openstack_engine.py  # OpenStack SDK integration
│   ├── providers/                 # Infrastructure abstraction
│   │   ├── base.py              # Abstract provider interface
│   │   ├── factory.py           # Provider factory pattern
│   │   ├── mock_provider.py     # In-memory test provider
│   │   └── openstack_provider.py # Real OpenStack provider
│   ├── services/                  # Business logic layer
│   │   ├── vm_service.py        # VM service operations
│   │   └── volume_service.py    # Volume service operations
│   └── utils/                     # Utility functions
├── frontend/                      # Frontend application (Vue.js/React)
│   ├── public/                   # Static assets
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client services
│   │   ├── stores/              # State management
│   │   ├── styles/              # Global styles
│   │   └── App.vue              # Root component
│   ├── package.json             # Frontend dependencies
│   └── vite.config.js           # Frontend build config
├── schema.json                    # OpenAPI 3.1.0 schema (AUTO-GENERATED)
├── clouds.yaml                    # Cloud configuration
├── clouds.yaml.example            # Configuration template
├── run.sh                         # Backend quick-start script
├── requirements.txt               # Python dependencies
└── docs/
    ├── ARCHITECTURE.md           # Design patterns
    ├── ROADMAP.md               # Development roadmap
    └── README.md                # Project README
```

### Working with the Backend

#### Running the API

```bash
# Using the quick-start script
./run.sh

# Or manually
python -m uvicorn api.main:app --reload --port 8000

# With specific cloud
OS_CLOUD=mock ./run.sh
OS_CLOUD=ovh ./run.sh
```

#### Making Changes

1. **Adding a new endpoint:**
   - Create route in `api/api/routes/`
   - Define request/response schemas in `api/api/schemas/`
   - Add service method in `api/services/`
   - Schema is auto-generated on startup

2. **Modifying domain models:**
   - Update `api/core/models.py`
   - Update corresponding schemas in `api/api/schemas/`
   - Add service methods if needed

3. **Adding exception types:**
   - Add to `api/core/exceptions.py`
   - Map to HTTP status code
   - Update error handlers in `api/main.py` if needed

#### Testing the API

```bash
# Check API is running
curl http://localhost:8000/health

# Check available clouds
curl http://localhost:8000/clouds

# Create a VM
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "image_id": "img-001", "flavor_id": "m1.small", "network_ids": ["net-001"]}'

# List VMs
curl http://localhost:8000/vms

# Interactive API docs
# Open: http://localhost:8000/docs
```

---

## Frontend Development

### 🚀 Quick Start: Using schema.json

The **`schema.json`** file is your blueprint for the frontend. It's automatically generated on backend startup and contains the complete OpenAPI 3.1.0 specification.

**File Location:** `schema.json` (root directory)

**Key Points:**
- ✅ Auto-generated from API code
- ✅ Always up-to-date with backend
- ✅ Contains all endpoints, request/response types
- ✅ Use to generate frontend types and API client

### Creating the Frontend

#### Step 1: Generate API Types from schema.json

**Recommended Tool:** `openapi-typescript` (fastest)

```bash
cd frontend

# Install code generator
npm install -D openapi-typescript

# Generate types from schema.json
npx openapi-typescript ../schema.json -o src/types/api.ts
```

This creates `frontend/src/types/api.ts` with all TypeScript types:

```typescript
// Auto-generated from schema.json
export interface VMResponse {
  id: string
  name: string
  status: "BUILDING" | "ACTIVE" | "STOPPED" | "REBOOTING" | "DELETING" | "ERROR" | "UNKNOWN"
  image_id: string
  flavor_id: string
  network_ids: string[]
  attached_volumes: string[]
  key_name: string | null
  security_groups: string[]
  metadata: Record<string, unknown>
  created_at: string | null
  updated_at: string | null
}

export interface CreateVMRequest {
  name: string
  image_id: string
  flavor_id: string
  network_ids: string[]
  key_name?: string | null
  security_groups?: string[]
  metadata?: Record<string, unknown>
}

export interface SuccessResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface ErrorResponse {
  success: boolean
  error: {
    code: string
    message: string
    status_code: number
  }
}

// ... All other types from schema.json
```

#### Step 2: Create API Service Layer

**File:** `frontend/src/services/vmService.ts`

Use the generated types:

```typescript
import type { VMResponse, CreateVMRequest, SuccessResponse } from "@/types/api"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

export const vmService = {
  async listVMs(limit = 100, offset = 0): Promise<SuccessResponse<VMResponse[]>> {
    const response = await fetch(
      `${API_BASE}/vms?limit=${limit}&offset=${offset}`
    )
    if (!response.ok) throw new Error("Failed to list VMs")
    return response.json()
  },

  async getVM(vmId: string): Promise<SuccessResponse<VMResponse>> {
    const response = await fetch(`${API_BASE}/vms/${vmId}`)
    if (!response.ok) throw new Error("Failed to fetch VM")
    return response.json()
  },

  async createVM(data: CreateVMRequest): Promise<SuccessResponse<VMResponse>> {
    const response = await fetch(`${API_BASE}/vms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to create VM")
    return response.json()
  },

  async deleteVM(vmId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/vms/${vmId}`, {
      method: "DELETE",
    })
    if (!response.ok) throw new Error("Failed to delete VM")
  },

  async performAction(vmId: string, action: "start" | "stop" | "reboot") {
    const response = await fetch(`${API_BASE}/vms/${vmId}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    })
    if (!response.ok) throw new Error(`Failed to ${action} VM`)
    return response.json()
  },
}
```

#### Step 3: Create UI Components

**File:** `frontend/src/pages/VmList.vue`

Use typed service and generated types:

```vue
<template>
  <div class="vm-list">
    <div class="header">
      <h1>Virtual Machines</h1>
      <button @click="showCreateForm = true" class="btn-primary">
        Create VM
      </button>
    </div>

    <div v-if="loading" class="loading">
      <LoadingSpinner />
    </div>

    <div v-else-if="error" class="error">
      <ErrorAlert :message="error" />
    </div>

    <div v-else class="vm-grid">
      <VmCard
        v-for="vm in vms"
        :key="vm.id"
        :vm="vm"
        @delete="deleteVM"
        @start="startVM"
        @stop="stopVM"
        @reboot="rebootVM"
      />
    </div>

    <CreateVmModal
      v-if="showCreateForm"
      @create="createVM"
      @close="showCreateForm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import type { VMResponse } from "@/types/api"
import { vmService } from "@/services/vmService"
import VmCard from "@/components/resources/VmCard.vue"
import CreateVmModal from "@/components/resources/CreateVmModal.vue"
import LoadingSpinner from "@/components/common/LoadingSpinner.vue"
import ErrorAlert from "@/components/common/ErrorAlert.vue"

const vms = ref<VMResponse[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const showCreateForm = ref(false)

onMounted(async () => {
  try {
    const response = await vmService.listVMs()
    vms.value = response.data
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to load VMs"
  } finally {
    loading.value = false
  }
})

const createVM = async (data) => {
  try {
    await vmService.createVM(data)
    showCreateForm.value = false
    const response = await vmService.listVMs()
    vms.value = response.data
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to create VM"
  }
}

const deleteVM = async (vmId: string) => {
  if (confirm("Are you sure?")) {
    try {
      await vmService.deleteVM(vmId)
      vms.value = vms.value.filter((vm) => vm.id !== vmId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to delete VM"
    }
  }
}

const startVM = async (vmId: string) => {
  try {
    const response = await vmService.performAction(vmId, "start")
    const vm = response.data as VMResponse
    const index = vms.value.findIndex((v) => v.id === vmId)
    if (index !== -1) vms.value[index] = vm
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to start VM"
  }
}

// Similar for stopVM and rebootVM
</script>

<style scoped>
.vm-list {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.vm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.loading,
.error {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>
```

### Frontend Architecture

#### Recommended Tech Stack

- **Framework:** Vue 3 (Composition API) or React 18+
- **State Management:** Pinia (Vue) or Zustand (React)
- **HTTP Client:** fetch API or axios
- **UI Framework:** TailwindCSS or Material UI
- **Build Tool:** Vite
- **TypeScript:** Required for type safety

#### Frontend Folder Structure

```
frontend/
├── public/                        # Static files
├── src/
│   ├── components/
│   │   ├── common/              # Reusable components
│   │   │   ├── Button.vue
│   │   │   ├── Modal.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   └── ErrorAlert.vue
│   │   ├── layout/              # Layout components
│   │   │   ├── Header.vue
│   │   │   ├── Sidebar.vue
│   │   │   └── Footer.vue
│   │   └── resources/           # Resource components
│   │       ├── VmCard.vue
│   │       ├── VmForm.vue
│   │       ├── VolumeCard.vue
│   │       └── SnapshotCard.vue
│   ├── pages/
│   │   ├── Dashboard.vue        # Home page
│   │   ├── VmList.vue           # VM list page
│   │   ├── VmDetail.vue         # VM detail page
│   │   ├── VolumeList.vue       # Volume list page
│   │   ├── SettingsPage.vue     # Settings page
│   │   └── NotFound.vue         # 404 page
│   ├── services/
│   │   ├── vmService.ts        # VM API calls (use VMResponse type)
│   │   ├── volumeService.ts    # Volume API calls
│   │   └── cloudService.ts     # Cloud API calls
│   ├── stores/
│   │   ├── vmStore.ts          # VM state management
│   │   ├── volumeStore.ts      # Volume state management
│   │   └── cloudStore.ts       # Cloud state management
│   ├── types/
│   │   └── api.ts              # GENERATED from schema.json
│   ├── styles/
│   │   ├── globals.css
│   │   └── variables.css
│   ├── App.vue                 # Root component
│   └── main.ts                 # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### Setting Up Frontend Development

#### Step 1: Initialize Project

```bash
# Create frontend folder
mkdir frontend
cd frontend

# Initialize with Vite
npm create vite@latest . -- --template vue-ts

# Or with React
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
```

#### Step 2: Install Required Packages

```bash
# Type generation
npm install -D openapi-typescript

# HTTP client (optional, can use fetch)
npm install axios

# State management
npm install pinia
```

#### Step 3: Generate Types from schema.json

```bash
# From frontend directory
npx openapi-typescript ../schema.json -o src/types/api.ts

# Add to package.json scripts:
"generate-types": "openapi-typescript ../schema.json -o src/types/api.ts"
```

#### Step 4: Configure Environment

**File:** `frontend/.env.development`
```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

**File:** `frontend/vite.config.ts`
```typescript
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import path from "path"

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

#### Step 5: Update package.json

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "generate-types": "openapi-typescript ../schema.json -o src/types/api.ts"
  }
}
```

### Frontend Pages to Implement

Use schema.json to understand required endpoints:

1. **Dashboard** (`/`)
   - System status overview
   - Quick stats (VM count, Volume count)
   - Active cloud display
   - Recent activity

2. **VMs Page** (`/vms`)
   - List all VMs with pagination
   - Create VM button → modal form
   - VM cards with actions (start, stop, reboot, delete)
   - Filter/search VMs
   - VM detail page

3. **Volumes Page** (`/volumes`)
   - List all volumes with pagination
   - Create volume button → modal form
   - Volume cards with actions
   - Attach/detach volume dialog
   - Delete confirmation

4. **Snapshots Page** (`/snapshots`)
   - List all snapshots
   - Create snapshot button → modal form
   - Delete snapshots
   - Link to source volume

5. **Settings Page** (`/settings`)
   - Active cloud display
   - Available clouds list
   - Health check status
   - API endpoint info

6. **Navigation**
   - Header with branding
   - Sidebar/nav menu
   - Cloud selector
   - Health status indicator

---

## Development Workflow

### Running Both Backend and Frontend

**Terminal 1: Start Backend**
```bash
./run.sh
```

**Terminal 2: Start Frontend**
```bash
cd frontend
npm install  # First time only
npm run generate-types  # When schema changes
npm run dev
```

**Open in Browser:**
- Frontend: http://localhost:5173 (Vite default)
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Updating Types After Backend Changes

```bash
# Backend: Make changes to models or endpoints
# Backend: Restart server (auto-generates schema.json)

# Frontend: Regenerate types
cd frontend
npm run generate-types

# Frontend: Components now have updated types!
```

### Testing Workflow

```bash
# 1. Test endpoint manually
curl -X POST http://localhost:8000/vms \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "image_id": "img-001", "flavor_id": "m1.small", "network_ids": ["net-001"]}'

# 2. Check schema.json has the endpoint
curl http://localhost:8000/openapi.json | python -m json.tool | grep -A 5 "your-endpoint"

# 3. Regenerate frontend types
npm run generate-types

# 4. Use in component
import type { YourNewType } from "@/types/api"
```

---

## Common Tasks for Agents

### Adding a New Feature (Full Stack)

**Backend:**
1. Create domain model in `api/core/models.py`
2. Create request/response schemas in `api/api/schemas/`
3. Add service method in `api/services/`
4. Create route in `api/api/routes/`
5. Restart backend → `schema.json` auto-updates

**Frontend:**
1. Run `npm run generate-types` (generates types from updated schema.json)
2. Create service function in `frontend/src/services/`
3. Create UI component in `frontend/src/components/`
4. Add page/route if needed
5. Test with real API

### Changing API Response Format

**Backend:**
1. Update schema in `api/api/schemas/`
2. Update service response in `api/services/`
3. Restart backend → new schema.json

**Frontend:**
1. Run `npm run generate-types` (auto-updates from schema.json)
2. Components automatically get new types!
3. TypeScript will error if you're using old field names
4. Fix errors → Done!

### Adding Error Handling

**Backend:**
1. Create exception in `api/core/exceptions.py`
2. Add handler in `api/main.py`
3. Restart → schema.json includes error response

**Frontend:**
1. Service layer catches errors
2. Display error to user in component
3. Use error response type from schema.json

---

## Understanding schema.json

### What It Contains

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "OpenStack VM Orchestrator",
    "version": "0.1.0",
    "description": "REST API for managing OpenStack VM lifecycle"
  },
  "servers": [
    {"url": "http://localhost:8000"}
  ],
  "paths": {
    "/vms": {
      "get": { /* GET /vms endpoint */ },
      "post": { /* POST /vms endpoint */ }
    },
    "/vms/{vm_id}": {
      "get": { /* GET /vms/{vm_id} endpoint */ },
      "delete": { /* DELETE /vms/{vm_id} endpoint */ }
    },
    "/volumes": { /* ... */ },
    "/snapshots": { /* ... */ },
    "/clouds": { /* ... */ },
    "/health": { /* ... */ }
  },
  "components": {
    "schemas": {
      "VMResponse": { /* VM data structure */ },
      "CreateVMRequest": { /* Create VM params */ },
      "VolumeResponse": { /* Volume data structure */ },
      "SuccessResponse": { /* Success wrapper */ },
      "ErrorResponse": { /* Error wrapper */ }
      /* ... more types ... */
    }
  }
}
```

### Using It for Code Generation

**Generate Types:**
```bash
npx openapi-typescript schema.json -o api-types.ts
```

**Generate Full API Client (advanced):**
```bash
docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
  -i /local/schema.json \
  -g typescript-fetch \
  -o /local/frontend/src/generated-api
```

---

## Tips for Developers and AI Agents

✅ **Do:**
- Use schema.json as the source of truth for types
- Regenerate frontend types when backend changes
- Test backend endpoints before building UI
- Keep services simple - they call the API
- Keep components focused on UI
- Use TypeScript types from schema.json
- Handle all error cases
- Display errors to users

❌ **Don't:**
- Hardcode API URLs (use environment variables)
- Use `any` type in TypeScript
- Forget to regenerate types after backend changes
- Build UI before having working API endpoint
- Mix API logic with UI components
- Ignore error responses from API
- Commit credentials to repository

---

## Resources

- **Backend OpenAPI Schema:** `schema.json` (root directory, auto-generated)
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Cloud Configuration:** `CLOUDS.md`
- **Architecture Documentation:** `docs/ARCHITECTURE.md`
- **Development Roadmap:** `docs/ROADMAP.md`
- **TypeScript OpenAPI Generator:** https://openapi-ts.dev/
- **Vite Documentation:** https://vitejs.dev/
- **Vue 3 Documentation:** https://vuejs.org/
- **Pinia State Management:** https://pinia.vuejs.org/

---

**Last Updated:** 2026-05-15
