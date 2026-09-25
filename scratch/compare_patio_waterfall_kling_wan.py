"""Compare Waterfall Patio Retreat motion on Kling v3 Pro vs Wan 2.1.

Evaluates:
- Kling v3 Pro (High kinematic displacement & volumetric water sheet flow)
- Alibaba Wan 2.1 (Laminar fluid physics with updated fluid momentum prompt)
- Single-pass 4K 24fps Lanczos rendering for both
"""

import asyncio
import os
import sys
import imageio_ffmpeg
import subprocess
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FAL_KEY = os.getenv("FAL_KEY")
OUT_DIR = Path("storage/live_production/waterfall_patio_retreat/comparison")
OUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_URL = "https://v3b.fal.media/files/b/0aabd81b/HaOToa3q1znGNmF6Ocf_o_3200c1fbad274e55b93547193ea8fead.jpg"
AUDIO_PATH = Path("storage/live_production/waterfall_patio_retreat/waterfall_soundscape_48k.aac")


async def run_kling_pro(client: httpx.AsyncClient) -> Path:
    """Submit exact patio keyframe to Kling v3 Pro."""
    clip_path = OUT_DIR / "patio_waterfall_kling_raw_5s.mp4"
    if clip_path.exists() and clip_path.stat().st_size > 100000:
        print(f"[i] Using existing Kling clip: {clip_path}")
        return clip_path

    prompt = (
        "Cinematic slow motion capture, powerful natural rushing waterfall cascading continuously over dark mossy rocks into the turquoise pool below, "
        "heavy volumetric water flow with realistic splashing mist and dynamic ripples on the water surface, gentle tropical breeze swaying hanging bougainvillea and fern leaves, "
        "warm flickering lantern light, slow tranquil forward camera push, photorealistic fluid physics, 24fps."
    )

    print("1. Submitting to Kling v3 Pro (Image-to-Video)...")
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "image_url": IMAGE_URL,
        "duration": "5",
        "aspect_ratio": "16:9"
    }

    resp = await client.post("https://queue.fal.run/fal-ai/kling-video/v3/pro/image-to-video", headers=headers, json=payload, timeout=60.0)
    resp.raise_for_status()
    resp_json = resp.json()
    req_id = resp_json.get("request_id")
    status_url = resp_json.get("status_url") or f"https://queue.fal.run/fal-ai/kling-video/v3/pro/image-to-video/requests/{req_id}/status"
    response_url = resp_json.get("response_url") or f"https://queue.fal.run/fal-ai/kling-video/v3/pro/image-to-video/requests/{req_id}"

    video_url = ""
    for elapsed in range(0, 480, 15):
        await asyncio.sleep(15)
        s_resp = await client.get(status_url, headers=headers, timeout=20.0)
        s_data = s_resp.json()
        status = s_data.get("status")
        print(f"   Kling v3 Pro Status: {status} ({elapsed}s elapsed)")
        if status == "COMPLETED":
            r_resp = await client.get(response_url, headers=headers, timeout=20.0)
            video_url = r_resp.json().get("video", {}).get("url", "")
            break
        if status == "FAILED":
            raise RuntimeError(f"Kling v3 Pro generation failed: {s_data}")

    if not video_url:
        raise RuntimeError("Kling v3 Pro generation timed out.")

    vid_bytes = await client.get(video_url, timeout=60.0)
    clip_path.write_bytes(vid_bytes.content)
    print(f"   Kling v3 Pro Clip Ready: {clip_path} ({len(vid_bytes.content)} bytes)")
    return clip_path


