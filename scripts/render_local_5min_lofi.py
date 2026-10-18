"""Render a sustained 5-minute (300s) animated keyframe video locally via FFmpeg.

Features:
- Zero local GPU / Zero API cost ($0.00 spend).
- Multi-harmonic sinusoidal camera drift (organic perpetual steadycam float).
- Gentle breathing zoom (1.00x - 1.05x) that never clips or runs out of room.
- Warm ambient lamp flicker & subtle Lo-Fi film grain texture.
- Seamlessly loops the Telugu Lo-Fi track for the full 5 minutes with smooth audio fadeout.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
import imageio_ffmpeg

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def render_5min_lofi_animation(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    duration_seconds: float = 300.0,
) -> Path:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎬 Starting 5-minute Local Lo-Fi Animation Render")
    print(f"🖼️ Input Keyframe: {image_path.name}")
    print(f"🎵 Input Audio: {audio_path.name} (Looping to {duration_seconds:.0f}s)")
    print(f"📁 Output Video: {output_path}")
    print(f"💰 API Cost: $0.00 (Pure Local CPU FFmpeg)\n")

    t0 = time.time()

    # Multi-harmonic floating camera sway:
    # - Zoom oscillates between 1.01 and 1.05 with a 14-second period
    # - X drift oscillates across 25 pixels with a 21-second period
    # - Y drift oscillates across 12 pixels with a 13-second period
    # The non-matching prime-like periods prevent obvious repeating loops.
    filter_complex = (
        "[0:v]scale=2160:1215,"
        "zoompan=z='1.025+0.025*sin(2*PI*in/336)':"
        "x='(iw-iw/zoom)/2+25*sin(2*PI*in/504)':"
        "y='(ih-ih/zoom)/2+12*cos(2*PI*in/312)':"
        "d=1:s=1920x1080:fps=24,"
        "eq=brightness='0.005*sin(2*PI*t/7)':contrast=1.02:saturation=1.03,"
        "noise=c1s=3:c1f=t+u,"
        "vignette=PI/5[v];"
        f"[1:a]afade=t=out:st={duration_seconds - 5.0:.1f}:d=5.0[a]"
    )

    cmd = [
        ffmpeg_exe, "-y",
        "-loop", "1", "-i", str(image_path),
        "-stream_loop", "-1", "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-t", f"{duration_seconds:.1f}",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart",
        str(output_path),
    ]

    print("⏳ Rendering 7,200 frames (5 minutes at 24 fps)... Please wait ~60-90s.")
    process = subprocess.run(cmd, capture_output=True, text=True)

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed:\n{process.stderr[-1000:]}")

    elapsed = time.time() - t0
    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    print(f"\n✅ 5-Minute Animation Successfully Generated!")
    print(f"⏱️ Render Time: {elapsed:.1f} seconds (~{duration_seconds / elapsed:.1f}x realtime)")
    print(f"📦 File Size: {file_size_mb:.2f} MB")
    print(f"🎥 Output Path: {output_path.resolve()}\n")

    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Render animated keyframe locally via FFmpeg")
    parser.add_argument("--duration", type=float, default=20.0, help="Duration in seconds (default: 20s)")
    parser.add_argument("--output", default="storage/tests/lofi_singer_test/lofi_singer_animated_20s.mp4", help="Output path")
    args = parser.parse_args()

    img_file = Path("storage/tests/lofi_singer_test/character_singer_portrait.jpg")
    aud_file = Path("storage/tests/lofi_singer_test/suno_telugu_lofi_song.mp3")
    out_file = Path(args.output)

    render_5min_lofi_animation(img_file, aud_file, out_file, duration_seconds=args.duration)
