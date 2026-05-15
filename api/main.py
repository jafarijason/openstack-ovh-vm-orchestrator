"""
OpenStack VM Orchestrator API

Main FastAPI application entry point for VM lifecycle management.
"""

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from api.api.routes.vm import router as vm_router
from api.api.routes.volume import router as volume_router, snapshot_router
from api.services.vm_service import VMService
from api.services.volume_service import VolumeService
from api.providers.factory import create_provider, list_available_clouds
from api.core.exceptions import OrchestratorException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances (will be initialized on startup)
vm_service: VMService | None = None
volume_service: VolumeService | None = None
active_cloud: str | None = None  # Track which cloud is currently active


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """
    Manage application lifespan: startup and shutdown.
    
    Startup:
        - Initialize provider and services
        - Save OpenAPI schema to schema.json
        - Initialize application resources
    
    Shutdown:
        - Cleanup resources
    """
    # Startup
    global vm_service, volume_service, active_cloud
    
    try:
        startup_time = datetime.utcnow().isoformat()
        logger.info(f"[{startup_time}] OpenStack VM Orchestrator API starting...")
        
        # List available clouds
        available_clouds = list_available_clouds()
        logger.info(f"Available clouds: {list(available_clouds.keys())}")
        for cloud_name, cloud_info in available_clouds.items():
            logger.info(f"  - {cloud_name}: {cloud_info['type']} (authenticated={cloud_info['authenticated']})")
        
        # Initialize provider from clouds.yaml
        logger.info("Initializing infrastructure provider...")
        cloud_name = os.environ.get("OS_CLOUD")
        provider = create_provider(cloud_name=cloud_name)
        active_cloud = cloud_name or "default"
        
        # Initialize services
        vm_service = VMService(provider)
        volume_service = VolumeService(provider)
        logger.info(f"Services initialized successfully using cloud: {active_cloud}")
        
        # Store in app state
        fast_app.state.vm_service = vm_service
        fast_app.state.volume_service = volume_service
        
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
        
        logger.info(f"OpenAPI schema saved to {schema_path}")
        logger.info(f"[{startup_time}] OpenStack VM Orchestrator API started")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    # Yield control to application
    yield
    
    # Shutdown
    shutdown_time = datetime.utcnow().isoformat()
    logger.info(f"[{shutdown_time}] OpenStack VM Orchestrator API shutting down")


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


# Exception handlers
@app.exception_handler(OrchestratorException)
async def orchestrator_exception_handler(request: Request, exc: OrchestratorException):
    """Handle orchestrator exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "status_code": exc.status_code,
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "status_code": 422,
                "details": exc.errors(),
            },
        },
    )


# Include routers
app.include_router(vm_router)
app.include_router(volume_router)
app.include_router(snapshot_router)


# Cloud status endpoint
@app.get("/clouds")
async def get_clouds_status():
    """
    Get status of all configured clouds.
    
    Returns:
        dict: Available clouds and current active cloud
    """
    try:
        available_clouds = list_available_clouds()
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "active_cloud": active_cloud,
                "clouds": available_clouds,
                "message": f"Currently using cloud: {active_cloud}",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "CLOUD_CONFIG_ERROR",
                    "message": f"Error reading cloud configuration: {str(e)}",
                    "status_code": 500,
                },
            },
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
            "active_cloud": active_cloud,
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
        "active_cloud": active_cloud,
        "docs_url": "/docs",
        "endpoints": {
            "clouds": "/clouds",
            "health": "/health",
            "vms": "/vms",
            "volumes": "/volumes",
            "snapshots": "/snapshots",
        },
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