async def run_wan_updated(client: httpx.AsyncClient) -> Path:
    """Submit exact patio keyframe to Alibaba Wan 2.1 with enhanced liquid momentum prompt."""
    clip_path = OUT_DIR / "patio_waterfall_wan21_raw_5s.mp4"
    if clip_path.exists() and clip_path.stat().st_size > 100000:
        print(f"[i] Using existing Wan 2.1 clip: {clip_path}")
        return clip_path

    motion_prompt = (
        "High-momentum fluid dynamic capture, continuous natural water volume rushing and falling over the stone waterfall ledge into the turquoise pool, "
        "heavy liquid displacement with dynamic expanding circular waves across the pool surface, gentle wind swaying the hanging purple flowers, "
        "steady smooth cinematic camera push, natural daylight, zero static streaks, zero wire artifacts, photorealistic fluid physics, 24fps."
    )

    print("2. Submitting to Alibaba Wan 2.1 (Enhanced Fluid Momentum)...")
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    payload = {
        "prompt": motion_prompt,
        "image_url": IMAGE_URL,
        "num_frames": 81,
        "aspect_ratio": "16:9"
    }

    resp = await client.post("https://queue.fal.run/fal-ai/wan-i2v", headers=headers, json=payload, timeout=60.0)
    resp.raise_for_status()
    resp_json = resp.json()
    req_id = resp_json.get("request_id")
    status_url = resp_json.get("status_url") or f"https://queue.fal.run/fal-ai/wan-i2v/requests/{req_id}/status"
    response_url = resp_json.get("response_url") or f"https://queue.fal.run/fal-ai/wan-i2v/requests/{req_id}"

    video_url = ""
    for elapsed in range(0, 240, 12):
        await asyncio.sleep(12)
        s_resp = await client.get(status_url, headers=headers, timeout=20.0)
        s_data = s_resp.json()
        status = s_data.get("status")
        print(f"   Wan 2.1 Status: {status} ({elapsed}s elapsed)")
        if status == "COMPLETED":
            r_resp = await client.get(response_url, headers=headers, timeout=20.0)
            video_url = r_resp.json().get("video", {}).get("url", "")
            break
        if status == "FAILED":
            raise RuntimeError(f"Wan 2.1 generation failed: {s_data}")

    if not video_url:
        raise RuntimeError("Wan 2.1 video generation timed out.")

    vid_bytes = await client.get(video_url, timeout=60.0)
    clip_path.write_bytes(vid_bytes.content)
    print(f"   Wan 2.1 Clip Ready: {clip_path} ({len(vid_bytes.content)} bytes)")
    return clip_path


def render_4k_master(raw_clip: Path, output_master: Path):
    """Render single-pass 4K 24.0 fps master with 48kHz nature audio."""
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin, "-y",
        "-i", str(raw_clip),
        "-i", str(AUDIO_PATH),
        "-filter_complex", "[0:v]scale=3840:2160:flags=lanczos,setsar=1,fps=24[v0]",
        "-map", "[v0]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-shortest",
        "-movflags", "+faststart",
        str(output_master)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"Master Ready: {output_master} ({output_master.stat().st_size / (1024*1024):.2f} MB)")


async def main():
    print("=" * 80)
    print("COMPARING WATERFALL PATIO MOTION: KLING v3 PRO vs ALIBABA WAN 2.1")
    print(f"Keyframe: {IMAGE_URL}")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Run both concurrently
        kling_task = asyncio.create_task(run_kling_pro(client))
        wan_task = asyncio.create_task(run_wan_updated(client))

        kling_clip, wan_clip = await asyncio.gather(kling_task, wan_task)

    print("\n3. Rendering Broadcast 4K Masters...")
    render_4k_master(kling_clip, OUT_DIR / "patio_waterfall_kling_4k_master.mp4")
    render_4k_master(wan_clip, OUT_DIR / "patio_waterfall_wan21_4k_master.mp4")

    print("=" * 80)
    print("COMPARISON COMPLETE!")
    print(f"- Kling v3 Pro 4K: {OUT_DIR / 'patio_waterfall_kling_4k_master.mp4'}")
    print(f"- Wan 2.1 4K:      {OUT_DIR / 'patio_waterfall_wan21_4k_master.mp4'}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
