"""Decoupled Studio Orchestrator API Routes."""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status

from src.orchestrator.orchestrator_models import (
    StudioCostEstimate,
    StudioJobStatus,
    StudioProductionRequest,
)
from src.orchestrator.orchestrator_service import studio_orchestrator
from src.orchestrator.studio_registry import studio_registry
from src.services.storage import get_storage_provider, StudioArtifactManifest

router = APIRouter(prefix="/api/studios", tags=["Studio Orchestrator"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_available_studios():
    """List all dynamically registered studio agents."""
    return [s.model_dump() for s in studio_registry.list_studios()]


@router.post("/estimate", response_model=StudioCostEstimate)
async def estimate_production_cost(req: StudioProductionRequest):
    """Calculate pre-flight itemized cost breakdown."""
    return await studio_orchestrator.calculate_preflight_cost(req)


@router.post("/submit", response_model=StudioJobStatus, status_code=status.HTTP_202_ACCEPTED)
async def submit_studio_production(req: StudioProductionRequest):
    """Submit a video generation job to the Studio Orchestrator."""
    job_status = await studio_orchestrator.submit_production(req)
    if job_status.stage == "blocked_duplicate":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Duplicate topic detected in TopicMemory.",
                "conflict": job_status.duplicate_conflict,
            },
        )
    if job_status.stage == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=job_status.error or "Job submission failed.",
        )
    return job_status


@router.get("/jobs/{job_id}", response_model=StudioJobStatus)
async def get_job_status(job_id: str):
    """Poll the real-time execution status of a studio job."""
    job_status = studio_orchestrator.get_job_status(job_id)
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return job_status


@router.get("/projects/{project_id}/manifest", response_model=StudioArtifactManifest)
async def get_project_manifest(project_id: str):
    """Fetch the canonical 6-section manifest for UI Right Preview Panel."""
    storage = get_storage_provider()
    manifest = await storage.get_manifest(project_id)
    if not manifest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project manifest for '{project_id}' not found.",
        )
    return manifest
