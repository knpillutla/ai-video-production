"""Vocal Music Video Metadata Packaging, Evidence Bundle, and Cost Export.

Produces YouTube packaging, chapter markers, localized metadata, A/B testing configs,
cost ledger updates, evidence bundles, and 9:16 vertical Shorts for completed vocal productions.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import time
from typing import Any

from src.billing.benchmark_db import record_production_benchmark
from src.billing.cost_tracker import actualize_production_cost, calculate_preflight_estimate, save_cost_report
from src.compliance.evidence_bundle import build_evidence_bundle, save_evidence_bundle
from src.compositor.vocal_short_renderer import render_vocal_short_video, select_full_pose_image
from src.core.telemetry import logger


def format_chapter_time(seconds: float) -> str:
    """Format seconds into standard YouTube MM:SS chapter timestamp."""
    s = int(round(seconds))
    m, sec = divmod(s, 60)
    return f"{m:02d}:{sec:02d}"


def sanitize_text(text: str, strip_emojis: bool = True) -> str:
    """Normalize text into clean, copy-pasteable plain text with real newlines, zero emojis, and zero /n or \\n."""
    if not text:
        return ""
    import re
    t = text.replace("/n", "\n").replace("\\\\n", "\n").replace("\\n", "\n").replace("\r\n", "\n")
    t = t.replace("<", "").replace(">", "").replace("\u2022", "-")
    if strip_emojis:
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff\u2600-\u27bf\ufe00-\ufe0f\u200d]+", flags=re.UNICODE)
        t = emoji_pattern.sub("", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" +\n", "\n", t)
    t = re.sub(r"\n +", "\n", t)
    while "\n\n\n" in t:
        t = t.replace("\n\n\n", "\n\n")
    return t.strip()


def export_vocal_production_bundle(
    episode: Any,
    ep_dir: Path,
    sb_data: dict[str, Any],
    actual_dur: float,
    t_start: float,
    language: str,
    keyframe_path: Path,
    master_video_path: Path | None = None,
) -> None:
    """Export complete evidence bundle, cost reporting, YouTube packaging, plain-text description, and 9:16 Short."""
    bundle = build_evidence_bundle(
        project_id=episode.id,
        episode_id=episode.id,
        title=episode.title,
        script_thesis=sb_data.get("hook_thesis", episode.title),
        research_sources=[{"type": "original_vocal_composition", "title": episode.title}],
        originality_score=0.98,
    )
    bundle_path = save_evidence_bundle(bundle, ep_dir / "evidence_bundle")
    episode.evidence_bundle_path = str(bundle_path)

    if episode.cost_record is None:
        episode.cost_record = calculate_preflight_estimate(episode)
        episode.estimated_cost_usd = episode.cost_record.predicted_total_usd
    render_elapsed = round(time.perf_counter() - t_start, 2)
    actualize_production_cost(
        episode.cost_record,
        {"tokens_used": 15000, "voice_characters": 0, "images_generated": 1, "music_tracks": 1, "render_seconds": render_elapsed, "lipsync_seconds": 0.0},
        duration_seconds=float(actual_dur),
    )
    episode.actual_spend_usd = episode.cost_record.actual_total_usd
    save_cost_report(episode.cost_record, ep_dir)

    try:
        record_production_benchmark(
            episode_id=str(episode.id),
            title=episode.title,
            duration_seconds=float(actual_dur),
            estimated_total_usd=episode.cost_record.predicted_total_usd,
            actual_total_usd=episode.cost_record.actual_total_usd,
            artifact_counts={"scenes": 1, "images": 1, "music_tracks": 1, "render_seconds": render_elapsed},
            model_breakdown={"script": "gemini-1.5-flash", "visuals": "fal-zimage", "soundtrack": "suno-v3.5-pro"},
            theme="vocal",
            genre="vocal",
            variance_explanation=f"Rendered vocal song in {render_elapsed:.1f}s",
        )
    except Exception as ex:
        logger.warning(f"benchmark_db_record_failed: {ex}")

    yt_meta = sb_data.get("youtube_metadata") or {}
    ch_p2 = max(10.0, actual_dur * 0.35)
    ch_p3 = max(20.0, actual_dur * 0.65)
    chapters = [
        "00:00 - Pallavi (Intro Groove & Melody Setup)",
        f"{format_chapter_time(ch_p2)} - Anupallavi (Emotional Verse & Swell)",
        f"{format_chapter_time(ch_p3)} - Charanam (Signature Climax & Harmony)",
    ]
    raw_desc = yt_meta.get("description") or (
        f"Official 4K lyrical video for '{sb_data.get('title_localized', '')} ({sb_data.get('title_en', episode.title)})'.\n\n"
        f"Broadcast Chapters:\n" + "\n".join(chapters) + f"\n\nLyrics:\n{sb_data.get('lyrics', '')}\n\n"
        f"Mastered to -14.0 LUFS 48kHz Broadcast Audio.\n100% Commercial Master Rights | 4K UHD Visuals"
    )
    clean_desc = sanitize_text(raw_desc)

    import re
    # Strictly remove character names from description and title
    char_names = [c.get("name") for c in sb_data.get("characters", []) if isinstance(c, dict) and c.get("name")]
    for cn in char_names:
        if cn and len(cn) > 1:
            clean_desc = re.sub(rf"\bFeaturing\s+{re.escape(cn)}\s+and\s+\w+\s+in\s+a\b", "A", clean_desc, flags=re.IGNORECASE)
            clean_desc = re.sub(rf"\bFeaturing\s+\w+\s+and\s+{re.escape(cn)}\s+in\s+a\b", "A", clean_desc, flags=re.IGNORECASE)
            clean_desc = re.sub(rf"\bFeaturing\s+{re.escape(cn)}\s+in\s+a\b", "A", clean_desc, flags=re.IGNORECASE)
            clean_desc = re.sub(rf"\bFeaturing\s+{re.escape(cn)}\b", "", clean_desc, flags=re.IGNORECASE)
            clean_desc = re.sub(rf"\b{re.escape(cn)}\b", "", clean_desc)

    clean_desc = re.sub(r"(\d{2}:\d{2})\s*[-–—]?\s*[^\w\s\(\)]*\s*", r"\1 - ", clean_desc)
    if "00:00" not in clean_desc:
        clean_desc += "\n\nBroadcast Chapters:\n" + "\n".join(chapters)
    if "Lyrics:" not in clean_desc and sb_data.get("lyrics"):
        clean_desc += f"\n\nLyrics:\n{sanitize_text(sb_data.get('lyrics', ''))}"
    if "-14.0 LUFS" not in clean_desc:
        clean_desc += "\n\nAudio & Visual Specs:\n- Mastered to -14.0 LUFS 48kHz Broadcast Stereo\n- 4K UHD Master (3840x2160) | 100% Commercial Master Rights"
    clean_desc = sanitize_text(clean_desc)

    clean_title = sanitize_text(yt_meta.get("title") or f"{sb_data.get('title_localized', '')} - {sb_data.get('title_en', episode.title)} | 4K Lyrical Music Video".strip(" -"))
    for cn in char_names:
        if cn and len(cn) > 1:
            clean_title = re.sub(rf"\b{re.escape(cn)}\b", "", clean_title)
    clean_title = re.sub(r"\s*\|\s*\|+", " |", clean_title)
    clean_title = re.sub(r"[ \t]+", " ", clean_title).strip(" -|")
    clean_pinned = sanitize_text(yt_meta.get("pinned_comment") or f"Enjoying '{sb_data.get('title_localized', '')}'? Share your favorite lyrical couplet in the comments!")
    tags_list = yt_meta.get("tags") or ["music_video", "lyrical_video", "4k_music_video", language, "telugu_songs" if language == "te" else f"{language}_songs"]
    tags_str = ", ".join(tags_list)

    pkg_dir = ep_dir / "youtube_package"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / "youtube_description.txt").write_text(clean_desc, encoding="utf-8")
    (ep_dir / "youtube_title.txt").write_text(clean_title, encoding="utf-8")
    (ep_dir / "youtube_tags.txt").write_text(tags_str, encoding="utf-8")
    (ep_dir / "youtube_pinned_comment.txt").write_text(clean_pinned, encoding="utf-8")
    (pkg_dir / "description.txt").write_text(clean_desc, encoding="utf-8")
    (pkg_dir / "title.txt").write_text(clean_title, encoding="utf-8")
    (pkg_dir / "tags.txt").write_text(tags_str, encoding="utf-8")
    (pkg_dir / "pinned_comment.txt").write_text(clean_pinned, encoding="utf-8")
    (pkg_dir / "chapters.txt").write_text("\n".join(chapters), encoding="utf-8")

    audio_candidates = [
        ep_dir / "audio_stems" / "bgm_normalized_48k.mp3",
        ep_dir / "audio_stems" / "bgm_cleaned.mp3",
        ep_dir / "audio_stems" / "bgm_master.wav",
        ep_dir / "audio" / "song.mp3",
        ep_dir / "song.mp3",
    ]
    if master_video_path and Path(master_video_path).is_file():
        audio_candidates.append(Path(master_video_path))
    audio_path = next((p for p in audio_candidates if p.is_file()), None)

    short_out = ep_dir / "short_9x16_teaser.mp4"
    shorts_dir = ep_dir / "shorts"
    shorts_dir.mkdir(parents=True, exist_ok=True)
    short_named = shorts_dir / f"short_9x16_{ep_dir.name}_{language}.mp4"

    full_pose_img = select_full_pose_image(ep_dir, sb_data, keyframe_path)
    lyrics_segs = sb_data.get("lyrics_segments", [])
    vocal_start = max(0.0, float(lyrics_segs[0].get("start", 0.0)) - 0.25) if lyrics_segs else 0.0

    if audio_path and audio_path.is_file() and full_pose_img.is_file():
        try:
            render_vocal_short_video(
                full_pose_img=full_pose_img,
                audio_path=audio_path,
                output_path=short_out,
                sb_data=sb_data,
                language=language,
                vocal_start=vocal_start,
                duration=30.0,
            )
            shutil.copyfile(short_out, short_named)
            logger.info(f"rendered_vocal_short: {short_out} (vocal_start={vocal_start:.2f}s, img={full_pose_img.name})")
        except Exception as ex:
            logger.warning(f"render_vocal_short_failed: {ex}")

    short_title = f"{sb_data.get('title_localized', '')} #Shorts | {language.upper()} Romantic Melody".strip()
    short_desc = f"Listen to the soulful {language.upper()} romantic melody '{sb_data.get('title_localized', '')}'! 🎵\nWatch the full 4K lyrical video on our channel!\n\n#Shorts #{language}_songs #RomanticMelody #4KMusicVideo"
    short_tags = ["Shorts", f"{language}_shorts", "RomanticShorts", "ViralMelody"]
    (pkg_dir / "short_title.txt").write_text(short_title, encoding="utf-8")
    (pkg_dir / "short_description.txt").write_text(short_desc, encoding="utf-8")
    (pkg_dir / "short_tags.txt").write_text(", ".join(short_tags), encoding="utf-8")

    short_video_file = str(short_out) if short_out.is_file() else None

    yt_pkg_short = {
        "title": short_title, "description": short_desc, "tags": short_tags,
        "category_id": "10", "has_synthetic_media": True, "privacy_status": "public",
        "short_video_path": short_video_file,
    }
    with open(ep_dir / "youtube_packaging_short.json", "w", encoding="utf-8") as f:
        json.dump(yt_pkg_short, f, indent=2, ensure_ascii=False)

    yt_packaging = {
        "title": clean_title,
        "description": clean_desc,
        "tags": tags_list,
        "category_id": "10",
        "thumbnail_prompt": yt_meta.get("thumbnail_prompt") or sb_data.get("prompts_by_model", {}).get("z_image", ""),
        "pinned_comment": clean_pinned,
        "chapter_markers": chapters,
        "caption_tracks": [
            {"language": "en", "name": "English Subtitles", "file": "subtitles/captions_en.srt"},
            {"language": language, "name": f"{language.upper()} Lyrics", "file": f"subtitles/captions_{language}.srt"},
        ],
        "has_synthetic_media": True,
        "contains_synthetic_media": True,
        "privacy_status": "public",
        "short_video_path": short_video_file,
    }
    ab_testing = {
        "archetype_key": "vocal_music_video",
        "variants": [
            {"variant_id": "variant_a_intimate", "name": "Intimate Couple Chemistry", "prompt": sb_data.get("prompts_by_model", {}).get("z_image", "")},
            {"variant_id": "variant_b_heritage", "name": "Opulent Heritage Courtyard", "prompt": sb_data.get("prompts_by_model", {}).get("flux_dev", "")},
        ],
    }
    loc_meta = {
        language: {"title": yt_packaging["title"], "description": yt_packaging["description"]},
        "en": {
            "title": f"{sb_data.get('title_en', episode.title)} • 4K Lyrical Music Video",
            "description": f"Official 4K music video for {sb_data.get('title_en', episode.title)}.\nMastered in broadcast 4K stereo (-14 LUFS).\n100% Commercial Master Rights.",
        },
    }
    ep_manifest = {
        "episode_id": ep_dir.name,
        "title": sb_data.get("title_en") or episode.title,
        "title_localized": sb_data.get("title_localized") or "",
        "tier": getattr(episode, "selected_tier", "balanced"),
        "genre": "music_video",
        "story_topic": sb_data.get("hook_thesis", episode.title),
        "duration_seconds": float(actual_dur),
        "recommended_fps": 30,
        "audio_tags": sb_data.get("suno_tags", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "is_approved": True,
        "short_video_path": short_video_file,
    }
    for fn, d in [
        ("youtube_packaging.json", yt_packaging),
        ("thumbnail_ab_testing.json", ab_testing),
        ("localized_metadata.json", loc_meta),
        ("episode_manifest.json", ep_manifest),
    ]:
        with open(ep_dir / fn, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)

    keyframe_p1 = ep_dir / "keyframe_p1.jpg"
    if not keyframe_p1.exists() and keyframe_path.exists():
        shutil.copyfile(keyframe_path, keyframe_p1)


__all__ = ["export_vocal_production_bundle", "select_full_pose_image", "render_vocal_short_video"]
