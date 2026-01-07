"""
Travel Platform - Main FastAPI Application
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.core.config.settings import settings
from src.core.logging import setup_logging
from src.database.connection import Database
from src.database.redis_client import redis_client

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    
    try:
        # Initialize database
        await Database.connect()
        logger.info("✅ Database connected")
        
        # Initialize Redis
        await redis_client.initialize()
        logger.info("✅ Redis connected")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down application...")
    await Database.disconnect()
    await redis_client.close()
    logger.info("✅ Clean shutdown completed")

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "status": "running",
        "docs": "/docs" if settings.APP_ENV != "production" else None,
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "database": "unknown",
            "redis": "unknown",
        }
    }
    
    try:
        # Check database
        db_health = await Database.health_check()
        health_status["services"]["database"] = "healthy" if db_health.get("status") == "healthy" else "unhealthy"
    except:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    try:
        # Check Redis
        redis_health = await redis_client.health_check()
        health_status["services"]["redis"] = "healthy" if redis_health.get("status") == "healthy" else "unhealthy"
    except:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

# For running directly
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
        log_level="info"
    )
