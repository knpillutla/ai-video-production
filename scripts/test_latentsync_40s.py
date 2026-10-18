"""Test ByteDance LatentSync on a 40-second looped living Wan 2.1 video base.

Cost: $0.20 flat (Fal.ai LatentSync up to 40 seconds).
Hardware: Zero local GPU (Local CPU FFmpeg + Fal Cloud API).
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import imageio_ffmpeg
from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter


def prepare_40s_assets(
    base_video: Path,
    song_audio: Path,
    out_dir: Path,
    duration: float = 40.0,
) -> tuple[Path, Path]:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out_looped = out_dir / f"looped_base_{int(duration)}s.mp4"
    out_sliced_audio = out_dir / f"song_slice_{int(duration)}s.mp3"

    # Step 1: Loop the 5s living Wan video to 40 seconds
    if not out_looped.is_file() or out_looped.stat().st_size < 100000:
        print(f"🎬 Looping 5s Wan living video to {duration:.0f}s via local FFmpeg ($0.00)...")
        cmd_v = [
            ffmpeg, "-y", "-nostats", "-loglevel", "error",
            "-stream_loop", "-1", "-i", str(base_video),
            "-t", f"{duration:.2f}",
            "-c:v", "copy", "-an",
            str(out_looped),
        ]
        subprocess.run(cmd_v, check=True)
        print(f"  ✅ Looped base ready: {out_looped.name} ({out_looped.stat().st_size / (1024*1024):.2f} MB)")
    else:
        print(f"  [CACHE HIT] Looped base already on disk: {out_looped.name} ($0.00)")

    # Step 2: Slice the first 40 seconds of the song audio
    if not out_sliced_audio.is_file() or out_sliced_audio.stat().st_size < 10000:
        print(f"🎵 Slicing {duration:.0f}s of Telugu Lo-Fi song ($0.00)...")
        cmd_a = [
            ffmpeg, "-y", "-nostats", "-loglevel", "error",
            "-ss", "0.0", "-i", str(song_audio),
            "-t", f"{duration:.2f}",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(out_sliced_audio),
        ]
        subprocess.run(cmd_a, check=True)
        print(f"  ✅ Sliced audio ready: {out_sliced_audio.name}")
    else:
        print(f"  [CACHE HIT] Sliced audio already on disk: {out_sliced_audio.name} ($0.00)")

    return out_looped, out_sliced_audio


async def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    base_video = out_dir / "character_living_motion_5s.mp4"
    song_audio = out_dir / "suno_telugu_lofi_song.mp3"
    target_out = out_dir / "lofi_singer_latentsync_40s.mp4"

    if not base_video.is_file():
        raise FileNotFoundError(f"Base video missing at {base_video}")
    if not song_audio.is_file():
        raise FileNotFoundError(f"Song audio missing at {song_audio}")

    print("=====================================================================")
    print("🎤 Starting ByteDance LatentSync (40s Singing Test)")
    print(f"🎬 Base Living Motion: {base_video.name}")
    print(f"🎵 Song Audio: {song_audio.name}")
    print("💰 API Cost: $0.20 flat (Fal.ai LatentSync up to 40s)")
    print("=====================================================================\n")

    t0 = time.time()

    # 1. Prepare 40s assets locally
    looped_video, sliced_audio = prepare_40s_assets(base_video, song_audio, out_dir, duration=40.0)

    # 2. Call Fal LatentSync
    print(f"\n🚀 Dispatching to Fal LatentSync (uploading {looped_video.name} & animating)...")
    adapter = FalLatentSyncAdapter()
    result_path = await adapter.lipsync_video(
        video_url=str(looped_video),
        audio_path=sliced_audio,
        output_path=target_out,
        force_live=True,
    )

    elapsed = time.time() - t0
    size_mb = Path(result_path).stat().st_size / (1024 * 1024)

    print("\n=====================================================================")
    print("✅ LatentSync 40-Second Video Complete!")
    print(f"⏱️ Finished in {elapsed:.1f}s")
    print(f"📦 File Size: {size_mb:.2f} MB")
    print(f"🎥 Local Path: {result_path}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
