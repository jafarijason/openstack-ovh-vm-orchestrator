"""
OpenStack VM Orchestrator API

Main FastAPI application entry point for VM lifecycle management.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI(
    title="OpenStack VM Orchestrator",
    description="REST API for managing OpenStack VM lifecycle operations",
    version="0.1.0",
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
        "redoc_url": "/redoc",
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
