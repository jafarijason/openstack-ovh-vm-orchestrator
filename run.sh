#!/bin/bash

# OpenStack VM Orchestrator - Run Script

set -e

echo "🚀 Starting OpenStack VM Orchestrator API..."
echo ""
echo "📦 Environment:"
echo "   Python: $(python --version 2>&1)"
echo "   FastAPI: $(python -c 'import fastapi; print(fastapi.__version__)')"
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

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
