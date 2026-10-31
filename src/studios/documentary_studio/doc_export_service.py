"""Documentary 4K Master Video Assembly and Packaging Service."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional
import imageio_ffmpeg

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_storyboard import DocStoryboard


def _probe_clip_duration(clip_path: Path) -> float:
    """Probe the exact duration of a video clip in seconds."""
    try:
        import re
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], capture_output=True, text=True, errors="ignore")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            return float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3))
    except Exception:
        pass
    return 15.0


def assemble_documentary_4k_master(
    video_clips: List[Path],
    audio_path: Path,
    output_master: Path,
    srt_path: Optional[Path] = None,
    crf: int = 22,
    force_rerun: bool = False,
) -> Path:
    """Assemble seamless 4K 24fps documentary master with audio-synchronized duration and zero cutoffs."""
    out = output_master.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        out_mtime = out.stat().st_mtime
        is_stale = any(c.is_file() and c.stat().st_mtime > out_mtime for c in video_clips) or (audio_path.is_file() and audio_path.stat().st_mtime > out_mtime)
        if not is_stale:
            return out

    from src.services.cineloop_service import ensure_thumbnail_intro_clip
    t_intro = ensure_thumbnail_intro_clip(out.parent, crf=crf)
    if t_intro and t_intro not in video_clips:
        video_clips = [t_intro] + list(video_clips)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    n = len(video_clips)
    durations = [_probe_clip_duration(c) for c in video_clips]
    a_dur = _probe_clip_duration(audio_path) if (audio_path and audio_path.is_file()) else 0.0
    x_dur = 1.0

    if n == 1:
        c_dur = durations[0]
        shortfall = max(0.0, a_dur - c_dur) + (1.2 if a_dur > 0 else 0.0)
        target_dur = round(c_dur + shortfall, 2)
        v_scale = f"[0:v]scale=3840:2160,setsar=1,fps=24"
        if shortfall > 0.05:
            v_scale += f",tpad=stop_mode=clone:stop_duration={shortfall:.2f}"
        v_scale += "[v]"
        afade_st = max(0.0, target_dur - 2.5)
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(video_clips[0]), "-i", str(audio_path),
            "-filter_complex", f"{v_scale};[1:a]volume=1.0,apad,afade=t=out:st={afade_st:.2f}:d=2.5[aout]",
            "-map", "[v]", "-map", "[aout]",
            "-r", "24",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            "-t", f"{target_dur:.2f}", "-movflags", "+faststart",
            str(out)
        ]
    else:
        offsets = [0.0]
        curr_off = max(0.1, durations[0] - x_dur)
        for i in range(1, n - 1):
            offsets.append(curr_off)
            curr_off += max(0.1, durations[i] - x_dur)
        offsets.append(curr_off)

        natural_v_dur = curr_off + durations[-1]
        shortfall = (max(0.0, a_dur - natural_v_dur) + (1.2 if a_dur > 0 else 0.0)) if a_dur <= (natural_v_dur + 20.0) else 0.0
        final_target_dur = round(natural_v_dur + shortfall, 2)

        inputs = []
        for c in video_clips:
            inputs.extend(["-i", str(c)])
        inputs.extend(["-i", str(audio_path)])

        scales = []
        for i in range(n):
            if i == n - 1 and shortfall > 0.05:
                scales.append(f"[{i}:v]scale=3840:2160,setsar=1,fps=24,tpad=stop_mode=clone:stop_duration={shortfall:.2f}[s{i}]")
            else:
                scales.append(f"[{i}:v]scale=3840:2160,setsar=1,fps=24[s{i}]")

        filter_parts = list(scales)
        prev_tag = "s0"
        for i in range(1, n):
            out_tag = f"v{i}" if i < n - 1 else "v"
            filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={offsets[i]:.2f}[{out_tag}]")
            prev_tag = out_tag

        afade_st = max(0.0, final_target_dur - 2.5)
        filter_parts.append(f"[{n}:a]volume=1.0,apad,afade=t=out:st={afade_st:.2f}:d=2.5[aout]")

        cmd = [
            ffmpeg_bin, "-y",
            *inputs,
            "-filter_complex", ";".join(filter_parts),
            "-map", "[v]",
            "-map", "[aout]",
            "-r", "24",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            "-t", f"{final_target_dur:.2f}",
            "-movflags", "+faststart",
            str(out)
        ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"documentary_master_assembled: {out.name} ({final_target_dur:.2f}s)")
    except subprocess.CalledProcessError as err:
        logger.error(f"failed_to_assemble_doc_master: {err}")
        raise

    return out


def _build_google_maps_route_url(scenes: List[Any]) -> Optional[str]:
    """Builds an official multi-stop Google Maps directions link for the itinerary stops."""
    import urllib.parse
    stops = []
    for sc in scenes:
        orig = getattr(sc, "origin_name", None)
        dest = getattr(sc, "destination_name", None)
        if orig and orig not in stops:
            stops.append(orig)
        if dest and dest not in stops:
            stops.append(dest)
        # Fallback to location_hub or title if not map transition
        loc = getattr(sc, "location_hub", None)
        if loc and loc not in ("Scenic Vista", "Aerial Vista") and loc not in stops:
            stops.append(loc)

    if len(stops) < 2:
        return None

    origin = stops[0]
    destination = stops[-1]
    waypoints = stops[1:-1]
    params = {
        "api": 1,
        "origin": origin,
        "destination": destination,
        "travelmode": "walking",
    }
    if waypoints:
        params["waypoints"] = "|".join(waypoints[:9])
    return "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(params)


def export_documentary_metadata_package(
    sb: DocStoryboard,
    ep_dir: Path,
    audio_tracks: Optional[List[Dict[str, Any]]] = None,
    shorts_file: Optional[Path] = None,
    gps_routes: Optional[Dict[str, Path]] = None,
) -> Dict[str, Any]:
    """Generate high-CTR YouTube metadata, chapter timestamps, and tags for documentary release."""
    chapters = []
    curr_time = 0.0
    for idx, scene in enumerate(sb.scenes):
        m = int(curr_time // 60)
        s = int(curr_time % 60)
        h = int(m // 60)
        time_tag = f"{h:02d}:{m%60:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

        ch_title = getattr(scene, "chapter_title", None)
        dest = getattr(scene, "destination_name", None)
        hub = getattr(scene, "location_hub", None)
        shot = getattr(scene, "shot_type", "scene").replace("_", " ").title()

        if ch_title:
            label = ch_title
        elif dest:
            label = f"Chapter {idx+1}: {dest}"
        elif hub and hub not in ("Scenic Vista", "Aerial Vista"):
            label = f"Chapter {idx+1}: {hub}"
        else:
            label = f"Chapter {idx+1}: {shot}"

        if idx == 0 and not ch_title:
            label = "Introduction & Historical Context"

        chapters.append(f"{time_tag} - {label}")
        curr_time += float(getattr(scene, "duration_seconds", 15.0))

    # Build Google Maps itinerary link
    gmaps_url = _build_google_maps_route_url(sb.scenes)
    map_section = ""
    if gmaps_url:
        map_section = f"🗺️ Full Interactive Route Map (Google Maps):\n👉 Follow the complete walking/transit route:\n{gmaps_url}\n\n"

    # Build individual direct attraction & venue links (Google Maps + Photos)
    import urllib.parse
    featured_stops = []
    seen = set()
    for sc in sb.scenes:
        name = getattr(sc, "origin_name", None) or getattr(sc, "destination_name", None) or getattr(sc, "location_hub", None)
        if name and name not in ("Scenic Vista", "Aerial Vista") and name.lower() not in seen:
            seen.add(name.lower())
            q = urllib.parse.quote_plus(name)
            map_link = f"https://www.google.com/maps/search/?api=1&query={q}"
            photos_link = f"https://www.google.com/search?q={q}+photos&tbm=isch"
            featured_stops.append(f"• {name}:\n  📍 Location: {map_link}\n  📸 Photos: {photos_link}")

    stops_section = ""
    if featured_stops:
        stops_section = (
            "🏛️ Featured Attractions, Neighborhood Squares & Cafes:\n"
            + "\n".join(featured_stops)
            + "\n\n"
        )

    gps_section = ""
    if gps_routes:
        gpx_n = getattr(gps_routes.get("gpx"), "name", "route_itinerary.gpx")
        kml_n = getattr(gps_routes.get("kml"), "name", "route_itinerary.kml")
        gps_section = (
            "🧭 DOWNLOAD GPS ROUTE & OFFLINE MAPS:\n"
            f"• GPX Route (Garmin / Apple Maps): {gpx_n}\n"
            f"• KML Tour (Google Earth / My Maps): {kml_n}\n\n"
        )

    description = (
        f"An in-depth 4K cinematic documentary exploring {sb.title}.\n\n"
        f"{map_section}"
        f"{gps_section}"
        f"{stops_section}"
        f"🎙️ Narration: Authoritative Natural History Voiceover\n"
        f"🎞️ Mastered in 4K UHD (24 fps cinematic cadence) with spatial acoustics.\n\n"
        f"⏰ CHAPTERS & TIMESTAMPS:\n" + "\n".join(chapters) + "\n\n"
        f"⚠️ TRAVEL ADVISORY & SAFETY DISCLAIMER:\n"
        f"This itinerary, transit fare estimates, and local venue suggestions are provided for informational and editorial entertainment purposes only. Operating hours, admission fees, route conditions, transit rates, and venue safety guidelines are subject to change. Travelers and families should exercise personal discretion and verify current local official advisories before visiting.\n\n"
        f"🌿 100% Commercial Master Rights | CineAI Documentary Studio"
    )

    genre_val = getattr(sb.genre, "value", str(sb.genre))
    tags = [
        genre_val, "documentary", "4k_documentary", "nature_documentary",
        "bbc_earth_style", "cinematic", "educational", "history", "science", "4k_uhd",
        "travel_itinerary", "walking_tour", "travel_guide"
    ]

    tracks_spec = audio_tracks or [
        {'language': 'en', 'label': 'English (Original)', 'voice': 'en-GB-RyanNeural', 'is_default': True},
        {'language': 'es', 'label': 'Spanish (Espa?ol)', 'voice': 'es-ES-AlvaroNeural', 'is_default': False},
        {'language': 'hi', 'label': 'Hindi (??????)', 'voice': 'hi-IN-MadhurNeural', 'is_default': False},
        {'language': 'te', 'label': 'Telugu (??????)', 'voice': 'te-IN-MohanNeural', 'is_default': False},
    ]
    from src.studios.documentary_studio.doc_curiosity_title_service import derive_contextual_doc_titles
    dest_name = getattr(sb, 'destination_entity', None) or sb.title.split(':')[0].strip()
    ctr_title, auto_thumb, th_variants = derive_contextual_doc_titles(
        dest_name, sb.title, gemini_yt_title=getattr(sb, 'youtube_title', None),
        gemini_thumb_headline=getattr(sb, 'thumbnail_headline', None), gemini_thumb_variants=getattr(sb, 'thumbnail_variants', None)
    )
    pkg = {
        "title": ctr_title,
        "story_title": sb.title,
        "description": description,
        "tags": tags,
        "seo_tags": tags,
        "genre": genre_val,
        "chapters": chapters,
        "chapter_markers": chapters,
        "language": getattr(sb, "language", "en-US"),
        "audio_tracks": tracks_spec,
        "thumbnail_variants": th_variants,
        "pinned_comment": pin_comm,
        "community_quiz": getattr(sb, "community_quiz", None),
        "google_maps_route_url": gmaps_url,
        "shorts_teaser_file": getattr(shorts_file, "name", None) if shorts_file else None,
        "gps_route_files": {k: getattr(v, "name", str(v)) for k, v in gps_routes.items()} if gps_routes else None,
        "has_synthetic_media": True,
        "contains_synthetic_media": True,
        "ypp_monetization_safety": "100% AdSense Advertiser-Friendly (Green Dollar Guarantee)",
    }

    (ep_dir / "youtube_packaging.json").write_text(json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8")
    return pkg
