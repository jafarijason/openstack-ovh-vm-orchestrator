# OpenStack VM Orchestrator - Frontend

A modern React 18+ TypeScript frontend for managing OpenStack virtual machines and cloud infrastructure.

## Features

- **Dashboard**: Real-time overview of VM statistics and status
- **VM Management**: Create, list, start, stop, reboot, and delete virtual machines
- **Volume Management**: Manage persistent block storage (coming soon)
- **Snapshots**: Create and manage volume snapshots (coming soon)
- **Settings**: Cloud configuration and API health status
- **Type Safety**: Fully typed with auto-generated types from backend schema.json

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (http://localhost:8000)

## Project Structure

```
frontend/
├── public/                    # Static assets
├── src/
│   ├── components/
│   │   ├── common/           # Reusable UI components
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorAlert.tsx
│   │   └── layout/           # Layout components
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── pages/                # Page components
│   │   ├── Dashboard.tsx
│   │   ├── VmList.tsx
│   │   ├── VolumeList.tsx
│   │   ├── SnapshotList.tsx
│   │   ├── Settings.tsx
│   │   └── NotFound.tsx
│   ├── services/             # API services
│   │   ├── api.ts           # Axios configuration
│   │   ├── vmService.ts     # VM API operations
│   │   └── cloudService.ts  # Cloud API operations
│   ├── stores/              # Zustand state management
│   │   └── cloudStore.ts
│   ├── styles/              # Global styles
│   │   └── globals.css
│   ├── types/               # Generated TypeScript types
│   │   └── api.ts           # Auto-generated from schema.json
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── index.html               # HTML template
├── package.json
├── tailwind.config.js       # Tailwind CSS configuration
├── postcss.config.js        # PostCSS configuration
├── tsconfig.json            # TypeScript configuration
└── vite.config.ts           # Vite configuration
```

## Installation

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Generate API types from backend schema:

```bash
npm run generate-types
```

This command reads the `schema.json` file from the project root and generates TypeScript types in `src/types/api.ts`.

## Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Environment Variables

Create a `.env.development` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

## Building

Build for production:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run generate-types` - Regenerate TypeScript types from schema.json

## Technologies Used

- **React 18+** - UI library
- **TypeScript** - Type safety
- **React Router v6** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Build tool and dev server

## API Integration

### Type Generation

Types are automatically generated from the backend's `schema.json` using `openapi-typescript`.

When the backend API changes:

1. Restart the backend (it auto-generates `schema.json`)
2. Run `npm run generate-types` in the frontend
3. Components now have updated types automatically

### Services Layer

All API calls go through service modules in `src/services/`:

- `vmService.ts` - VM operations (create, list, delete, start, stop, reboot)
- `cloudService.ts` - Cloud status and health checks
- `api.ts` - Axios instance with global interceptors

### State Management

Cloud configuration state is managed with Zustand in `src/stores/cloudStore.ts`:

```typescript
import { useCloudStore } from '@/stores/cloudStore';

const { activeCloud, activeClouds, healthStatus, fetchCloudsStatus } = useCloudStore();
```

## Features in Detail

### Dashboard

- VM count statistics (Total, Active, Stopped, Error)
- Recent VMs table
- Real-time status overview

### VM Management (VmList)

**Create VM:**
- Modal form with validation
- Required fields: Name, Image ID, Flavor ID, Network IDs
- Optional fields: SSH Key, Security Groups

**VM Actions:**
- **Start**: Start a stopped VM
- **Stop**: Stop a running VM
- **Reboot**: Reboot a running VM
- **Delete**: Remove a VM with confirmation

**Status Indicators:**
- ACTIVE (green)
- STOPPED (orange)
- BUILDING (blue)
- ERROR (red)

### Settings

- Active cloud display
- Available clouds list
- API health status
- API endpoint configuration
- Application information

## Error Handling

- Global error alerts in UI
- Service layer error handling
- Axios response interceptors for common errors
- User-friendly error messages

## Performance

- Lazy component loading with React Router
- Optimized re-renders with proper state management
- Memoization where needed
- Loading states for all async operations

## Styling

Using **Tailwind CSS** with utility classes:

- Responsive design (mobile-first)
- Dark mode support (via class)
- Custom component classes in `globals.css`
- Consistent color scheme

## Troubleshooting

### API Connection Issues

1. Verify backend is running: `http://localhost:8000/health`
2. Check `VITE_API_URL` in `.env.development`
3. Check browser console for CORS errors
4. Ensure backend is accessible from your local network

### Type Generation Errors

1. Verify `schema.json` exists in project root
2. Ensure backend is running and schema is generated
3. Run `npm run generate-types` again

### Build Errors

1. Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf .vite`
3. Check TypeScript errors: `npx tsc --noEmit`

## Contributing

When adding new features:

1. Create page in `src/pages/`
2. Create services in `src/services/` if needed
3. Use generated types from `src/types/api.ts`
4. Add route in `src/App.tsx`
5. Update sidebar navigation in `src/components/layout/Sidebar.tsx`

## Testing the API

### Via Frontend

1. Navigate to VmList page
2. Click "Create VM"
3. Fill in the form with mock data
4. Submit and observe results

### Via cURL

```bash
# List VMs
curl http://localhost:8000/vms

# Get health status
curl http://localhost:8000/health

# Get clouds status
curl http://localhost:8000/clouds
```

## Next Steps

- Implement Volume management page
- Implement Snapshot management page
- Add VM detail page with advanced configuration
- Add batch operations
- Add search and filtering
- Add authentication/authorization
- Add user preferences/settings storage
- Add notifications/alerts system

## Support

For issues or questions, refer to the main project README at the project root.

## License

See LICENSE in project root.
