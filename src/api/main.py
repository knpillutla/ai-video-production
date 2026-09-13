"""FastAPI Application Entrypoint for AI Video Producer Studio."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.api.routes import (
    approvals,
    auth,
    billing,
    channels,
    dashboard,
    production,
    projects,
    schedules,
    shows,
    trending,
)
from src.core.config import settings
from src.core.telemetry import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context managing startup and shutdown."""
    from uuid import UUID
    from src.core.queue import task_queue
    from src.compositor.pipeline import pipeline_coordinator

    logger.info(
        f"video_studio_started: env={settings.app.app_env}, storage={settings.storage.storage_backend}"
    )

    async def video_worker(payload: dict):
        u_id = UUID(payload["user_id"])
        ep_id = UUID(payload["episode_id"])
        await pipeline_coordinator.produce_episode_master(u_id, ep_id, dry_run=True)

    task_queue.register_handler("produce_video", video_worker)
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
    app.include_router(schedules.router)

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

    @app.get("/", response_class=HTMLResponse, tags=["Web Studio UI"])
    @app.get("/ui", response_class=HTMLResponse, tags=["Web Studio UI"])
    async def serve_studio_ui():
        """Serve the interactive Web Studio SaaS dashboard."""
        from pathlib import Path
        ui_path = Path(__file__).resolve().parent.parent / "static" / "index.html"
        if ui_path.exists():
            return HTMLResponse(content=ui_path.read_text(encoding="utf-8"))
        return HTMLResponse("<h1>CineAI Studio API Online</h1><p>Visit /docs for Swagger UI</p>")

    return app


app = create_app()

__all__ = ["app", "create_app"]
