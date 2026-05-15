# OVH Region Configuration Fix

## The Issue

When listing VMs from OVH cloud, you might get a 500 error:

```json
{
  "detail": {
    "code": "CLOUD_OPERATION_ERROR",
    "message": "Cloud operation 'list_vms' failed: public endpoint for compute service in BHS region not found"
  }
}
```

## Root Cause

OVH region names must be **full region codes**, not abbreviated codes.

### ❌ Wrong (Doesn't Work)
```yaml
region_name: BHS    # Too short
region_name: SBG    # Too short
region_name: GRA    # Too short
```

### ✅ Correct (Works)
```yaml
region_name: SBG5   # Full code
region_name: BHS3   # Full code
region_name: GRA1   # Full code
```

## Solution

Update your `clouds.yaml` to use the full region code:

```yaml
clouds:
  ovh:
    auth:
      auth_url: https://auth.cloud.ovh.net/v3
      username: YOUR_USERNAME
      password: YOUR_PASSWORD
      project_name: YOUR_PROJECT_ID
      user_domain_name: Default
      project_domain_name: Default
    
    region_name: SBG5  # Changed from: BHS → SBG5
    interface: public
    identity_api_version: "3"
    volume_api_version: "3"
```

## Available OVH Regions

| Code | Location | Notes |
|------|----------|-------|
| SBG1 | Strasbourg, France | Legacy region |
| SBG3 | Strasbourg, France | Legacy region |
| **SBG5** | **Strasbourg, France** | **Recommended - Default** |
| BHS1 | Beauharnois, Canada | |
| BHS3 | Beauharnois, Canada | |
| GRA1 | Gravelines, France | |
| WAW1 | Warsaw, Poland | |
| SGP1 | Singapore | |
| SYD1 | Sydney, Australia | |
| NYC1 | New York, USA | |

## How to Find Your Region

1. Log into [OVH Public Cloud Console](https://ca.ovh.com/manager/public-cloud/)
2. Select your project
3. Go to **Compute → Instances** or **Storage → Object Storage**
4. Look at the instances/storage - the region code is shown (e.g., SBG5)

Alternatively, check your project settings for the default region.

## Testing the Fix

After updating `clouds.yaml`:

```bash
# Restart backend
pkill -f "uvicorn api.main"
./run.sh

# Test OVH cloud (should now work)
curl http://localhost:8000/health/cloud/ovh
curl "http://localhost:8000/vms?cloud=ovh"
```

Expected response (200 OK):
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "total": 0,
    "page": 1,
    "per_page": 100,
    "pages": 0
  }
}
```

## Why This Happens

OVH has multiple datacenters across different regions. The Keystone endpoint registry stores endpoints for specific region codes. When you provide an abbreviated code (BHS), OpenStack SDK can't find the matching endpoint and returns "endpoint not found".

Full codes (BHS3, SBG5, etc.) map directly to endpoints in the registry.

## Prevention

- Always use full region codes when configuring OpenStack
- Check the [OVH documentation](https://docs.ovh.com/us/en/public-cloud/first-steps-with-openstack-api/)
- Verify region in OVH console before setting in config

## Related Issues

- **Similar Error**: "public endpoint for service X in region Y not found"
- **Cause**: Always invalid or unavailable region code
- **Solution**: Always use the full region code from OVH console

---

See [OVH_SETUP.md](./OVH_SETUP.md) for complete OVH configuration guide.
