"""
OpenStack VM Orchestrator API

Main FastAPI application entry point for VM lifecycle management.
"""

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """
    Manage application lifespan: startup and shutdown.
    
    Startup:
        - Save OpenAPI schema to schema.json
        - Initialize application resources
    
    Shutdown:
        - Cleanup resources
    """
    # Startup
    try:
        # Generate OpenAPI schema
        openapi_schema = fast_app.openapi()
        
        # Determine schema file path
        schema_dir = os.environ.get("SERVICE_CURRENT_DIR", "")
        schema_path = (
            os.path.join(schema_dir, "schema.json")
            if schema_dir
            else "schema.json"
        )
        
        # Ensure directory exists
        schema_dir_path = os.path.dirname(schema_path)
        if schema_dir_path and not os.path.exists(schema_dir_path):
            os.makedirs(schema_dir_path, exist_ok=True)
        
        # Save schema to file
        with open(schema_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)
        
        startup_time = datetime.utcnow().isoformat()
        print(f"[{startup_time}] OpenAPI schema saved to {schema_path}")
        print(f"[{startup_time}] OpenStack VM Orchestrator API started")
        
    except (IOError, OSError, json.JSONDecodeError) as e:
        print(f"Error saving OpenAPI schema: {e}")
    
    # Yield control to application
    yield
    
    # Shutdown
    shutdown_time = datetime.utcnow().isoformat()
    print(f"[{shutdown_time}] OpenStack VM Orchestrator API shutting down")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="OpenStack VM Orchestrator",
    description="REST API for managing OpenStack VM lifecycle operations",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,  # Disable ReDoc
    openapi_url="/openapi.json",
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Health status
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": "0.1.0",
            "message": "OpenStack VM Orchestrator API is running",
        },
    )


# Hello World endpoint
@app.get("/")
async def hello_world():
    """
    Hello World endpoint to verify basic functionality.
    
    Returns:
        dict: Welcome message
    """
    return {
        "message": "Hello World! OpenStack VM Orchestrator API",
        "status": "running",
        "api_version": "0.1.0",
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
