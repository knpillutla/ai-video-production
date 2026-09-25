"""FastAPI Application Entrypoint for AI Video Producer Studio."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.api.routes import (
    analytics,
    approvals,
    auth,
    billing,
    channel_analytics,
    channels,
    dashboard,
    local_production,
    production,
    projects,
    schedules,
    shows,
    studio_orchestrator,
    trending,
)
from src.core.config import settings
from src.core.telemetry import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context managing startup and shutdown."""
    from src.core.queue import task_queue

    logger.info(
        f"video_studio_started: env={settings.app.app_env}, storage={settings.storage.storage_backend}"
    )

    # Initialize modular studios
    try:
        import src.studios.nature_retreat       # noqa: F401
        import src.studios.cozy_ambiance        # noqa: F401
        import src.studios.rain_retreat         # noqa: F401
        import src.studios.healing_relaxation   # noqa: F401
        logger.info("studios_initialized: nature_retreat, cozy_ambiance, rain_retreat, healing_relaxation")
    except Exception as exc:
        logger.warning(f"studio_initialization_warning: {exc}")

    await task_queue.start_worker()

    yield

    await task_queue.stop_worker()
    logger.info("video_studio_stopped")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="AI Video Producer Studio Core API",
        version="2.0.0",
        description="Multi-tenant, 0-GPU, monetization-ready video generation engine",
        lifespan=lifespan,
    )

    # Configure CORS for Next.js Web Studio frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(auth.router)
    app.include_router(billing.router)
    app.include_router(dashboard.router)
    app.include_router(approvals.router)
    app.include_router(shows.router)
    app.include_router(projects.router)
    app.include_router(production.router)
    app.include_router(trending.router)
    app.include_router(channels.router)
    app.include_router(channel_analytics.router)
    app.include_router(schedules.router)
    app.include_router(analytics.router)
    app.include_router(local_production.router)
    app.include_router(studio_orchestrator.router)

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Global health check endpoint for Cloudflare and Kubernetes probes."""
        return {
            "status": "ok",
            "service": "video-studio-api",
            "version": "2.0.0",
            "storage_backend": settings.storage.storage_backend,
            "environment": settings.app.app_env,
        }

    from pathlib import Path
    from fastapi.staticfiles import StaticFiles

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    storage_dir = Path(__file__).resolve().parent.parent.parent / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/storage", StaticFiles(directory=str(storage_dir)), name="storage")

    @app.get("/", response_class=HTMLResponse, tags=["Web Studio UI"])
    @app.get("/ui", response_class=HTMLResponse, tags=["Web Studio UI"])
    async def serve_studio_ui():
        """Serve the interactive Web Studio SaaS dashboard."""
        try:
            from src.api.ui_composer import render_studio_html
            return HTMLResponse(content=render_studio_html())
        except Exception as exc:
            return HTMLResponse(f"<h1>CineAI Studio API Online</h1><p>{exc}</p>")

    return app


app = create_app()

__all__ = ["app", "create_app"]
