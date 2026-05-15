# OVH OpenStack Cloud Setup & Configuration Guide

## Overview

The OpenStack VM Orchestrator now fully supports OVH Public Cloud with comprehensive error handling and diagnostics.

## Prerequisites

1. **openstacksdk**: Installed ✅
   ```bash
   pip install openstacksdk==4.12.0
   ```

2. **OVH Account**: Active OVH Public Cloud account
3. **Valid Credentials**: Username, password, and project details

---

## Configuration

### Step 1: Get Your OVH Credentials

**Via OVH Public Cloud Console:**

1. Log into [OVH Public Cloud Console](https://ca.ovh.com/auth/?action=gotomanager)
2. Go to Public Cloud → Your Project → Users & Roles
3. Create a new user or use existing credentials
4. Note:
   - **Username**: Format `user-XXXXXXXXX`
   - **Password**: Strong password
   - **Project ID**: Found in Project Settings
   - **Region**: SBG5, BHS3, GRA1, etc.

### Step 2: Update `clouds.yaml`

Edit `clouds.yaml` with your credentials:

```yaml
ovh:
  auth:
    auth_url: https://auth.cloud.ovh.net/v3
    username: user-YOUR_USERNAME
    password: YOUR_PASSWORD
    project_name: YOUR_PROJECT_ID
    user_domain_name: Default          # Important!
    project_domain_name: Default       # Important!
  
  region_name: SBG5  # Change to your region
  interface: public
  identity_api_version: "3"
  volume_api_version: "3"
```

**Critical Settings:**
- `user_domain_name: Default` - Required for Keystone v3
- `project_domain_name: Default` - Required for Keystone v3
- These prevent "Expecting to find domain in project" errors

---

## Testing Configuration

### Endpoint 1: Cloud Health Check (NEW!)

Test if you can connect to OVH:

```bash
curl http://localhost:8000/health/cloud/ovh
```

**Success Response:**
```json
{
    "status": "healthy",
    "cloud": "ovh",
    "connected": true,
    "message": "Successfully connected to ovh cloud"
}
```

**Error Response (with diagnostics):**
```json
{
    "status": "unhealthy",
    "cloud": "ovh",
    "connected": false,
    "error_code": "MISSING_DOMAIN",
    "error": "...",
    "solution": "Add domain configuration to clouds.yaml: user_domain_name or project_domain_name",
    "troubleshooting": { ... }
}
```

### Endpoint 2: List Clouds

See all configured clouds and their status:

```bash
curl http://localhost:8000/clouds
```

**Response:**
```json
{
    "clouds": {
        "mock": {
            "type": "mock",
            "authenticated": false,
            "available": true,
            "error": null
        },
        "ovh": {
            "type": "openstack",
            "authenticated": true,
            "available": true,
            "error": null
        }
    }
}
```

### Endpoint 3: List VMs on OVH

```bash
curl http://localhost:8000/vms?cloud=ovh
```

Works just like mock cloud!

---

## Common Errors & Solutions

### Error 1: Missing Dependencies

**Error Message:**
```
"Cannot connect to ovh cloud"
"solution": "Install required packages: pip install openstacksdk"
```

**Solution:**
```bash
pip install openstacksdk
```

### Error 2: Domain Not Found

**Error Message:**
```
"error_code": "MISSING_DOMAIN"
"error": "Expecting to find domain in project"
```

**Solution:** Add to `clouds.yaml`:
```yaml
ovh:
  auth:
    user_domain_name: Default
    project_domain_name: Default
```

### Error 3: Authentication Failed (401)

**Error Message:**
```
"error_code": "AUTHENTICATION_FAILED"
"error": "401: Unauthorized"
```

**Solution:** Check credentials in `clouds.yaml`:
- Verify username format: `user-XXXXXXXXX`
- Verify password is correct
- Verify project_name matches OVH console
- Reset password in OVH console if needed

### Error 4: Invalid Project

**Error Message:**
```
"error_code": "INVALID_PROJECT"
"error": "Project not found"
```

**Solution:**
- Verify `project_name` in `clouds.yaml`
- Get project ID from OVH Console → Project Settings

### Error 5: Connection Error

**Error Message:**
```
"error_code": "CONNECTION_ERROR"
"error": "Connection refused"
```

**Solution:**
- Verify `auth_url`: `https://auth.cloud.ovh.net/v3`
- Check internet connection
- Verify firewall allows outbound HTTPS

---

## Health Check Endpoint Details

New endpoint: `GET /health/cloud/{cloud_name}`

### What It Does:
1. Creates provider for specified cloud
2. Attempts to connect using stored credentials
3. Returns detailed status and diagnostics
4. Provides solutions for common errors

### Error Codes:

| Code | Meaning | Solution |
|------|---------|----------|
| `AUTHENTICATION_FAILED` | Invalid credentials | Check username/password |
| `MISSING_DOMAIN` | Missing domain config | Add user_domain_name, project_domain_name |
| `INVALID_PROJECT` | Project ID incorrect | Verify project_name |
| `BAD_REQUEST` | Configuration error | Check all auth settings |
| `SERVICE_NOT_FOUND` | Auth URL unreachable | Verify auth_url and region |
| `CONNECTION_ERROR` | Network error | Check firewall/connectivity |

---

## OVH Regions

Available regions for `region_name` in `clouds.yaml`:

```
SBG1, SBG3, SBG5  - Strasbourg, France
BHS1, BHS3        - Beauharnois, Canada  
GRA1              - Gravelines, France
WAW1              - Warsaw, Poland
DE1               - Nuremberg, Germany
SYD1              - Sydney, Australia
SIN1              - Singapore
```

---

## Best Practices

### 1. Secure Credentials

- **Never commit credentials** to git
- Use `.gitignore`:
  ```
  clouds.yaml
  *.credentials
  .env
  ```

- Consider using environment variables:
  ```bash
  export OS_CLOUD=ovh
  export OS_AUTH_URL=https://auth.cloud.ovh.net/v3
  export OS_USERNAME=user-XXX
  export OS_PASSWORD=xxx
  ```

### 2. Test Connectivity First

Always test health check before using endpoints:

```bash
# Test OVH connection
curl http://localhost:8000/health/cloud/ovh

# If healthy, test VMs
curl http://localhost:8000/vms?cloud=ovh
```

### 3. Monitoring

Check `/health` periodically:

```bash
# General health
curl http://localhost:8000/health

# OVH specific
curl http://localhost:8000/health/cloud/ovh
```

---

## Troubleshooting Checklist

- [ ] openstacksdk installed: `pip list | grep openstacksdk`
- [ ] clouds.yaml has valid syntax (YAML format)
- [ ] OVH username format: `user-XXXXXXXXX` (not email)
- [ ] user_domain_name: `Default`
- [ ] project_domain_name: `Default`
- [ ] project_name matches OVH console
- [ ] region_name is valid: `SBG5`, `BHS1`, etc.
- [ ] auth_url: `https://auth.cloud.ovh.net/v3`
- [ ] Test health check: `/health/cloud/ovh`
- [ ] Test with mock cloud first to verify setup
- [ ] Backend can reach auth URL (no firewall blocks)

---

## Testing Workflow

```bash
# 1. Start backend
./run.sh

# 2. Test mock cloud
curl http://localhost:8000/vms?cloud=mock

# 3. Test OVH health
curl http://localhost:8000/health/cloud/ovh

# 4. If healthy, test OVH VMs
curl http://localhost:8000/vms?cloud=ovh

# 5. Use in UI
# Open http://localhost:5173
# Cloud picker shows ovh as available ✓
```

---

## Multi-Cloud Management

Switch between clouds in UI dropdown:

```
Cloud Picker:
├─ mock ✓ (Development)
└─ ovh  ✓ (Production)
```

Frontend automatically:
- Sends `?cloud=` parameter to API
- Clears old data when switching
- Shows error if cloud unavailable
- Disables unavailable clouds

---

## Production Checklist

- [ ] openstacksdk installed on production server
- [ ] clouds.yaml secured (restricted permissions)
- [ ] Credentials in environment variables (not in file)
- [ ] Health checks passing for all clouds
- [ ] Error handling tested for common failures
- [ ] Network access verified to OVH auth URL
- [ ] Backup/disaster recovery plan
- [ ] Monitoring/alerting on `/health` endpoints

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Overall API health |
| `/health/cloud/{name}` | GET | Specific cloud health with diagnostics |
| `/clouds` | GET | List all configured clouds |
| `/vms?cloud=ovh` | GET | List VMs on OVH |
| `/volumes?cloud=ovh` | GET | List volumes on OVH |
| `/snapshots?cloud=ovh` | GET | List snapshots on OVH |

---

## Support & Documentation

- **OpenStack SDK**: https://docs.openstack.org/openstacksdk/
- **OVH API**: https://docs.ovh.com/us/en/public-cloud/
- **Keystone Auth**: https://docs.openstack.org/keystone/latest/

---

**Your OVH cloud is now fully configured and ready!** 🚀
