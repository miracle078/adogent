"""
ADOGENT FastAPI Application
AI-powered e-commerce platform with voice interface and intelligent recommendations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.config import settings
from app.api import health, auth, users, products, recommendations

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered e-commerce platform with voice interface and intelligent product recommendations using Groq API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initialize database connections and other resources.
    """
    # TODO: Initialize database tables
    # TODO: Initialize Groq client
    # TODO: Load AI models if needed
    
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    Clean up resources.
    """
    print(f"🛑 {settings.APP_NAME} shutting down...")


# Health check endpoint
@app.get("/ping", tags=["Health"])
async def ping():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Include API routers


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "description": "AI-powered e-commerce platform with voice interface",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": "/ping"
    }
