"""Autonomous Daily Theme Scheduler API routes."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.deps import get_current_user
from src.core.telemetry import logger
from src.domain.distribution import ScheduleJob, ScheduleJobCreate
from src.domain.repo import repo
from src.domain.user import User
from src.scheduling.daily_scheduler import daily_scheduler

router = APIRouter(prefix="/api/schedules", tags=["Autonomous Scheduling"])


class TriggerScheduleResponse(BaseModel):
    """Response returned when scheduled pipeline run is triggered."""

    schedule_id: UUID
    episode_id: UUID
    title: str
    theme: str
    master_video_path: str | None
    published: bool
    publication_id: UUID | None
    total_videos_created: int


@router.get("", response_model=list[ScheduleJob])
async def list_schedules(current_user: User = Depends(get_current_user)):
    """List all autonomous recurring generation schedules owned by user."""
    return repo.list_schedules(current_user.id)


@router.post("", response_model=ScheduleJob, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    req: ScheduleJobCreate,
    current_user: User = Depends(get_current_user),
):
    """Register a new autonomous recurring theme generation schedule."""
    show = repo.get_show(current_user.id, req.show_id)
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Universe show not found")

    job = ScheduleJob(
        user_id=current_user.id,
        show_id=req.show_id,
        theme=req.theme,
        format=req.format,
        visual_style=req.visual_style,
        cadence=req.cadence,
        time_of_day_utc=req.time_of_day_utc,
        target_languages=req.target_languages,
        auto_publish=req.auto_publish,
        auto_publish_channel_id=req.auto_publish_channel_id,
    )
    saved = repo.save_schedule(job)
    logger.info(f"schedule_created: id={saved.id} theme='{saved.theme}' cadence='{saved.cadence}'")
    return saved


@router.post("/{schedule_id}/trigger", response_model=TriggerScheduleResponse)
async def trigger_schedule_now(
    schedule_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Manually trigger an immediate execution of an autonomous scheduled theme pipeline."""
    job = repo.get_schedule(current_user.id, schedule_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule job not found")

    result = await daily_scheduler.trigger_schedule_job(job_id=schedule_id, user_id=current_user.id)
    return TriggerScheduleResponse(**result)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Delete an autonomous schedule."""
    deleted = repo.delete_schedule(current_user.id, schedule_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule job not found")
