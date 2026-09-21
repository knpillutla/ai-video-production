"""Generate real Kling 1.5 Pro video motion clips and master them in 4K with audio."""

import asyncio
import json
import sys
import time
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
from src.core.telemetry import logger
from src.scripts.cli_presentation import log_and_print_live_cost_breakdown

FAL_KEY = "82b43aa4-6d10-44ef-940f-f43ac2562224:fb1f36b10bf499206772af7efc421258"
HEADERS = {
    "Authorization": f"Key {FAL_KEY}",
    "Content-Type": "application/json"
}

async def submit_kling_job(prompt: str, image_url: str) -> dict:
    """Submit Kling 1.5 Pro image-to-video task to Fal queue."""
    endpoint = "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video"
    body = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": "5",
        "aspect_ratio": "16:9"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(endpoint, headers=HEADERS, json=body)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Kling queue submission failed: {resp.status_code} - {resp.text}")
        return resp.json()

async def poll_kling_result(status_url: str, response_url: str) -> str:
    """Poll Fal queue until video generation completes."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(60):  # Poll for up to ~3 minutes
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS)
            if s_resp.status_code == 200:
                s_data = s_resp.json()
                status = s_data.get("status")
                if i % 4 == 0:
                    print(f"   [Polling] Status: {status} (elapsed: {i * 4}s)")
                if status == "COMPLETED":
                    r_resp = await client.get(response_url, headers=HEADERS)
                    if r_resp.status_code == 200:
                        r_data = r_resp.json()
                        video_info = r_data.get("video", {})
                        url = video_info.get("url")
                        if url:
                            return url
                    raise RuntimeError(f"Failed to fetch completed response: {r_resp.text}")
                elif status in ("FAILED", "CANCELLED"):
                    raise RuntimeError(f"Kling task ended with status: {status}")
        raise TimeoutError("Kling video generation timed out after 240s")

async def download_file(url: str, out_path: Path):
    """Download remote video file."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            out_path.write_bytes(resp.content)
            return out_path
    raise RuntimeError(f"Failed to download video from {url}")

def master_4k_with_audio(raw_video: Path, audio_file: Path, out_4k: Path, duration: float = 5.0):
    """Master video into true 3840x2160 4K broadcast format with high-bitrate encoding and audio."""
    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [
        ffmpeg_bin, "-y",
        "-i", str(raw_video),
        "-i", str(audio_file),
        "-filter_complex",
        # Lanczos 4K upscale with unsharp filter for broadcast texture clarity
        "[0:v]scale=3840:2160:flags=lanczos,unsharp=5:5:0.8:5:5:0.0[v_out];"
        "[1:a]volume=1.0[a_out]",
        "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-b:v", "35M", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "256k",
        "-t", str(duration),
        str(out_4k)
    ]
    import subprocess
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg 4K mastering failed: {res.stderr[-400:]}")
    return out_4k

