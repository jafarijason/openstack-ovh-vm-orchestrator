#!/bin/bash

# OpenStack VM Orchestrator - Run Script

set -e

# Use asdf Python if available, otherwise fall back to python3
PYTHON_CMD="python"
if command -v asdf &> /dev/null; then
    PYTHON_CMD="$(asdf which python)"
fi

echo "🚀 Starting OpenStack VM Orchestrator API..."
echo ""
echo "📦 Environment:"
echo "   Python: $($PYTHON_CMD --version 2>&1)"
echo "   FastAPI: $($PYTHON_CMD -c 'import fastapi; print(fastapi.__version__)')"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  No virtual environment detected."
    echo "   Recommended: python3 -m venv .venv && source .venv/bin/activate"
    echo ""
fi

# Run the application
echo "🔥 Starting server on http://0.0.0.0:8000"
echo "📚 API Documentation:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""

$PYTHON_CMD -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
