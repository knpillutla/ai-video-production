"""Cozy Ambiance Studio Package."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.studios.cozy_ambiance.cozy_storyboard import CozyStoryboard, generate_cozy_storyboard
from src.studios.studio_producer import StudioProducer, StudioProducer as CozyAmbianceProducer


async def handle_orchestrated_cozy(job_id: str, request: Any) -> Any:
    """Orchestrator bridge handler for Cozy Ambiance productions."""
    from src.services.storage import get_storage_provider, ArtifactCategory, StudioArtifactManifest

    storage = get_storage_provider()
    from src.studios.cozy_ambiance.cozy_storyboard import generate_cozy_storyboard_gemini
    sb = await generate_cozy_storyboard_gemini(theme=request.topic, duration_seconds=float(request.duration_seconds))
    producer = StudioProducer()
    result = await producer.produce(sb)

    ep_id = result["episode_id"]
    master_item = await storage.save_artifact(
        project_id=ep_id,
        category=ArtifactCategory.SECTION_0_MASTER,
        filename=Path(result["master_video_path"]).name,
        source_path_or_bytes=result["master_video_path"],
        resolution="3840x2160",
    )

    image_items = []
    for idx, kf in enumerate(result["keyframes"]):
        item = await storage.save_artifact(
            project_id=ep_id,
            category=ArtifactCategory.SECTION_1_IMAGES,
            filename=Path(kf).name,
            source_path_or_bytes=kf,
            scene_index=idx + 1,
            model_name="flux-1.1-pro-ultra",
        )
        image_items.append(item)

    video_items = []
    for idx, vid in enumerate(result.get("raw_videos", [])):
        item = await storage.save_artifact(
            project_id=ep_id,
            category=ArtifactCategory.SECTION_2_VIDEOS,
            filename=Path(vid).name,
            source_path_or_bytes=vid,
            scene_index=idx + 1,
            model_name="wan-2.1-fluid",
        )
        video_items.append(item)

    bgm_path = result.get("bgm_path")
    bgm_items = []
    if bgm_path:
        bgm_item = await storage.save_artifact(
            project_id=ep_id,
            category=ArtifactCategory.SECTION_4_BGM,
            filename=Path(bgm_path).name,
            source_path_or_bytes=bgm_path,
            model_name="suno-v3.5-pro",
        )
        bgm_items.append(bgm_item)

    manifest = StudioArtifactManifest(
        project_id=ep_id,
        title=result["title"],
        studio_type="cozy_ambiance",
        topic=request.topic,
        created_at=datetime.now(timezone.utc).isoformat(),
        section_0_master=master_item,
        section_1_images=image_items,
        section_2_videos=video_items,
        section_4_bgm=bgm_items,
    )
    return manifest


try:
    from src.orchestrator.studio_registry import studio_registry
    studio_registry.register_studio(
        studio_id="cozy_ambiance",
        display_name="Cozy Ambiance & Biophilic Studio",
        description="Produces 4K Cozy Living Spaces, Oceanfront Fireplace Terraces, and ASMR Soundscapes",
        default_fps=24,
        genre="cozy_ambiance",
        handler=handle_orchestrated_cozy,
    )
except Exception:
    pass

__all__ = [
    "CozyStoryboard",
    "generate_cozy_storyboard",
    "CozyAmbianceProducer",
    "handle_orchestrated_cozy",
]