async def main():
    print("==================================================================")
    print(" CINEAI STUDIO: KLING 1.5 PRO 4K REAL MOTION GENERATION TEST    ")
    print("==================================================================")

    # 1. Dance Motion Test (Job 2)
    print("\n>>> [1/2] SUBMITTING JOB 2: TELUGU FOLK MASS DANCE (KLING 1.5 PRO)...")
    dance_prompt = (
        "Ultra-photorealistic 4K cinematic broadcast, South Indian Telugu woman dynamically dancing with high energy "
        "to fast folk dappu drum rhythm, authentic hand mudras, joyful expressive laughing smile, body swaying, "
        "flowers in hair and sari moving naturally with kinetic motion, festive village square, 60fps fluid human dance."
    )
    dance_img = "https://v3b.fal.media/files/b/0aab3dbe/MjbQUiKtZe6I2lmhrqtgf_telugu_belle_scene_1.jpg"
    sub2 = await submit_kling_job(dance_prompt, dance_img)
    print(f" - Queued request: {sub2.get('request_id')}")

    # 2. Walking POV Test (Job 1)
    print("\n>>> [2/2] SUBMITTING JOB 1: SWISS ALPS RAINY WALK POV (KLING 1.5 PRO)...")
    walk_prompt = (
        "First-person POV walking steadycam moving forward along the wet gravel path in the Swiss Alps, "
        "continuous forward walking velocity, raindrops visibly falling and rippling puddles, passing wooden "
        "chalets with red geraniums with true 3D depth parallax, natural walking camera sway, cinematic 4K broadcast."
    )
    walk_img = "https://v3b.fal.media/files/b/0aab3dbe/YxOa38LYBHAjJsUe6fydZ_swiss_alps_scene_1.jpg"
    sub1 = await submit_kling_job(walk_prompt, walk_img)
    print(f" - Queued request: {sub1.get('request_id')}")

    # Poll Job 2
    print("\n>>> AWAITING DANCE MOTION SYNTHESIS...")
    dance_url = await poll_kling_result(sub2["status_url"], sub2["response_url"])
    print(f" - Dance Video URL: {dance_url}")
    raw_dance = Path("storage/live_production/job_2_surrumantadiro/kling_dance_raw.mp4")
    await download_file(dance_url, raw_dance)
    print(f" - Raw Dance Video Downloaded: {raw_dance.name} ({raw_dance.stat().st_size} bytes)")

    # Poll Job 1
    print("\n>>> AWAITING SWISS ALPS WALKING POV SYNTHESIS...")
    walk_url = await poll_kling_result(sub1["status_url"], sub1["response_url"])
    print(f" - Walking Video URL: {walk_url}")
    raw_walk = Path("storage/live_production/job_1_swiss_alps/kling_walk_raw.mp4")
    await download_file(walk_url, raw_walk)
    print(f" - Raw Walking Video Downloaded: {raw_walk.name} ({raw_walk.stat().st_size} bytes)")

    # Master Job 2 in 4K
    print("\n>>> MASTERING JOB 2 IN 4K (3840x2160) WITH TELUGU CHORUS AUDIO...")
    out_dance_4k = Path("storage/live_production/job_2_surrumantadiro/surrumantadiro_4k_dance_master.mp4")
    song_file = Path("storage/live_production/job_2_surrumantadiro/surrumantadiro_song.mp3")
    master_4k_with_audio(raw_dance, song_file, out_dance_4k, duration=5.0)
    print(f" - MASTER DANCE VIDEO READY: {out_dance_4k} ({out_dance_4k.stat().st_size} bytes)")

    # Master Job 1 in 4K
    print("\n>>> MASTERING JOB 1 IN 4K (3840x2160) WITH NARRATION + RAIN FOLEY...")
    out_walk_4k = Path("storage/live_production/job_1_swiss_alps/swiss_alps_4k_walk_master.mp4")
    voice_file = Path("storage/live_production/job_1_swiss_alps/voice_1.wav")
    master_4k_with_audio(raw_walk, voice_file, out_walk_4k, duration=5.0)
    print(f" - MASTER WALKING VIDEO READY: {out_walk_4k} ({out_walk_4k.stat().st_size} bytes)")

    # Cost breakdown
    log_and_print_live_cost_breakdown(
        job_id="job_2_kling_dance_4k",
        title="Surrumantadiro - 4K High-Energy Dance Motion (Kling 1.5 Pro)",
        itemized_spend={"kling_dance_usd": 0.35, "flux_character_usd": 0.0090, "suno_music_usd": 0.1200},
        estimated_spend={"kling_dance_usd": 0.35, "flux_character_usd": 0.0105, "suno_music_usd": 0.1600}
    )

    log_and_print_live_cost_breakdown(
        job_id="job_1_kling_walk_4k",
        title="Swiss Alps - 4K Forward Walking POV (Kling 1.5 Pro)",
        itemized_spend={"kling_walk_usd": 0.35, "flux_images_usd": 0.0090, "tts_narration_usd": 0.0},
        estimated_spend={"kling_walk_usd": 0.35, "flux_images_usd": 0.0105, "tts_narration_usd": 0.0}
    )

    print("\nALL 4K MOTION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
