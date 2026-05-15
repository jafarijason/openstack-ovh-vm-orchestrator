"""
OpenStack VM Orchestrator API

Main FastAPI application entry point for VM lifecycle management.
"""

# ============================================================================
# DEBUGPY - Attach debugger at startup
# ============================================================================
import debugpy

port = 5162
debugpy.listen(("localhost", port))
print(f"\n[DEBUG] Debugpy listening on localhost:{port}")
print(f"[DEBUG] Waiting for debugger to attach...")
# debugpy.wait_for_client()
print(f"[DEBUG] Debugger attached!")
# ============================================================================

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api.api.routes.vm import router as vm_router
from api.api.routes.image import router as image_router
from api.api.routes.flavor import router as flavor_router
from api.api.routes.ssh_key import router as ssh_key_router
from api.services.vm_service import VMService
from api.services.image_service import ImageService
from api.services.flavor_service import FlavorService
from api.services.ssh_key_service import SSHKeyService
from api.providers.factory import create_provider, list_available_clouds
from api.core.exceptions import OrchestratorException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances (will be initialized on startup)
vm_service: VMService | None = None
image_service: ImageService | None = None
flavor_service: FlavorService | None = None
ssh_key_service: SSHKeyService | None = None
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
    global vm_service, image_service, flavor_service, ssh_key_service, active_cloud
    
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
        
        # Get the actual active cloud name from configuration
        from api.core.config import get_clouds_config
        clouds_config = get_clouds_config()
        default_cloud = clouds_config.get_default()
        active_cloud = cloud_name or (default_cloud.name if default_cloud else "default")
        
        # Initialize services
        vm_service = VMService(provider)
        image_service = ImageService(provider)
        flavor_service = FlavorService(provider)
        ssh_key_service = SSHKeyService(provider)
        logger.info(f"Services initialized successfully using cloud: {active_cloud}")
        
        # Store in app state
        fast_app.state.vm_service = vm_service
        fast_app.state.image_service = image_service
        fast_app.state.flavor_service = flavor_service
        fast_app.state.ssh_key_service = ssh_key_service
        fast_app.state.active_cloud = active_cloud
        
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


# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",      # Alternative dev port
        "http://127.0.0.1:5173",      # localhost alternative
        "http://127.0.0.1:3000",      # localhost alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(image_router)
app.include_router(flavor_router)
app.include_router(ssh_key_router)


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
        },
    }


# Cloud Health Check endpoint
@app.get("/health/cloud/{cloud_name}")
async def cloud_health_check(cloud_name: str):
    """
    Check if a specific cloud can be connected to.
    
    This endpoint tests the actual connection to a cloud provider
    to ensure credentials are valid and the service is reachable.
    
    Args:
        cloud_name: Name of the cloud to check (e.g., 'ovh', 'mock')
    
    Returns:
        dict: Cloud health status with connection details
    """
    try:
        # Create provider for the cloud
        provider = create_provider(cloud_name=cloud_name)
        
        # Try to check connection
        is_connected = await provider.check_connection()
        
        if is_connected:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "healthy",
                    "cloud": cloud_name,
                    "connected": True,
                    "message": f"Successfully connected to {cloud_name} cloud",
                },
            )
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "cloud": cloud_name,
                    "connected": False,
                    "message": f"Could not verify connection to {cloud_name} cloud",
                    "error": "Connection verification failed",
                },
            )
    
    except ImportError as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "cloud": cloud_name,
                "connected": False,
                "message": f"Cannot connect to {cloud_name} cloud",
                "error": "Missing dependencies",
                "details": str(e),
                "solution": "Install required packages: pip install openstacksdk",
            },
        )
    
    except Exception as e:
        error_str = str(e)
        
        # Provide specific solutions based on error type
        solution = "Check your cloud configuration in clouds.yaml"
        error_code = "UNKNOWN_ERROR"
        
        if "401" in error_str or "Unauthorized" in error_str:
            error_code = "AUTHENTICATION_FAILED"
            solution = "Check your credentials (username, password, application credentials)"
        elif "domain" in error_str.lower():
            error_code = "MISSING_DOMAIN"
            solution = "Add domain configuration to clouds.yaml: user_domain_name or project_domain_name"
        elif "project" in error_str.lower():
            error_code = "INVALID_PROJECT"
            solution = "Verify project_name in clouds.yaml is correct"
        elif "400" in error_str or "Bad Request" in error_str:
            error_code = "BAD_REQUEST"
            solution = "Check auth configuration - may be missing domain, user_domain_name, or project_domain_name"
        elif "404" in error_str or "Not Found" in error_str:
            error_code = "SERVICE_NOT_FOUND"
            solution = "Check auth_url in clouds.yaml and verify region_name"
        elif "Connection" in error_str:
            error_code = "CONNECTION_ERROR"
            solution = "Check if OpenStack/OVH cloud is reachable at the auth_url"
        
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "cloud": cloud_name,
                "connected": False,
                "message": f"Cannot connect to {cloud_name} cloud",
                "error_code": error_code,
                "error": error_str,
                "solution": solution,
                "cloud_config_file": "clouds.yaml",
                "troubleshooting": {
                    "step1": "Check if openstacksdk is installed: pip install openstacksdk",
                    "step2": "Verify credentials in clouds.yaml",
                    "step3": "Check cloud configuration: curl http://localhost:8000/clouds",
                    "step4": "Test auth_url is reachable",
                    "step5": "Verify user_domain_name and project_domain_name for Keystone v3",
                },
            },
        )


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
