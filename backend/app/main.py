"""
ADOGENT FastAPI Application
AI-powered e-commerce platform with voice interface and intelligent recommendations.
"""

import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid

from app.config.config import settings
from app.api import auth
from app.logging.log import logger, log_api_request, log_user_action


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    logger.info(f"📊 Logging initialized - JSON structured logging enabled")
    logger.info(f"📁 Log directory: {getattr(settings, 'LOG_DIR', 'logs')}")
    
    # Test logging with different levels
    logger.debug("Debug logging test message")
    logger.info("Info logging test message")
    logger.warning("Warning logging test message")
    logger.error("Error logging test message")
    
    # Log application startup
    log_user_action(
        action="application_startup",
        user_id="system",
        details={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG
        }
    )
    
    yield
    
    # Shutdown
    logger.info(f"🛑 {settings.APP_NAME} shutting down...")
    log_user_action(
        action="application_shutdown",
        user_id="system",
        details={"app_name": settings.APP_NAME}
    )


# Create FastAPI application with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered e-commerce platform with voice interface and intelligent product recommendations using Groq API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)


# Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware to log all HTTP requests and responses.
    """
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Get request details
    method = request.method
    url = str(request.url)
    endpoint = request.url.path
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host if request.client else "unknown"
    
    # Start timer
    start_time = time.time()
    
    # Log request start
    logger.info(
        f"Request started: {method} {endpoint}",
        extra={
            "request_id": request_id,
            "method": method,
            "endpoint": endpoint,
            "url": url,
            "user_agent": user_agent,
            "client_ip": client_ip,
            "event_type": "request_start"
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log successful response
        log_api_request(
            method=method,
            endpoint=endpoint,
            status_code=response.status_code,
            response_time=response_time,
            request_id=request_id
        )
        
        logger.info(
            f"Request completed: {method} {endpoint} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time": response_time,
                "event_type": "request_complete"
            }
        )
        
        return response
        
    except Exception as e:
        # Calculate response time for errors
        response_time = time.time() - start_time
        
        # Log error
        logger.error(
            f"Request failed: {method} {endpoint} - {str(e)}",
            extra={
                "request_id": request_id,
                "method": method,
                "endpoint": endpoint,
                "response_time": response_time,
                "error": str(e),
                "event_type": "request_error"
            },
            exc_info=True
        )
        
        raise


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/ping", tags=["Health"])
async def ping():
    """Simple health check endpoint."""
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }


# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}"
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    logger.info("Root endpoint accessed")
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "description": "AI-powered e-commerce platform with voice interface",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": "/ping",
        "endpoints": {
            "auth": f"{settings.API_V1_PREFIX}/auth",
            "docs": f"{settings.API_V1_PREFIX}/docs",
            "health": "/ping"
        }
    }


# Log files check endpoint (for development)
@app.get("/logs/status", tags=["Development"])
async def logs_status():
    """
    Check logging status and file creation.
    """
    import os
    from pathlib import Path
    
    log_dir = Path(getattr(settings, 'LOG_DIR', 'logs'))
    
    status = {
        "logging_enabled": True,
        "log_directory": str(log_dir),
        "log_directory_exists": log_dir.exists(),
        "log_files": []
    }
    
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        for log_file in log_files:
            file_stats = log_file.stat()
            status["log_files"].append({
                "name": log_file.name,
                "size": file_stats.st_size,
                "modified": file_stats.st_mtime,
                "path": str(log_file)
            })
    
    logger.info("Log status check performed", extra={"log_status": status})
    return status