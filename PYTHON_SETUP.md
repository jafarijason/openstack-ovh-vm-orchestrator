# Python Setup Guide

## Problem: Multiple Python Installations

The OpenStack VM Orchestrator requires openstacksdk for OpenStack/OVH cloud support. On systems with multiple Python installations (e.g., Homebrew + asdf), this can cause issues if openstacksdk is installed in one environment but the backend uses a different Python interpreter.

### The Issue
- **Symptom**: `ModuleNotFoundError: No module named 'openstack'`
- **Root Cause**: openstacksdk installed in asdf Python, but backend runs with Homebrew Python
- **Result**: OVH cloud appears unavailable, mock cloud works fine

## Solution

### Option 1: Use asdf Python (Recommended)

If you have asdf installed with Python 3.13.12, the run.sh script will automatically use it:

```bash
# Simply run as usual
./run.sh

# The script will automatically:
# 1. Check if asdf is available
# 2. Use asdf Python if found
# 3. Fall back to system python3 otherwise
```

**Why this works:**
- openstacksdk is already installed in asdf Python
- asdf Python is specified in `.tool-versions`
- No additional setup needed

### Option 2: Use Virtual Environment (Best Practice)

For long-term development, use Python virtual environments:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
./run.sh
```

### Option 3: Reinstall in Homebrew Python

If you prefer Homebrew Python, create a virtual environment first (Homebrew 3.4.0+ requires this):

```bash
# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install openstacksdk
pip install openstacksdk==4.12.0

# Run backend
./run.sh
```

## Checking Your Setup

### Verify Python Version
```bash
python3 --version
# Expected: Python 3.13.x
```

### Verify openstacksdk is Installed
```bash
python3 -c "import openstack; print('✅ openstacksdk is available')"
```

### Verify Backend Starts Correctly
```bash
# In one terminal
./run.sh

# In another terminal (after 5 seconds)
curl http://localhost:8000/health/cloud/ovh
# Expected: {"status":"healthy","cloud":"ovh","connected":true}
```

## Understanding the Fix

The `run.sh` script has been updated to intelligently select Python:

```bash
# Use asdf Python if available, otherwise fall back to python3
PYTHON_CMD="python"
if command -v asdf &> /dev/null; then
    PYTHON_CMD="$(asdf which python)"
fi

# Run with the correct Python
$PYTHON_CMD -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Python Versions Tested

- ✅ Python 3.13.12 (asdf)
- ✅ Python 3.13.7 (Homebrew) with venv
- ✅ Python 3.13.x in general

## Troubleshooting

### Still Getting "ModuleNotFoundError: No module named 'openstack'"?

1. **Check which Python is running:**
   ```bash
   which python3
   # Should be: /opt/homebrew/bin/python3 or ~/.asdf/shims/python
   ```

2. **Check Python sys.path:**
   ```bash
   python3 -c "import sys; print('\n'.join(sys.path))"
   # Look for site-packages containing openstacksdk
   ```

3. **Reinstall openstacksdk:**
   ```bash
   python3 -m pip install --force-reinstall openstacksdk==4.12.0
   ```

4. **Use a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### OVH Cloud Still Shows as Unavailable?

1. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health/cloud/ovh | python3 -m json.tool
   ```

2. **Check backend logs:**
   ```bash
   # Look for error messages about OpenStack connection
   # They should appear on stdout
   ```

3. **Verify clouds.yaml:**
   ```bash
   # Should have both mock and ovh clouds
   cat clouds.yaml
   ```

4. **Restart backend:**
   ```bash
   pkill -f "uvicorn api.main"
   ./run.sh
   ```

## Requirements

- Python 3.13.x (3.12.x should also work)
- openstacksdk 4.12.0+
- All dependencies in requirements.txt

## See Also

- [AGENTS.md](./AGENTS.md) - Development guidelines
- [DEBUG.md](./DEBUG.md) - Debugging guide
- [OVH_SETUP.md](./OVH_SETUP.md) - OVH cloud configuration

---

**Last Updated:** 2026-05-15

