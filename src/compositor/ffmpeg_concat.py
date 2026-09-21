"""Fast Stream-Copy FFmpeg Concat Generator (-f concat -safe 0 -c:v copy)."""

from pathlib import Path

from src.compositor.timeline import CompiledTimeline
from src.scripts.local_audio_ducking import build_timeline_volume_expression


def build_fast_concat_command(
    timeline: CompiledTimeline,
    output_path: Path,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str] | None:
    """Construct ultra-fast stream-copy concat command (-f concat -safe 0 -c:v copy) in < 1.5s."""
    if not (timeline.scenes and all(sc.video_path and sc.video_path.exists() for sc in timeline.scenes)):
        return None

    concat_txt = output_path.parent / "concat_inputs.txt"
    lines = [f"file '{str(sc.video_path.resolve()).replace(chr(92), '/')}'" for sc in timeline.scenes if sc.video_path]
    concat_txt.write_text("\n".join(lines), encoding="utf-8")

    cmd: list[str] = [ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt.resolve())]

    # Mix audio stems with stream-copied video
    input_cursor = 1
    bgm_idx, foley_idx = None, None
    if timeline.bgm_path and timeline.bgm_path.exists():
        bgm_idx = input_cursor
        cmd.extend(["-stream_loop", "-1", "-i", str(timeline.bgm_path)])
        input_cursor += 1

    if getattr(timeline, "foley_path", None) and timeline.foley_path.exists():
        foley_idx = input_cursor
        cmd.extend(["-stream_loop", "-1", "-i", str(timeline.foley_path)])
        input_cursor += 1

    voice_inputs = []
    for sc in timeline.scenes:
        if sc.voice_path and sc.voice_path.exists():
            voice_inputs.append(input_cursor)
            cmd.extend(["-i", str(sc.voice_path)])
            input_cursor += 1

    if bgm_idx is None and foley_idx is None and not voice_inputs:
        cmd.extend(["-c", "copy", "-movflags", "+faststart", str(output_path)])
        return cmd

    filter_chains = []
    has_speech = len(voice_inputs) > 0
    if has_speech:
        if len(voice_inputs) == 1:
            filter_chains.append(f"[{voice_inputs[0]}:a]volume=1.2[a_speech]")
        else:
            voice_tags = "".join(f"[{v}:a]" for v in voice_inputs)
            filter_chains.append(f"{voice_tags}concat=n={len(voice_inputs)}:v=0:a=1,volume=1.2[a_speech]")

    duck_expr = build_timeline_volume_expression(timeline.speech_intervals, base_volume=0.35, ducked_volume=0.08) if has_speech else "volume=0.35"
    foley_expr = build_timeline_volume_expression(timeline.speech_intervals, base_volume=0.45, ducked_volume=0.18) if has_speech else "volume=0.45"

    if bgm_idx is not None and foley_idx is not None and has_speech:
        filter_chains.append(f"[{bgm_idx}:a]{duck_expr}[a_ducked]")
        filter_chains.append(f"[{foley_idx}:a]{foley_expr}[a_foley_ducked]")
        filter_chains.append(f"[a_ducked][a_foley_ducked][a_speech]amix=inputs=3:duration=first:dropout_transition=0:weights='0.25 0.35 1.20'[a_mix]")
        current_a = "[a_mix]"
    elif bgm_idx is not None and has_speech:
        filter_chains.append(f"[{bgm_idx}:a]{duck_expr}[a_ducked]")
        filter_chains.append(f"[a_ducked][a_speech]amix=inputs=2:duration=first:dropout_transition=0:weights='0.30 1.20'[a_mix]")
        current_a = "[a_mix]"
    elif foley_idx is not None and has_speech:
        filter_chains.append(f"[{foley_idx}:a]{foley_expr}[a_foley_ducked]")
        filter_chains.append(f"[a_foley_ducked][a_speech]amix=inputs=2:duration=first:dropout_transition=0:weights='0.40 1.20'[a_mix]")
        current_a = "[a_mix]"
    elif has_speech:
        current_a = "[a_speech]"
    elif bgm_idx is not None and foley_idx is not None:
        filter_chains.append(f"[{bgm_idx}:a]volume=0.35[a_bgm_plain]")
        filter_chains.append(f"[{foley_idx}:a]volume=0.45[a_foley_plain]")
        filter_chains.append(f"[a_bgm_plain][a_foley_plain]amix=inputs=2:duration=first:dropout_transition=0:weights='0.50 0.50'[a_mix]")
        current_a = "[a_mix]"
    elif bgm_idx is not None:
        filter_chains.append(f"[{bgm_idx}:a]volume=0.35[a_mix]")
        current_a = "[a_mix]"
    else:
        filter_chains.append(f"anullsrc=channel_layout=stereo:sample_rate=48000:d={timeline.total_duration_seconds:.2f}[a_mix]")
        current_a = "[a_mix]"

    filter_chains.append(f"{current_a}loudnorm=I=-14.0:TP=-1.0:LRA=7.0[a_norm]")

    cmd.extend([
        "-filter_complex", ";".join(filter_chains),
        "-map", "0:v", "-map", "[a_norm]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", f"{timeline.total_duration_seconds:.2f}",
        "-movflags", "+faststart",
        str(output_path),
    ])
    return cmd


__all__ = ["build_fast_concat_command"]
