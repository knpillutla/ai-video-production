"""Ambient World Packaging and Export Utilities.

Handles long-play stretching, teaser short extraction, localized metadata, and topic memory indexing.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.services.ambient_metadata_packager import YouTubeAmbientPackage, generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import LocalizedMetadata, localize_metadata_for_languages
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import ThumbnailABPackage, generate_thumbnail_ab_variants
from src.services.topic_memory import topic_memory
from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


def handle_long_play_export(master: Path, ep_dir: Path, hours: Optional[float], fade_hours: Optional[float]) -> Optional[Path]:
    """Export long-play multi-hour stream loop with optional fade to black."""
    if not hours or hours <= 0:
        return None
    suffix = f"_{int(fade_hours)}h_black" if fade_hours else ""
    label = int(hours) if hours.is_integer() else hours
    lp_path = ep_dir / f"master_4k_{label}hour{suffix}_sleep.mp4"
    if not lp_path.is_file() or lp_path.stat().st_size < 1000:
        export_long_play_broadcast(source_4k_video=master, output_long_play=lp_path, target_duration_seconds=hours * 3600.0, fade_to_black_hours=fade_hours)
    return lp_path


def handle_short_export(master: Path, ep_dir: Path, gen: bool) -> Optional[Path]:
    """Generate 9:16 vertical teaser short from 4K master."""
    if not gen:
        return None
    s_path = ep_dir / "short_9x16_teaser.mp4"
    if not s_path.is_file() or s_path.stat().st_size < 1000:
        generate_ambient_short(source_4k_video=master, output_short_path=s_path)
    return s_path


def export_metadata_packages(
    sb: AmbientStoryboard, ep_dir: Path, hours: Optional[float], fade_h: Optional[float]
) -> Tuple[YouTubeAmbientPackage, ThumbnailABPackage, Dict[str, LocalizedMetadata]]:
    """Generate YouTube packaging, A/B thumbnails, multi-language SEO, and persist in Topic Memory."""
    pkg = generate_youtube_ambient_package(sb.primary_archetype, hours or 1.0, sb.secondary_archetype, fade_h)
    (ep_dir / "youtube_packaging.json").write_text(json.dumps(pkg.model_dump(), indent=2), encoding="utf-8")
    ab = generate_thumbnail_ab_variants(sb.primary_archetype)
    (ep_dir / "thumbnail_ab_variants.json").write_text(json.dumps(ab.model_dump(), indent=2), encoding="utf-8")
    loc = localize_metadata_for_languages(sb.primary_archetype, pkg.title, pkg.description)
    (ep_dir / "localized_metadata.json").write_text(json.dumps({k: v.model_dump() for k, v in loc.items()}, indent=2), encoding="utf-8")
    topic_memory.remember_topic(sb.title, f"ambient_{sb.cluster}", [sb.primary_archetype, sb.cluster, "relaxation", "sleep", "4k", "432hz"], f"Velvet Ambient: {sb.title}", ep_dir.name)
    return pkg, ab, loc
