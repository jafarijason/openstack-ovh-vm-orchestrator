# Cloud Provider Configuration

This project supports multiple cloud providers through a flexible configuration system. Clouds are defined in `clouds.yaml` and can be switched via environment variables.

## Quick Start

### Using Mock Provider (Default - No Credentials Required)

The mock provider is perfect for development and testing:

```bash
# Start with mock provider (default)
./run.sh

# Or explicitly
OS_CLOUD=mock python -m uvicorn app.main:app --reload --port 8000
```

Mock provider runs entirely in-memory with no external dependencies or credentials needed.

### Checking Available Clouds

```bash
curl http://localhost:8000/clouds
```

Response:
```json
{
  "success": true,
  "active_cloud": "mock",
  "clouds": {
    "mock": {
      "type": "mock",
      "authenticated": false,
      "default": true
    },
    "ovh": {
      "type": "openstack",
      "authenticated": true,
      "default": false
    }
  }
}
```

## Configuration

### Creating clouds.yaml

1. Copy the example file:
```bash
cp clouds.yaml.example clouds.yaml
```

2. Edit `clouds.yaml` with your cloud credentials:

```yaml
clouds:
  # Mock provider - for testing
  mock:
    auth_type: none
    _provider_type: mock

  # OVH Public Cloud
  ovh:
    auth:
      auth_url: https://auth.cloud.ovh.net/v3
      application_credential_id: YOUR_APP_CRED_ID
      application_credential_secret: YOUR_APP_CRED_SECRET
    region_name: SBG5
    interface: public
    identity_api_version: "3"
    volume_api_version: "3"

  # Generic OpenStack
  openstack:
    auth:
      auth_url: https://openstack.example.com/v3
      username: user
      password: pass
      project_name: project
      user_domain_name: Default
      project_domain_name: Default
    region_name: RegionOne
    interface: public
```

### Switching Between Clouds

Use the `OS_CLOUD` environment variable:

```bash
# Use OVH cloud
OS_CLOUD=ovh ./run.sh

# Use mock cloud
OS_CLOUD=mock ./run.sh

# Default (first configured cloud)
./run.sh
```

## Supported Cloud Types

### Mock Provider
- **Best for**: Development, testing, CI/CD
- **Credentials**: None required
- **Storage**: In-memory (data lost on restart)
- **Cost**: Free
- **Setup time**: None

### OpenStack Provider
- **Best for**: Production use with real clouds
- **Credentials**: Cloud authentication required
- **Storage**: Persistent on cloud
- **Cost**: Pay-as-you-go
- **Setup time**: 5-10 minutes

## Cloud Logging

The application logs which clouds are configured and which is active at startup:

```
INFO:app.main:Available clouds: ['mock', 'ovh']
INFO:app.main:  - mock: mock (authenticated=False)
INFO:app.main:  - ovh: openstack (authenticated=True)
INFO:app.main:Initializing infrastructure provider...
INFO:app.providers.factory:Creating provider for cloud: mock
INFO:app.providers.factory:Initializing Mock provider
INFO:app.main:Services initialized successfully using cloud: default
```

## Cloud Health Status

Check if a cloud is healthy:

```bash
curl http://localhost:8000/health
```

Response includes the active cloud:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "active_cloud": "mock",
  "message": "OpenStack VM Orchestrator API is running"
}
```

## Using with OVH Cloud

1. Create application credentials in OVH Control Panel
2. Add to `clouds.yaml`:
```yaml
ovh:
  auth:
    auth_url: https://auth.cloud.ovh.net/v3
    application_credential_id: YOUR_ID
    application_credential_secret: YOUR_SECRET
  region_name: SBG5  # or your preferred region
  interface: public
  identity_api_version: "3"
  volume_api_version: "3"
```
3. Switch to OVH:
```bash
OS_CLOUD=ovh ./run.sh
```

## Available OVH Regions

- `SBG1`, `SBG3`, `SBG5` - Strasbourg, France
- `BHS1`, `BHS3` - Beauharnois, Canada
- `GRA1` - Gravelines, France
- `WAW1` - Warsaw, Poland
- `SYD1` - Sydney, Australia
- `DE1` - Nuremberg, Germany

## Troubleshooting

### "clouds.yaml not found"
Make sure you have created `clouds.yaml` from `clouds.yaml.example`

### "No cloud configured"
Add clouds to `clouds.yaml` or set `OS_CLOUD` environment variable

### "Cloud connection failed"
Check your credentials and network connectivity:
```bash
# Test specific cloud
OS_CLOUD=ovh python -m uvicorn app.main:app --reload
```

### "Module 'openstack' not found"
Install openstacksdk:
```bash
pip install openstacksdk
```

## Best Practices

1. **Development**: Use `mock` provider
2. **Testing**: Use `mock` provider
3. **Staging**: Use test cloud with real credentials
4. **Production**: Use production cloud with secure credentials
5. **CI/CD**: Use `mock` provider in pipelines for speed

## Security

- Never commit `clouds.yaml` with real credentials
- Use environment variables for sensitive data
- Rotate application credentials regularly
- Use separate credentials for dev/staging/prod
