"""Cineloop Utility for transforming AI diffusion clips into seamless loops."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import imageio_ffmpeg

from src.core.telemetry import logger

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def get_media_duration(media_path: Path) -> float:
    """Probe the exact duration of a media file in seconds."""
    try:
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run(
            [ffmpeg_bin, "-i", str(media_path)],
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=_SUBPROCESS_FLAGS,
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            return float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3))
    except Exception:
        pass
    return 5.0


def build_seamless_forward_cineloop(clip_path: Path, xfade_dur: float = 1.2, crf: int = 22) -> Path:
    """Transform short 5s/10s AI diffusion motion clip into an infinitely loopable cineloop."""
    if clip_path.name.endswith("_fwd_seamless.mp4") and clip_path.is_file():
        return clip_path

    base_stem = clip_path.stem.replace("_fwd_seamless", "")
    sp_file = clip_path.parent / "screenplay.json"
    if "p" in base_stem and sp_file.is_file():
        try:
            sp = json.loads(sp_file.read_text(encoding="utf-8"))
            idx = int("".join(filter(str.isdigit, base_stem)) or "1")
            scs = sp.get("scenes", [])
            if idx - 1 < len(scs) and scs[idx - 1].get("motion_type") in ("ken_burns", "static", "local_zoompan"):
                return clip_path
        except Exception:
            pass

    out_seamless = clip_path.parent / f"{base_stem}_fwd_seamless.mp4"
    duration = get_media_duration(clip_path)
    if duration <= xfade_dur + 0.5 or duration >= 25.0:
        return clip_path

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    has_audio = False
    try:
        check = subprocess.run(
            [ffmpeg_bin, "-i", str(clip_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore",
            creationflags=_SUBPROCESS_FLAGS,
        )
        has_audio = "Audio:" in check.stderr
    except Exception:
        pass

    if out_seamless.is_file() and out_seamless.stat().st_size > 1000 and out_seamless.stat().st_mtime >= clip_path.stat().st_mtime:
        return out_seamless

    split_offset = max(0.1, duration - xfade_dur)
    v_xf = f"[0:v]split=2[h][t];[t]trim=start={split_offset:.2f}:end={duration:.2f},setpts=PTS-STARTPTS,fps=24[t1];[h]trim=start=0:end={split_offset:.2f},setpts=PTS-STARTPTS,fps=24[h1];[t1][h1]xfade=transition=fade:duration={xfade_dur:.2f}:offset=0,fps=24,format=yuv420p[v]"
    f_graph = f"{v_xf};[0:a]atrim=0:{split_offset:.2f},asetpts=PTS-STARTPTS[a]" if has_audio else v_xf
    cmd = [
        ffmpeg_bin, "-y", "-nostats", "-loglevel", "error", "-i", str(clip_path),
        "-filter_complex", f_graph, "-map", "[v]",
        *(["-map", "[a]"] if has_audio else []),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
        *(["-c:a", "aac", "-b:a", "320k", "-ar", "48000"] if has_audio else []),
        str(out_seamless),
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True, creationflags=_SUBPROCESS_FLAGS)
        return out_seamless
    except subprocess.CalledProcessError as err:
        logger.warning(f"failed_to_build_seamless_loop: {(err.stderr or str(err)).strip()}")
        return clip_path


def ensure_thumbnail_intro_clip(
    ep_dir: Optional[Path],
    duration_sec: float = 2.0,
    fps: int = 24,
    crf: int = 22,
) -> Optional[Path]:
    """Render a 4K 24fps video intro card from thumbnail.jpg so YouTube's frame 0 is the high-CTR thumbnail."""
    if not ep_dir:
        return None
    ep = Path(ep_dir)
    thumb_img = next((p for p in [ep / "thumbnail.jpg", ep / "thumbnail_a.jpg", ep / "thumbnail.png"] if p.is_file() and p.stat().st_size > 1000), None)
    if not thumb_img:
        return None
    out_clip = ep / "thumbnail_intro.mp4"
    if out_clip.is_file() and out_clip.stat().st_size > 1000 and out_clip.stat().st_mtime >= thumb_img.stat().st_mtime:
        return out_clip
    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-nostats", "-loglevel", "error",
        "-loop", "1", "-i", str(thumb_img),
        "-t", f"{duration_sec:.2f}",
        "-vf", f"scale=3840:2160,setsar=1,fps={fps}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", str(crf),
        "-movflags", "+faststart", str(out_clip),
    ]
    try:
        subprocess.run(cmd, check=True, creationflags=_SUBPROCESS_FLAGS)
        return out_clip if out_clip.is_file() else None
    except Exception as ex:
        logger.warning(f"failed_to_build_thumbnail_intro: {ex}")
        return None

