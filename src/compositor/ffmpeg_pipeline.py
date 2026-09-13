"""100% Pure Python Single-Pass FFmpeg Compositor constructing -filter_complex CLI graphs."""

import asyncio
import shutil
from pathlib import Path

from src.compositor.timeline import CompiledTimeline
from src.core.telemetry import logger
from src.scripts.local_audio_ducking import build_timeline_volume_expression
from src.scripts.local_pan_zoom import build_zoompan_expression


def get_ffmpeg_binary() -> str:
    """Resolve FFmpeg binary path from system PATH or imageio_ffmpeg fallback."""
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def has_ffmpeg() -> bool:
    """Check if an FFmpeg binary is available on the system or bundled."""
    if shutil.which("ffmpeg"):
        return True
    try:
        import imageio_ffmpeg

        return bool(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return False


def build_single_pass_command(
    timeline: CompiledTimeline,
    output_path: Path | str,
) -> list[str]:
    """Construct an optimized, single-pass FFmpeg CLI execution command with zero intermediate re-encodings."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd: list[str] = [get_ffmpeg_binary(), "-y"]
    filter_chains: list[str] = []

    # 1. Register image inputs and build visual zoompan streams
    for idx, sc in enumerate(timeline.scenes):
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

    # 3. Optional subtitle burning filter
    if timeline.subtitle_path and timeline.subtitle_path.exists():
        # Escape path for FFmpeg filter syntax
        sub_escaped = str(timeline.subtitle_path).replace("\\", "/").replace(":", "\\:")
        filter_chains.append(f"{current_v}subtitles='{sub_escaped}'[v_final]")
        current_v = "[v_final]"

    # 4. Audio composition: Multi-track Scene Voices + Ducked BGM
    input_cursor = len(timeline.scenes)
    bgm_idx = None

    # Register BGM input loop
    if timeline.bgm_path and timeline.bgm_path.exists():
        bgm_idx = input_cursor
        cmd.extend(["-stream_loop", "-1", "-i", str(timeline.bgm_path)])
        input_cursor += 1

    # Register all scene voiceover stems
    voice_inputs: list[int] = []
    for sc in timeline.scenes:
        if sc.voice_path and sc.voice_path.exists():
            voice_inputs.append(input_cursor)
            cmd.extend(["-i", str(sc.voice_path)])
            input_cursor += 1

    # Build speech stream
    has_speech = len(voice_inputs) > 0
    if has_speech:
        if len(voice_inputs) == 1:
            filter_chains.append(f"[{voice_inputs[0]}:a]volume=1.2[a_speech]")
        else:
            voice_tags = "".join(f"[{v_idx}:a]" for v_idx in voice_inputs)
            filter_chains.append(f"{voice_tags}concat=n={len(voice_inputs)}:v=0:a=1,volume=1.2[a_speech]")

    # Mix BGM and Speech
    if bgm_idx is not None and has_speech:
        duck_expr = build_timeline_volume_expression(timeline.speech_intervals, base_volume=0.35, ducked_volume=0.08)
        filter_chains.append(f"[{bgm_idx}:a]{duck_expr}[a_ducked]")
        filter_chains.append(f"[a_ducked][a_speech]amix=inputs=2:duration=first:dropout_transition=0:weights='0.30 1.20'[a_out]")
        current_a = "[a_out]"
    elif has_speech:
        current_a = "[a_speech]"
    elif bgm_idx is not None:
        filter_chains.append(f"[{bgm_idx}:a]volume=0.35[a_out]")
        current_a = "[a_out]"
    else:
        filter_chains.append(f"anullsrc=channel_layout=stereo:sample_rate=48000:d={timeline.total_duration_seconds:.2f}[a_out]")
        current_a = "[a_out]"

    # 5. Assemble -filter_complex and final encoding parameters
    full_filter_str = ";".join(filter_chains)
    cmd.extend(["-filter_complex", full_filter_str])
    cmd.extend(["-map", current_v, "-map", current_a])

    # Enforce YouTube-optimal broadcast encoding
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        "-t", f"{timeline.total_duration_seconds:.2f}",
        "-movflags", "+faststart",
        str(out),
    ])

    return cmd


async def execute_single_pass_render(
    timeline: CompiledTimeline,
    output_path: Path | str,
    dry_run: bool = False,
) -> Path:
    """Execute the single-pass FFmpeg rendering command asynchronously."""
    out = Path(output_path)
    cmd = build_single_pass_command(timeline, out)
    cmd_str = " ".join(cmd[:12]) + " ... (single-pass filter_complex)"
    logger.info(f"rendering_single_pass: out={out.name}, duration={timeline.total_duration_seconds}s")

    if dry_run:
        logger.info("dry_run_enabled: skipping ffmpeg process launch")
        out.touch()
        return out

    # Run FFmpeg process asynchronously
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err_msg = stderr.decode(errors="replace")[-500:]
        logger.error(f"ffmpeg_render_failed: code={proc.returncode}, err={err_msg}")
        raise RuntimeError(f"FFmpeg rendering failed (code {proc.returncode}): {err_msg}")

    logger.info(f"render_completed_successfully: {out}")
    return out


__all__ = [
    "build_single_pass_command",
    "execute_single_pass_render",
    "get_ffmpeg_binary",
    "has_ffmpeg",
]
