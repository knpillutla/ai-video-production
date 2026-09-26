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
) -> Path:
    """Assemble seamless 4K 24fps documentary master with dynamic crossfades and optimized CRF 22 encoding."""
    out = output_master.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.is_file() and out.stat().st_size > 1000:
        return out

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    n = len(video_clips)
    durations = [_probe_clip_duration(c) for c in video_clips]
    x_dur = 1.0

    if n == 1:
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(video_clips[0]),
            "-i", str(audio_path),
            "-r", "24",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            "-shortest", "-movflags", "+faststart",
            str(out)
        ]
    else:
        inputs = []
        for c in video_clips:
            inputs.extend(["-i", str(c)])
        inputs.extend(["-i", str(audio_path)])

        scales = [f"[{i}:v]scale=3840:2160,setsar=1,fps=24[s{i}]" for i in range(n)]
        filter_parts = list(scales)
        prev_tag = "s0"
        curr_offset = max(0.1, durations[0] - x_dur)

        for i in range(1, n):
            out_tag = f"v{i}" if i < n - 1 else "v"
            filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={curr_offset:.2f}[{out_tag}]")
            prev_tag = out_tag
            clip_dur = durations[i] if i < len(durations) else 15.0
            curr_offset += max(0.1, clip_dur - x_dur)

        cmd = [
            ffmpeg_bin, "-y",
            *inputs,
            "-filter_complex", ";".join(filter_parts),
            "-map", "[v]",
            "-map", f"{n}:a",
            "-r", "24",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            "-shortest", "-movflags", "+faststart",
            str(out)
        ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"documentary_master_assembled: {out.name}")
    except subprocess.CalledProcessError as err:
        logger.error(f"failed_to_assemble_doc_master: {err}")
        raise

    return out


def export_documentary_metadata_package(
    sb: DocStoryboard,
    ep_dir: Path,
) -> Dict[str, Any]:
    """Generate high-CTR YouTube metadata, chapter timestamps, and tags for documentary release."""
    chapters = ["00:00 🎬 Introduction & Historical Context"]
    curr_time = 0.0
    for idx, scene in enumerate(sb.scenes):
        if idx > 0:
            m = int(curr_time // 60)
            s = int(curr_time % 60)
            chapters.append(f"{m:02d}:{s:02d} 🌿 Chapter {idx+1}: {scene.shot_type.title()} Focus")
        curr_time += scene.duration_seconds

    description = (
        f"An in-depth 4K cinematic documentary exploring {sb.title}.\n\n"
        f"🎙️ Narration: Authoritative Natural History Voiceover\n"
        f"🎞️ Mastered in 4K UHD (24 fps cinematic cadence) with spatial acoustics.\n\n"
        f"⏰ Documentary Chapters:\n" + "\n".join(chapters) + "\n\n"
        f"🌿 100% Commercial Master Rights | CineAI Documentary Studio"
    )

    tags = [
        sb.genre.value, "documentary", "4k_documentary", "nature_documentary",
        "bbc_earth_style", "cinematic", "educational", "history", "science", "4k_uhd"
    ]

    pkg = {
        "title": f"{sb.title} [4K UHD Cinematic Documentary]",
        "description": description,
        "tags": tags,
        "genre": sb.genre.value,
        "chapters": chapters,
        "language": sb.language,
    }

    (ep_dir / "youtube_packaging.json").write_text(json.dumps(pkg, indent=2), encoding="utf-8")
    return pkg
