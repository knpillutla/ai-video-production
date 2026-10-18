"""Master Script: Produce Final Live Acoustic Concert Music Video.

Pipeline:
1. Shot 3: Intimate Chorus Close-Up (Flux Dev $0.02 + Wan 2.1 $0.40).
2. LatentSync Lip-Sync on Verse 1 (Shot 1) and Chorus (Shot 3) ($0.20 x 2 = $0.40).
3. Local FFmpeg Director Multi-Cut Assembly & 48kHz Stereo Master Mux ($0.00).
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
from src.providers.fal_storage import _fal_api_key
from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter
from src.providers.visual.fal_wan21 import FalWan21Adapter

SHOT3_KEYFRAME_PROMPT = (
    "Award-winning 4K live concert photograph, intimate 85mm portrait close-up of the cute and beautiful 24-year-old South Indian singer "
    "singing passionately into a vintage chrome condenser microphone on stage. "
    "Expressive emotional eyes, subtle charming smile, delicate silver jhumki earrings catching the light, modern pastel georgette neckline visible. "
    "Lighting: bright crisp neutral white 5600K studio spotlight beautifully illuminating her radiant skin and hair with sharp clarity, "
    "cool deep indigo-blue ambient concert stage with soft-focus audience bokeh in the background, crystal clear 4K portrait, Coke Studio aesthetic."
)

SHOT3_MOTION_PROMPT = (
    "Cinematic live concert close-up: the cute South Indian singer gently tilts her head with the emotional melody, "
    "subtle natural blinking, expressive emotional eyes, gentle chest breathing, glowing white spotlight catching her hair, "
    "fluid realistic human performance kinematics."
)

NEGATIVE_PROMPT = (
    "deformed face, twitching, fast jerky movement, robotic motion, yellow tint, amber wash, "
    "golden hour flare, blurry eyes, low resolution."
)


async def generate_shot3(out_dir: Path, fal_key: str) -> Path:
    img_path = out_dir / "shot3_chorus_closeup_keyframe.jpg"
    video_path = out_dir / "shot3_chorus_closeup_5s.mp4"

    # Step 1: Shot 3 Keyframe (~$0.02)
    if not img_path.is_file() or img_path.stat().st_size < 10000:
        print("📸 Generating Shot 3 Close-Up Keyframe via Flux Dev (~$0.02)...")
        headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
        payload = {
            "prompt": SHOT3_KEYFRAME_PROMPT,
            "negative_prompt": NEGATIVE_PROMPT,
            "image_size": "landscape_16_9",
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post("https://queue.fal.run/fal-ai/flux/dev", headers=headers, json=payload)
            data = resp.json()
            status_url, response_url = data.get("status_url"), data.get("response_url")
            for _ in range(40):
                await asyncio.sleep(2.0)
                st = (await client.get(status_url, headers=headers)).json()
                if st.get("status") == "COMPLETED":
                    res = (await client.get(response_url, headers=headers)).json()
                    img_path.write_bytes((await client.get(res["images"][0]["url"])).content)
                    break
        print(f"  ✅ Shot 3 Keyframe ready: {img_path.name}")
    else:
        print(f"  [CACHE HIT] Reusing Shot 3 keyframe: {img_path.name} ($0.00)")

    # Step 2: Shot 3 Wan 2.1 Motion ($0.40)
    if not video_path.is_file() or video_path.stat().st_size < 500000:
        print("🎬 Generating Shot 3 5s Living Motion via Alibaba Wan 2.1 ($0.40)...")
        adapter = FalWan21Adapter()
        _, saved_video = await adapter.generate_video(
            image_url=str(img_path),
            motion_prompt=SHOT3_MOTION_PROMPT,
            output_path=video_path,
            duration=5,
            force_live=True,
            negative_prompt=NEGATIVE_PROMPT,
        )
        return saved_video
    else:
        print(f"  [CACHE HIT] Reusing Shot 3 video: {video_path.name} ($0.00)")
        return video_path


def slice_audio(full_audio: Path, out_path: Path, start_s: float, dur_s: float) -> Path:
    if out_path.is_file() and out_path.stat().st_size > 5000:
        return out_path
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-ss", f"{start_s:.2f}", "-i", str(full_audio),
        "-t", f"{dur_s:.2f}", "-c:a", "libmp3lame", "-b:a", "192k", str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path


def loop_video(in_video: Path, out_video: Path, target_dur: float) -> Path:
    if out_video.is_file() and out_video.stat().st_size > 50000:
        return out_video
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-stream_loop", "-1", "-i", str(in_video),
        "-t", f"{target_dur:.2f}", "-c:v", "copy", "-an", str(out_video),
    ]
    subprocess.run(cmd, check=True)
    return out_video


async def apply_latentsync(base_video: Path, audio_slice: Path, out_video: Path, dur_s: float) -> Path:
    if out_video.is_file() and out_video.stat().st_size > 50000:
        print(f"  [CACHE HIT] Reusing lip-synced video: {out_video.name} ($0.00)")
        return out_video

    raw_loop = out_video.parent / f"tmp_loop_{out_video.name}"
    loop_video(base_video, raw_loop, dur_s)

    print(f"🎤 Applying LatentSync ({dur_s:.1f}s) to {out_video.name} ($0.20)...")
    adapter = FalLatentSyncAdapter()
    res = await adapter.lipsync_video(
        video_url=str(raw_loop),
        audio_path=audio_slice,
        output_path=out_video,
        force_live=True,
    )
    raw_loop.unlink(missing_ok=True)
    return Path(res)


def assemble_final_concert_video(cut_list: list[Path], full_audio: Path, final_video: Path) -> Path:
    print(f"\n🎬 Assembling final multi-camera concert video ({len(cut_list)} cuts) via local FFmpeg ($0.00)...")
    concat_txt = final_video.parent / "concert_concat_list.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in cut_list), encoding="utf-8")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(full_audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart",
        str(final_video),
    ]
    subprocess.run(cmd, check=True)
    return final_video


async def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    full_audio = out_dir / "suno_telugu_lofi_song.mp3"
    shot1_video = out_dir / "stage_singer_living_motion_5s.mp4"
    shot2_video = out_dir / "shot2_acoustic_guitar_5s.mp4"
    final_video = out_dir / "master_telugu_lofi_concert_video.mp4"

    fal_key = _fal_api_key()
    t0 = time.time()

    print("=====================================================================")
    print("🎬 MASTER PRODUCTION: Telugu Lo-Fi Live Acoustic Concert Video")
    print("📁 Output Directory: storage/tests/lofi_singer_test")
    print("💰 Total Remaining Budget: ~$0.82 (Shot 3 $0.42 + LatentSync $0.40)")
    print("=====================================================================\n")

    # 1. Shot 3 Generation
    shot3_video = await generate_shot3(out_dir, fal_key)

    # 2. Singing Lip-Sync Passes
    # Verse 1 (18.0s - 38.0s = 20s) -> Shot 1 Front Stage
    verse_audio = slice_audio(full_audio, out_dir / "vocal_verse1_20s.mp3", start_s=18.0, dur_s=20.0)
    singing_verse = await apply_latentsync(shot1_video, verse_audio, out_dir / "scene_verse1_singing.mp4", dur_s=20.0)

    # Chorus (48.0s - 72.0s = 24s) -> Shot 3 Close-Up
    chorus_audio = slice_audio(full_audio, out_dir / "vocal_chorus_24s.mp3", start_s=48.0, dur_s=24.0)
    singing_chorus = await apply_latentsync(shot3_video, chorus_audio, out_dir / "scene_chorus_singing.mp4", dur_s=24.0)

    # 3. Create Multi-Camera Cuts
    # Cut 1: Intro Guitar (0-6s)
    c1 = loop_video(shot2_video, out_dir / "cut1_intro_guitar_6s.mp4", 6.0)
    # Cut 2: Intro Singer Smiling (6-12s)
    c2 = loop_video(shot1_video, out_dir / "cut2_intro_singer_6s.mp4", 6.0)
    # Cut 3: Intro Guitar Swell (12-18s)
    c3 = loop_video(shot2_video, out_dir / "cut3_intro_guitar_6s.mp4", 6.0)
    # Cut 4: Verse 1 Front Singing (18-38s)
    c4 = singing_verse
    # Cut 5: Interlude Guitar Strumming (38-43s)
    c5 = loop_video(shot2_video, out_dir / "cut5_interlude_guitar_5s.mp4", 5.0)
    # Cut 6: Interlude Singer Nodding to Crowd (43-48s)
    c6 = loop_video(shot1_video, out_dir / "cut6_interlude_singer_5s.mp4", 5.0)
    # Cut 7: Chorus Climax Close-Up Singing (48-72s)
    c7 = singing_chorus
    # Cut 8: Outro Singer Smiling & Applause (72-79s)
    c8 = loop_video(shot1_video, out_dir / "cut8_outro_singer_7s.mp4", 7.0)
    # Cut 9: Outro Final Guitar Resolve (79-85.6s)
    c9 = loop_video(shot2_video, out_dir / "cut9_outro_guitar_6.6s.mp4", 6.6)

    cuts = [c1, c2, c3, c4, c5, c6, c7, c8, c9]

    # 4. Final Single-Pass Assembly & 48kHz Mastering
    master_out = assemble_final_concert_video(cuts, full_audio, final_video)

    elapsed = time.time() - t0
    size_mb = master_out.stat().st_size / (1024 * 1024)

    print("\n=====================================================================")
    print("🎉 MASTER LIVE CONCERT VIDEO 100% COMPLETE & BROADCAST READY!")
    print(f"⏱️ Total Production Time: {elapsed:.1f}s")
    print(f"📦 Final File Size: {size_mb:.2f} MB")
    print(f"🎥 Master Video Path: {master_out}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
