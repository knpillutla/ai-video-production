"""Dedicated API Router for Blue-Chip Educational Documentary Productions.

Provides independent endpoints for 21-chapter story creation, metadata extraction,
and stage-gate artifact synthesis, decoupled from relaxation and music video pipelines.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.routes.local_production import LocalProduceRequest, LocalProduceResponse, _reserve_next_episode_id
from src.core.storage import storage_service, sanitize_container_name
from src.core.telemetry import logger
from src.domain.format_artifacts import DocumentaryArtifacts, DocumentaryStoryArtifact, DocumentaryChapter
from src.services.job_manager import job_manager
from src.studios.documentary_studio.doc_stage_orchestrator import dispatch_documentary_stage
from src.studios.documentary_studio.doc_story_service import (
    build_raw_documentary_story,
    persist_raw_documentary_story,
)

router = APIRouter(prefix="/api/documentary", tags=["Documentary Studio Engine"])


class DocumentaryCreateEpisodeRequest(BaseModel):
    channel_id: str = "euro_discovery"
    destination: Optional[str] = None
    country: Optional[str] = None
    prompt: Optional[str] = None
    genre: Optional[str] = "doc/nations"
    sub_genre: Optional[str] = "europe_nations"
    primary_archetype: Optional[str] = "countries"
    user_id: Optional[str] = "user_krishna_01"
    tier: Optional[str] = "balanced"


class DocumentaryCreateEpisodeResponse(BaseModel):
    success: bool
    episode_id: str
    title: str
    destination_entity: str
    format: str = "documentary"
    total_chapters: int
    story: Dict[str, Any]


def _resolve_doc_episode_dir(user_id: str, channel_id: str, dest_slug: str, episode_id: str) -> Path:
    c_name = sanitize_container_name(user_id) if "@" in user_id else user_id
    base = storage_service.root_dir / c_name / "networks" / channel_id / "documentary" / dest_slug / episode_id.lower()
    base.mkdir(parents=True, exist_ok=True)
    return base


def _find_doc_episode_dir(channel_id: str, episode_id: str) -> Optional[Path]:
    return storage_service.find_episode_path("user_krishna_01", channel_id, episode_id, format_slug="documentary")


@router.post("/create-episode", response_model=DocumentaryCreateEpisodeResponse, status_code=status.HTTP_201_CREATED)
async def create_documentary_episode(req: DocumentaryCreateEpisodeRequest):
    """Auto-generates raw story script with 21 chapters, extracting title and metadata."""
    user_id_val = req.user_id or "user_krishna_01"
    eff_channel = req.channel_id or "euro_discovery"
    dest = (req.destination or req.country or "").strip()
    clean_prompt = (req.prompt or "").strip()
    eff_sub = req.sub_genre or ("europe_nations" if ("euro" in eff_channel.lower() or "discovery" in eff_channel.lower()) else "europe_nations")
    eff_arch = req.primary_archetype or "country_overview"

    # If destination not provided or is generic theme/id, resolve country from geo rotation
    from src.studios.documentary_studio.doc_geo_rotation import is_known_geo_entity, resolve_autonomous_geo_details
    if not dest or re.match(r"^ep[-_]?\d+$", dest.lower()) or not is_known_geo_entity(dest):
        _, _, _, picked_entity = resolve_autonomous_geo_details(
            sub_genre=eff_sub,
            archetype=eff_arch,
            user_id=user_id_val,
            channel_id=eff_channel,
            custom_prompt=clean_prompt or dest,
        )
        dest = picked_entity or "Norway"

    # 1. Synthesize 21-chapter Master Story via Gemini
    story_dict = await asyncio.to_thread(
        build_raw_documentary_story,
        destination=dest,
        genre=req.genre or "doc/nations",
        sub_genre=eff_sub,
        archetype=eff_arch,
        custom_prompt=clean_prompt,
        channel_id=eff_channel,
    )

    # 2. Derive authentic country entity from generated story
    final_dest = story_dict.get("destination_entity") or dest
    dest_slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", final_dest.lower()).strip("_") or "destination"
    next_id = _reserve_next_episode_id(user_id_val, eff_channel, format_slug="documentary", production_name=dest_slug)
    ep_dir = _resolve_doc_episode_dir(user_id_val, eff_channel, dest_slug, next_id)

    # 3. Persist raw story, gemini_inputs, user_inputs, manifest and pipeline state
    persist_raw_documentary_story(ep_dir, story_dict)
    derived_title = story_dict.get("title", f"{final_dest}: Sovereign Heritage & 21 Wonders")
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()

    user_inputs_payload = {
        "channel_id": eff_channel,
        "format": "documentary",
        "format_slug": "documentary",
        "episode_id": next_id,
        "production_name": final_dest,
        "destination": final_dest,
        "country": final_dest,
        "prompt": clean_prompt,
        "theme": derived_title,
        "title": derived_title,
        "genre": req.genre or "doc/nations",
        "sub_genre": eff_sub,
        "primary_archetype": eff_arch,
        "user_id": user_id_val,
        "tier": req.tier or "balanced",
        "execution_mode": "test",
        "pipeline_strategy": "documentary_standard",
        "num_shots": len(story_dict.get("chapters", [])) * 3,
        "total_chapters": len(story_dict.get("chapters", [])),
        "created_at": now_iso,
        "screenplay_generation_status": "ready",
        "generated_output": {
            "title": derived_title,
            "story_topic": story_dict.get("synopsis", ""),
            "destination_entity": final_dest,
            "genre": req.genre or "doc/nations",
            "sub_genre": eff_sub,
            "primary_archetype": eff_arch,
        },
    }
    (ep_dir / "user_inputs.json").write_text(json.dumps(user_inputs_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest_payload = {
        "episode_id": next_id,
        "title": derived_title,
        "production_name": final_dest,
        "destination_entity": final_dest,
        "tier": req.tier or "balanced",
        "prompt": clean_prompt,
        "genre": req.genre or "doc/nations",
        "sub_genre": eff_sub,
        "primary_archetype": eff_arch,
        "format": "documentary",
        "channel_id": eff_channel,
        "user_id": user_id_val,
        "created_at": now_iso,
    }
    (ep_dir / "episode_manifest.json").write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    pipeline_state_payload = {
        "episode_id": next_id,
        "channel_id": eff_channel,
        "pipeline_strategy": "documentary_standard",
        "execution_mode": "test",
        "tier": req.tier or "balanced",
        "current_stage": 1,
        "stage_status": "ready",
        "stage_approvals": {"story": True, "narration": False, "screenplay": False, "keyframes": False, "bgm": False, "motion": False, "master": False, "short": False, "packaging": False, "script": True, "photos": False, "audio": False},
        "stages_completed": {"story": True, "narration": False, "screenplay": False, "keyframes": False, "bgm": False, "motion": False, "master": False, "short": False, "packaging": False, "script": True, "photos": False, "audio": False},
        "artifacts": ["raw_gemini_story.json", "gemini_story_inputs.json", "gemini_inputs.json", "user_inputs.json", "episode_manifest.json", "pipeline_state.json"],
    }
    (ep_dir / "pipeline_state.json").write_text(json.dumps(pipeline_state_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    job_id = f"job_doc_{next_id.lower()}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=next_id, title=derived_title, channel_id=eff_channel, user_id=user_id_val)
    logger.info(f"doc_episode_created: id={next_id} entity='{final_dest}' dir={ep_dir}")

    return DocumentaryCreateEpisodeResponse(
        success=True,
        episode_id=next_id,
        title=derived_title,
        destination_entity=final_dest,
        total_chapters=story_dict.get("total_chapters", len(story_dict.get("chapters", []))),
        story=story_dict,
    )


@router.post("/stages/{stage_name}", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def execute_documentary_stage(stage_name: str, req: LocalProduceRequest):
    """Execute a specific documentary stage (story, narration, screenplay, photos, bgm, motion, master)."""
    res = await dispatch_documentary_stage(req, stage_name=stage_name)
    return LocalProduceResponse(**res)


@router.post("/produce", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def produce_documentary(req: LocalProduceRequest):
    """Produces documentary stages independently (Story -> Narration -> Screenplay -> Photos -> BGM -> Motion -> Master)."""
    res = await dispatch_documentary_stage(req)
    return LocalProduceResponse(**res)


@router.get("/poll-artifacts")
async def poll_documentary_artifacts(
    channel_id: str,
    episode_id: str,
    format: Optional[str] = "documentary",
    production_name: Optional[str] = None,
    user_id: str = "knpillutla@gmail.com",
):
    """Real-time disk scanner returning synthesized documentary artifacts decoupled from relaxation."""
    from src.studios.documentary_studio.doc_artifact_scanner import scan_documentary_artifacts
    return scan_documentary_artifacts(
        channel_id=channel_id,
        episode_id=episode_id,
        format_slug=format,
        production_name=production_name,
        user_id=user_id,
    )


@router.get("/artifacts/{channel_id}/{episode_id}", response_model=DocumentaryArtifacts)
async def get_documentary_artifacts(channel_id: str, episode_id: str):
    """Scans and returns the decoupled DocumentaryArtifacts domain model for an episode."""
    ep_dir = _find_doc_episode_dir(channel_id, episode_id)
    if not ep_dir or not ep_dir.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documentary episode '{episode_id}' not found.")
    raw_s = json.loads((ep_dir / "raw_gemini_story.json").read_text(encoding="utf-8")) if (ep_dir / "raw_gemini_story.json").is_file() else {}
    story_obj = DocumentaryStoryArtifact(
        title=raw_s.get("title", f"Documentary {episode_id}"), destination_entity=raw_s.get("destination_entity", "Destination"),
        synopsis=raw_s.get("synopsis", ""), total_chapters=len(raw_s.get("chapters", [])),
        chapters=[DocumentaryChapter(**ch) for ch in raw_s.get("chapters", [])], status=raw_s.get("status", "ready"),
    ) if raw_s else None
    kfs = [{"filename": img.name, "url": f"/storage/{img.name}", "size": img.stat().st_size}
           for ext in ("*.png", "*.jpg", "*.webp") for img in sorted(ep_dir.glob(f"keyframe_{ext}")) + sorted(ep_dir.glob(f"shot_{ext}"))]
    return DocumentaryArtifacts(
        episode_id=episode_id, channel_id=channel_id, title=story_obj.title if story_obj else f"Documentary {episode_id}",
        current_stage=1 if not kfs else 4, story=story_obj, keyframes=kfs,
    )
