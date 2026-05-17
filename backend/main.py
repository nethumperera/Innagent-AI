# ════════════════════════════════════════════════════════════════
# InnAgent AI — FastAPI Application Entry Point
# ════════════════════════════════════════════════════════════════

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import get_settings
from backend.routers import (
    agent_router, webhook_router, dashboard_router,
    hotels_router, reviews_router,
)
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Start scheduler in non-test environments
    if settings.ENVIRONMENT != "test":
        try:
            from backend.services.scheduler import start_scheduler
            start_scheduler()
            logger.info("Scheduler started")
        except Exception as e:
            logger.warning(f"Scheduler failed to start: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    try:
        from backend.services.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        f"Multi-agent AI hotel management platform for {settings.CLIENT_NAME}. "
        "Manages pricing, guest communication, revenue analytics, reviews, and operations."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(hotels_router)
app.include_router(agent_router)
app.include_router(webhook_router)
app.include_router(dashboard_router)
app.include_router(reviews_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "client": settings.CLIENT_NAME,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check with service status."""
    services = {"api": True, "groq": False, "supabase": False, "twilio": False}

    if settings.GROQ_API_KEY:
        services["groq"] = True
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
        services["supabase"] = True
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        services["twilio"] = True

    all_healthy = all(services.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
    )
