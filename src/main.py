"""
Travel Platform - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.core.config.settings import settings
from src.travel_platform.utils.logger import setup_structlog as setup_logging
from src.database.connection import Database
from src.api.v1.router import api_router
from src.bot.webhook import router as webhook_router
from src.bot.setup import setup_bot, stop_bot
from src.api.middleware import setup_middleware

# Setup logging
logger = setup_logging()

# Get settings with defaults
app_name = getattr(settings, 'APP_NAME', 'Travel Platform')
app_version = getattr(settings, 'APP_VERSION', '1.0.0')
app_description = getattr(settings, 'APP_DESCRIPTION', 'Travel Platform API')
app_env = getattr(settings, 'APP_ENV', 'development')
app_host = getattr(settings, 'APP_HOST', '0.0.0.0')
app_port = getattr(settings, 'APP_PORT', 8000)

# Create FastAPI app
app = FastAPI(
    title=app_name,
    version=app_version,
    description=app_description,
    docs_url="/docs" if app_env != "production" else None,
    redoc_url="/redoc" if app_env != "production" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup API middleware
setup_middleware(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Include bot webhook routes
app.include_router(webhook_router, prefix="/bot")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"🚀 Starting {app_name} v{app_version}")
    logger.info(f"Environment: {app_env}")

    try:
        # Initialize database
        await Database.connect()
        logger.info("✅ Database connected")

        # Initialize bot
        await setup_bot()
        logger.info("✅ Bot initialized")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down application...")
    await Database.disconnect()
    await stop_bot()
    logger.info("✅ Clean shutdown completed")

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": app_name,
        "version": app_version,
        "environment": app_env,
        "status": "running",
        "docs": "/docs" if app_env != "production" else None,
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "database": "unknown",
        }
    }

    try:
        # Check database
        db_health = await Database.health_check()
        health_status["services"]["database"] = "healthy" if db_health.get("status") == "healthy" else "unhealthy"
    except:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status

# For running directly
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=app_host,
        port=app_port,
        reload=app_env == "development",
        log_level="info"
    )

