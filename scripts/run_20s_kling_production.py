"""End-to-End 20-Second Concert Production Test with Kling LipSync ($0.014/s).

Features:
- Unobstructed mouth keyframe (mic held below chin).
- Alibaba Wan 2.1 living base motion ($0.40).
- Kling LipSync (3D diffusion audio-to-video lipsync, $0.014/s).
- Seamless guitar cutaway to prevent looping.
- Single-pass local FFmpeg 48kHz stereo master assembly ($0.00).
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
import imageio_ffmpeg
from src.providers.fal_storage import _fal_api_key, upload_to_fal
from src.providers.visual.fal_wan21 import FalWan21Adapter

MOTION_PROMPT = (
    "Cinematic live concert performance: the cute and stylish South Indian singer gently sways her head and shoulders "
    "to the rhythm while holding the microphone comfortably below her chin, natural blinking, expressive emotional eyes, "
    "subtle chest breathing, charming smile, bright crisp white spotlight illuminating her face and pastel Punjabi dress, "
    "fluid realistic human performance kinematics."
)

NEGATIVE_PROMPT = (
    "microphone covering lips, hand covering mouth, fast jerky movement, robotic motion, "
    "distorted facial features, deformed hands, yellow tint, amber wash."
)

KLING_LIPSYNC_ENDPOINT = "https://queue.fal.run/fal-ai/kling-video/lipsync/audio-to-video"


async def generate_unobstructed_living_video(img_path: Path, out_video: Path) -> Path:
    if out_video.is_file() and out_video.stat().st_size > 500000:
        print(f"  [CACHE HIT] Reusing unobstructed living motion: {out_video.name} ($0.00)")
        return out_video

    print("🎬 Generating 5s Living Motion via Alibaba Wan 2.1 ($0.40)...")
    adapter = FalWan21Adapter()
    _, saved_path = await adapter.generate_video(
        image_url=str(img_path),
        motion_prompt=MOTION_PROMPT,
        output_path=out_video,
        duration=5,
        force_live=True,
        negative_prompt=NEGATIVE_PROMPT,
    )
    return saved_path


async def call_kling_lipsync(video_path: Path, audio_path: Path, out_path: Path, fal_key: str) -> Path:
    if out_path.is_file() and out_path.stat().st_size > 50000:
        print(f"  [CACHE HIT] Reusing Kling lip-synced clip: {out_path.name} ($0.00)")
        return out_path

    print(f"🎤 Calling Kling LipSync ({out_path.name}) at $0.014/sec...")
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}

    # Upload video and audio to Fal storage
    vid_url = await upload_to_fal(video_path, fal_key)
    aud_url = await upload_to_fal(audio_path, fal_key)

    payload = {"video_url": vid_url, "audio_url": aud_url}

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(KLING_LIPSYNC_ENDPOINT, headers=headers, json=payload)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Kling LipSync submit failed: {resp.text}")

        data = resp.json()
        status_url = data.get("status_url")
        response_url = data.get("response_url")

        for attempt in range(60):
            await asyncio.sleep(3.0)
            st = (await client.get(status_url, headers=headers)).json()
            status = st.get("status")
            if status == "COMPLETED":
                res = (await client.get(response_url, headers=headers)).json()
                v_url = res.get("video", {}).get("url") or res.get("video_url")
                if not v_url:
                    raise RuntimeError(f"Kling lipsync response missing video URL: {res}")
                v_content = (await client.get(v_url, timeout=60.0)).content
                out_path.write_bytes(v_content)
                print(f"  ✅ Kling LipSync downloaded: {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)")
                return out_path
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Kling LipSync task failed: {st}")
            if attempt % 4 == 0:
                print(f"  ⏳ Kling LipSync processing... status={status} ({attempt*3}s)")

    raise TimeoutError("Kling LipSync timed out.")


def loop_video_clip(in_video: Path, out_video: Path, dur: float) -> Path:
    if out_video.is_file() and out_video.stat().st_size > 50000:
        return out_video
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-stream_loop", "-1", "-i", str(in_video),
        "-t", f"{dur:.2f}", "-c:v", "copy", "-an", str(out_video),
    ]
    subprocess.run(cmd, check=True)
    return out_video


def slice_audio_clip(in_audio: Path, out_audio: Path, ss: float, t: float) -> Path:
    if out_audio.is_file() and out_audio.stat().st_size > 5000:
        return out_audio
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-ss", f"{ss:.2f}", "-i", str(in_audio),
        "-t", f"{t:.2f}", "-c:a", "libmp3lame", "-b:a", "192k", str(out_audio),
    ]
    subprocess.run(cmd, check=True)
    return out_audio


def assemble_20s_video(cuts: list[Path], master_audio: Path, out_master: Path) -> Path:
    print(f"\n🎬 Assembling final 20s concert video ({len(cuts)} cuts) & 48kHz stereo master...")
    concat_txt = out_master.parent / "test20_concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in cuts), encoding="utf-8")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(master_audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart",
        str(out_master),
    ]
    subprocess.run(cmd, check=True)
    return out_master


async def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    trimmed_audio = out_dir / "trimmed_vocal_20s.mp3"
    keyframe_img = out_dir / "unobstructed_singer_keyframe.png"
    guitar_video = out_dir / "shot2_acoustic_guitar_5s.mp4"
    final_master = out_dir / "master_telugu_concert_20s_test.mp4"

    fal_key = _fal_api_key()
    t0 = time.time()

    print("=====================================================================")
    print("🎬 20-Second Live Concert Production Test (Kling LipSync)")
    print(f"🎵 Audio: {trimmed_audio.name} (0s-3s intro pickup, 3s-20s active vocals)")
    print("💰 Total Estimated Cost: ~$0.55")
    print("=====================================================================\n")

    # Step 1: Living Base Video via Wan 2.1 ($0.40)
    living_base = await generate_unobstructed_living_video(
        keyframe_img, out_dir / "unobstructed_living_motion_5s.mp4"
    )

    # Step 2: Cut 1: 0.0s - 3.0s (3s) -> Guitar intro pickup ($0.00)
    c1 = loop_video_clip(guitar_video, out_dir / "test20_cut1_guitar_3s.mp4", 3.0)

    # Step 3: Cut 2: 3.0s - 14.0s (11s) -> Active Telugu Singing with Kling LipSync ($0.15)
    vocal_audio_11s = slice_audio_clip(trimmed_audio, out_dir / "test20_vocal_11s.mp3", ss=3.0, t=11.0)
    looped_base_11s = loop_video_clip(living_base, out_dir / "test20_base_loop_11s.mp4", 11.0)
    c2 = await call_kling_lipsync(looped_base_11s, vocal_audio_11s, out_dir / "test20_cut2_singing_11s.mp4", fal_key)

    # Step 4: Cut 3: 14.0s - 17.0s (3s) -> Guitar strumming cutaway ($0.00)
    c3 = loop_video_clip(guitar_video, out_dir / "test20_cut3_guitar_3s.mp4", 3.0)

    # Step 5: Cut 4: 17.0s - 20.0s (3s) -> Vocal climax close-up ($0.04)
    vocal_audio_3s = slice_audio_clip(trimmed_audio, out_dir / "test20_vocal_3s.mp3", ss=17.0, t=3.0)
    looped_base_3s = loop_video_clip(living_base, out_dir / "test20_base_loop_3s.mp4", 3.0)
    c4 = await call_kling_lipsync(looped_base_3s, vocal_audio_3s, out_dir / "test20_cut4_singing_3s.mp4", fal_key)

    # Step 6: Assemble final 20s master
    cuts = [c1, c2, c3, c4]
    master = assemble_20s_video(cuts, trimmed_audio, final_master)

    elapsed = time.time() - t0
    size_mb = master.stat().st_size / (1024 * 1024)

    print("\n=====================================================================")
    print("🎉 20-Second End-to-End Concert Test Complete!")
    print(f"⏱️ Total Time: {elapsed:.1f}s")
    print(f"📦 File Size: {size_mb:.2f} MB")
    print(f"🎥 Master Video: {master}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
