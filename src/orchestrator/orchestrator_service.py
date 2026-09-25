"""Studio Orchestrator executing the 4-Stage Progressive Quality Gate."""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from src.core.telemetry import logger
from src.orchestrator.orchestrator_models import (
    ProductionStage,
    StudioCostEstimate,
    StudioJobStatus,
    StudioProductionRequest,
)
from src.orchestrator.studio_registry import studio_registry
from src.services.storage import get_storage_provider


class StudioOrchestrator:
    """Decoupled orchestrator coordinating studio agents and unified storage."""

    def __init__(self):
        self._jobs: Dict[str, StudioJobStatus] = {}
        self._storage = get_storage_provider()

    def get_job_status(self, job_id: str) -> Optional[StudioJobStatus]:
        """Fetch current status of a production job."""
        return self._jobs.get(job_id)

    async def calculate_preflight_cost(
        self, req: StudioProductionRequest
    ) -> StudioCostEstimate:
        """Calculate itemized pre-flight cost forecast."""
        scenes = max(1, req.scene_count)
        llm_cost = 0.005
        img_cost = scenes * 0.060
        motion_cost = scenes * 0.280 if req.studio_id == "nature_retreat" else scenes * 0.080
        compute_cost = 0.010
        total = round(llm_cost + img_cost + motion_cost + compute_cost, 4)
        return StudioCostEstimate(
            llm_cost_usd=llm_cost,
            image_cost_usd=img_cost,
            video_motion_cost_usd=motion_cost,
            compute_cost_usd=compute_cost,
            total_cost_usd=total,
        )

    async def submit_production(
        self, req: StudioProductionRequest
    ) -> StudioJobStatus:
        """Validate, stage, and dispatch a new studio production."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        cost_est = await self.calculate_preflight_cost(req)

        status = StudioJobStatus(
            job_id=job_id,
            studio_id=req.studio_id,
            topic=req.topic,
            stage=ProductionStage.STAGE_1_PREFLIGHT,
            progress_pct=10,
            message="Stage 1: Pre-flight deduplication & validation",
            cost_estimate=cost_est,
        )
        self._jobs[job_id] = status

        # Check registered studio
        studio_defn = studio_registry.get_studio(req.studio_id)
        if not studio_defn:
            status.stage = ProductionStage.FAILED
            status.error = f"Studio '{req.studio_id}' is not registered."
            return status

        # Launch background execution
        asyncio.create_task(self._execute_pipeline_task(job_id, req))
        return status

    async def _execute_pipeline_task(
        self, job_id: str, req: StudioProductionRequest
    ) -> None:
        """Asynchronous worker executing the 4-Stage Progressive Quality Gate."""
        status = self._jobs[job_id]
        handler = studio_registry.get_handler(req.studio_id)

        try:
            # Stage 1: Pre-Flight Deduplication Check
            from src.services.topic_memory import topic_memory
            is_dup, conflict = topic_memory.is_duplicate_topic(
                req.topic,
                genre=req.studio_id,
                tags=req.custom_params.get("tags", []),
                threshold=0.80,
            )
            if is_dup and conflict and not req.dry_run:
                status.stage = ProductionStage.BLOCKED_DUPLICATE
                status.message = f"Duplicate detected: {conflict.get('title')} ({conflict.get('similarity', 0)*100:.1f}%)"
                status.duplicate_conflict = conflict
                logger.warning(f"orchestrator_duplicate_blocked: {job_id} topic='{req.topic}'")
                return

            status.stage = ProductionStage.STAGE_2_KEYFRAMES
            status.progress_pct = 30
            status.message = "Stage 2: Keyframe Image Quality Gate"
            status.updated_at = datetime.now(timezone.utc).isoformat()

            # Execute Studio Handler (Returns manifest or output artifact paths)
            manifest = await handler(job_id=job_id, request=req)

            status.stage = ProductionStage.COMPLETED
            status.progress_pct = 100
            status.message = "Production complete. 4K Master ready."
            status.manifest = manifest
            status.updated_at = datetime.now(timezone.utc).isoformat()

            # Persist canonical 6-section manifest to storage
            if manifest:
                await self._storage.save_manifest(manifest)

            logger.info(f"orchestrator_job_completed: {job_id}")

        except Exception as exc:
            status.stage = ProductionStage.FAILED
            status.error = str(exc)
            status.message = f"Production failed: {exc}"
            status.updated_at = datetime.now(timezone.utc).isoformat()
            logger.error(f"orchestrator_job_failed: {job_id} error={exc}")


studio_orchestrator = StudioOrchestrator()
