"""Ambient World & Relaxation Studio Package."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.studios.ambient_world.ambient_catalog import ARCHETYPES
from src.studios.ambient_world.ambient_producer import AmbientWorldProducer
from src.studios.ambient_world.ambient_storyboard import generate_ambient_storyboard


async def handle_orchestrated_ambient(job_id: str, request: Any) -> Any:
    """Orchestrator bridge handler for Ambient World productions."""
    from src.services.storage import get_storage_provider, ArtifactCategory, StudioArtifactManifest

    storage = get_storage_provider()
    primary = getattr(request, "archetype", None) or request.topic or "swiss_alps"
    secondary = getattr(request, "secondary_atmosphere", None)
    sb = generate_ambient_storyboard(
        primary=primary,
        secondary=secondary,
        custom_title=request.topic,
        duration_seconds=float(request.duration_seconds),
    )
    producer = AmbientWorldProducer()
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
    for idx, vid in enumerate(result["raw_videos"]):
        item = await storage.save_artifact(
            project_id=ep_id,
            category=ArtifactCategory.SECTION_2_VIDEOS,
            filename=Path(vid).name,
            source_path_or_bytes=vid,
            scene_index=idx + 1,
            model_name="hunyuan-video-1080p",
        )
        video_items.append(item)

    bgm_item = await storage.save_artifact(
        project_id=ep_id,
        category=ArtifactCategory.SECTION_4_BGM,
        filename=Path(result["bgm_path"]).name,
        source_path_or_bytes=result["bgm_path"],
        model_name="velvet-sound-suno",
    )

    manifest = StudioArtifactManifest(
        project_id=ep_id,
        title=result["title"],
        studio_type="ambient_world",
        topic=request.topic,
        created_at=datetime.now(timezone.utc).isoformat(),
        section_0_master=master_item,
        section_1_images=image_items,
        section_2_videos=video_items,
        section_4_bgm=[bgm_item],
    )
    return manifest


try:
    from src.orchestrator.studio_registry import studio_registry
    
    # 1. Register Unified Master Ambient World Studio
    studio_registry.register_studio(
        studio_id="ambient_world",
        display_name="Velvet Ambient World Studio (14 Archetypes & Fusion)",
        description="Produces 4K Swiss Alps, Ocean, Forest, Blizzard, Beach House & Night Sleep with Velvet Anti-Fatigue Audio",
        default_fps=24,
        genre="ambient_relaxation",
        handler=handle_orchestrated_ambient,
    )
    
    # 2. Register The 5 Clustered Specialized Studios for convenient direct routing
    clusters = [
        ("alpine_sanctuary", "Alpine & Mountain Sanctuary", "Swiss Alps, Sacred Himalayas, and Misty Mountain Ranges"),
        ("aquatic_haven", "Aquatic & Coastal Haven", "Ocean World, Crystal Lakes, Tropical Beaches, and Beach Houses"),
        ("forest_seasonal", "Forest & Seasonal Retreat", "Ancient Pine Forests, Autumn Foliage, Winter Snows, and Rain Retreats"),
        ("cozy_hearth", "Cozy Shelter & Hearth", "Starlit Campfires, Blizzard Cabins, and Fireplace Terraces"),
        ("deep_sleep_zen", "Deep Sleep & Celestial Zen", "Moonlit Night Skies, 432Hz Meditation, and Delta Wave Sleepscapes"),
    ]
    for cid, cname, cdesc in clusters:
        studio_registry.register_studio(
            studio_id=cid,
            display_name=cname,
            description=cdesc,
            default_fps=24,
            genre="ambient_relaxation",
            handler=handle_orchestrated_ambient,
        )
except Exception:
    pass
