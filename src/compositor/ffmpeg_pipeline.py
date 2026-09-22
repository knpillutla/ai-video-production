"""100% Pure Python Single-Pass FFmpeg Compositor constructing -filter_complex CLI graphs."""

import asyncio
import shutil
import subprocess
import sys
from pathlib import Path

from src.compositor.timeline import CompiledTimeline
from src.core.telemetry import logger
from src.scripts.local_audio_ducking import build_timeline_volume_expression
from src.scripts.local_pan_zoom import build_zoompan_expression


def get_ffmpeg_binary() -> str:
    """Resolve FFmpeg binary path from system PATH, imageio_ffmpeg, or local virtualenv."""
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return str(exe)
    except Exception:
        pass

    root = Path(__file__).resolve().parent.parent.parent
    for venv_name in (".venv", "venv"):
        v_dir = root / venv_name
        if v_dir.exists():
            for match in v_dir.glob("**/imageio_ffmpeg/binaries/ffmpeg*.exe"):
                if match.is_file():
                    return str(match)
    return "ffmpeg"


def has_ffmpeg() -> bool:
    """Check if an FFmpeg binary is available on the system or bundled."""
    bin_path = get_ffmpeg_binary()
    return bool(shutil.which(bin_path) or Path(bin_path).exists())


def build_single_pass_command(
    timeline: CompiledTimeline,
    output_path: Path | str,
) -> list[str]:
    """Construct an optimized, single-pass FFmpeg CLI execution command with zero intermediate re-encodings."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd: list[str] = [get_ffmpeg_binary(), "-y"]
    filter_chains: list[str] = []

    # 1. Register visual inputs (true video motion or zoompan over keyframe)
    for idx, sc in enumerate(timeline.scenes):
        if sc.video_path and sc.video_path.exists():
            cmd.extend(["-i", str(sc.video_path)])
            pts_factor = (sc.duration_seconds / 10.0) if sc.duration_seconds > 10.0 else 1.0
            filter_chains.append(
                f"[{idx}:v]setpts={pts_factor:.4f}*(PTS-STARTPTS),scale={timeline.target_resolution[0]}:{timeline.target_resolution[1]}:flags=lanczos,unsharp=lx=5:ly=5:la=0.6:cx=5:cy=5:ca=0.3,fps={timeline.fps},setsar=1[v{idx}]"
            )
        else:
            img_file = sc.image_path or Path("placeholder.png")
            cmd.extend(["-loop", "1", "-t", f"{sc.duration_seconds:.2f}", "-i", str(img_file)])

            # Apply 2.5D camera pan-zoom motion over static keyframe
            zp_filter = build_zoompan_expression(
                movement=sc.camera_movement,
                duration_seconds=sc.duration_seconds,
                fps=timeline.fps,
                target_res=timeline.target_resolution,
            )
            filter_chains.append(f"[{idx}:v]{zp_filter},setsar=1[v{idx}]")

    # 2. Concatenate visual scenes sequentially into [v_concat]
    concat_inputs = "".join(f"[v{i}]" for i in range(len(timeline.scenes)))
    filter_chains.append(f"{concat_inputs}concat=n={len(timeline.scenes)}:v=1:a=0[v_concat]")

    current_v = "[v_concat]"

    # 2b. Optional Film Print LUT Color Grading
    if getattr(timeline, "film_lut", None):
        filter_chains.append(f"{current_v}{timeline.film_lut}[v_graded]")
        current_v = "[v_graded]"

    # 3. Optional subtitle burning filter
    if timeline.subtitle_path and timeline.subtitle_path.exists():
        # Escape path for FFmpeg filter syntax
        sub_escaped = str(timeline.subtitle_path).replace("\\", "/").replace(":", "\\:")
        filter_chains.append(f"{current_v}subtitles='{sub_escaped}'[v_final]")
        current_v = "[v_final]"

    # 4. Audio composition: Multi-track Scene Voices + Ducked BGM + Foley Stem
    input_cursor = len(timeline.scenes)
    bgm_idx = None
    foley_idx = None

    # Register BGM input loop
    if timeline.bgm_path and timeline.bgm_path.exists():
        bgm_idx = input_cursor
        cmd.extend(["-stream_loop", "-1", "-i", str(timeline.bgm_path)])
        input_cursor += 1

    # Register Atmospheric Foley Stem
    if getattr(timeline, "foley_path", None) and timeline.foley_path.exists():
        foley_idx = input_cursor
        cmd.extend(["-stream_loop", "-1", "-i", str(timeline.foley_path)])
        input_cursor += 1

    # Register all scene voiceover stems with exact timeline start-time delays (adelay)
    speech_tags: list[str] = []
    for sc in timeline.scenes:
        if sc.voice_path and sc.voice_path.exists():
            v_idx = input_cursor
            cmd.extend(["-i", str(sc.voice_path)])
            input_cursor += 1
            delay_ms = max(0, int(sc.start_time * 1000))
            tag = f"sp_{sc.scene_index}"
            filter_chains.append(f"[{v_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.2[{tag}]")
            speech_tags.append(f"[{tag}]")

    # Build synchronized multi-track speech stream across all scenes
    has_speech = len(speech_tags) > 0
    if has_speech:
        if len(speech_tags) == 1:
            filter_chains.append(f"{speech_tags[0]}volume=1.0[a_speech]")
        else:
            all_sp = "".join(speech_tags)
            filter_chains.append(f"{all_sp}amix=inputs={len(speech_tags)}:dropout_transition=0:normalize=0[a_speech]")

    # Mix BGM, Foley, and Speech Stems
    duck_expr = build_timeline_volume_expression(timeline.speech_intervals, base_volume=0.35, ducked_volume=0.08) if has_speech else "volume=0.35"
    foley_expr = build_timeline_volume_expression(timeline.speech_intervals, base_volume=0.45, ducked_volume=0.18) if has_speech else "volume=0.45"

    if bgm_idx is not None and foley_idx is not None and has_speech:
        filter_chains.append(f"[{bgm_idx}:a]{duck_expr}[a_ducked]")
        filter_chains.append(f"[{foley_idx}:a]{foley_expr}[a_foley_ducked]")
        filter_chains.append(f"[a_ducked][a_foley_ducked][a_speech]amix=inputs=3:duration=first:dropout_transition=0:weights='0.25 0.35 1.20'[a_out]")
        current_a = "[a_out]"
    elif bgm_idx is not None and has_speech:
        filter_chains.append(f"[{bgm_idx}:a]{duck_expr}[a_ducked]")
        filter_chains.append(f"[a_ducked][a_speech]amix=inputs=2:duration=first:dropout_transition=0:weights='0.30 1.20'[a_out]")
        current_a = "[a_out]"
    elif foley_idx is not None and has_speech:
        filter_chains.append(f"[{foley_idx}:a]{foley_expr}[a_foley_ducked]")
        filter_chains.append(f"[a_foley_ducked][a_speech]amix=inputs=2:duration=first:dropout_transition=0:weights='0.40 1.20'[a_out]")
        current_a = "[a_out]"
    elif has_speech:
        current_a = "[a_speech]"
    elif bgm_idx is not None and foley_idx is not None:
        filter_chains.append(f"[{bgm_idx}:a]volume=0.35[a_bgm_plain]")
        filter_chains.append(f"[{foley_idx}:a]volume=0.45[a_foley_plain]")
        filter_chains.append(f"[a_bgm_plain][a_foley_plain]amix=inputs=2:duration=first:dropout_transition=0:weights='0.50 0.50'[a_out]")
        current_a = "[a_out]"
    elif bgm_idx is not None:
        filter_chains.append(f"[{bgm_idx}:a]volume=0.35[a_out]")
        current_a = "[a_out]"
    elif foley_idx is not None:
        filter_chains.append(f"[{foley_idx}:a]volume=0.45[a_out]")
        current_a = "[a_out]"
    else:
        filter_chains.append(f"anullsrc=channel_layout=stereo:sample_rate=48000:d={timeline.total_duration_seconds:.2f}[a_out]")
        current_a = "[a_out]"
    # 4b. Broadcast Loudness Normalization (-14.0 LUFS EBU R128 standard)
    filter_chains.append(f"{current_a}loudnorm=I=-14.0:TP=-1.0:LRA=7.0[a_norm]")
    current_a = "[a_norm]"

    # 5. Assemble -filter_complex and final encoding parameters
    full_filter_str = ";".join(filter_chains)
    cmd.extend(["-filter_complex", full_filter_str])
    cmd.extend(["-map", current_v, "-map", current_a])

    # Enforce YouTube-optimal broadcast encoding (Directive 14)
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", str(timeline.fps),
        "-threads", "0",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "48000",
        "-t", f"{timeline.total_duration_seconds:.2f}",
        "-movflags", "+faststart",
        str(out),
    ])

    return cmd


from src.compositor.ffmpeg_concat import build_fast_concat_command


async def execute_single_pass_render(
    timeline: CompiledTimeline,
    output_path: Path | str,
    dry_run: bool = False,
) -> Path:
    """Execute the single-pass FFmpeg rendering command asynchronously."""
    out = Path(output_path)
    if out.exists() and out.stat().st_size > 50000:
        logger.info(f"master_render_cache_hit: reusing existing master render {out.name} ({out.stat().st_size} bytes)")
        return out

    cmd = build_single_pass_command(timeline, out)
    logger.info(f"rendering_single_pass: out={out.name}, duration={timeline.total_duration_seconds}s, fps={timeline.fps}")

    if dry_run:
        logger.info("dry_run_enabled: copying minimal valid mp4 container")
        stub_path = Path(__file__).parent / "minimal_valid_master.mp4"
        if stub_path.exists():
            shutil.copyfile(stub_path, out)
        else:
            out.touch()
        return out

    # Run FFmpeg process asynchronously without Windows SelectorEventLoop or console initialization failure
    def _run_ffmpeg():
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=flags,
        )

    proc_res = await asyncio.to_thread(_run_ffmpeg)

    if proc_res.returncode != 0:
        err_msg = proc_res.stderr.decode(errors="replace")[-500:]
        logger.error(f"ffmpeg_render_failed: code={proc_res.returncode}, err={err_msg}")
        raise RuntimeError(f"FFmpeg rendering failed (code {proc_res.returncode}): {err_msg}")

    logger.info(f"render_completed_successfully: {out}")
    return out


__all__ = [
    "build_single_pass_command",
    "execute_single_pass_render",
    "get_ffmpeg_binary",
    "has_ffmpeg",
]
