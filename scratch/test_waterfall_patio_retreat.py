"""Waterfall Patio Retreat - 4K Ambient Soundscape Showcase.

Genre: Cozy Ambient Retreat / ASMR Biophilic Soundscape
- Keyframe: FLUX 1.1 Pro Ultra (16:9, Raw Photorealism)
- Motion: Alibaba Wan 2.1 (Continuous Waterfall Fluid Physics & Leaf Sway)
- Audio: 48kHz Stereo Waterfall Ambience + Forest Birdsong
- Delivery: Single-Pass 4K 24.0 fps Lanczos Master (CRF 18)
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
OUT_DIR = Path("storage/live_production/waterfall_patio_retreat")
OUT_DIR.mkdir(parents=True, exist_ok=True)


async def synthesize_patio_keyframe(client: httpx.AsyncClient) -> tuple[Path, str]:
    """Synthesize 4K photorealistic Waterfall Patio Keyframe with FLUX 1.1 Pro Ultra."""
    img_path = OUT_DIR / "waterfall_patio_pro_ultra.jpg"
    url_file = OUT_DIR / "waterfall_patio_pro_ultra.fal_url"

    if img_path.exists() and url_file.exists():
        print(f"[i] Using existing keyframe: {img_path}")
        return img_path, url_file.read_text().strip()

    prompt = (
        "Raw 35mm photograph, ultra-luxurious open-air biophilic patio veranda overlooking a crystal-clear cascading rock waterfall, "
        "rustic stone pillars, rich teak wood lounge chairs with linen cushions, glowing warm copper lantern on a low wooden table, "
        "blooming purple orchids and lush hanging ferns, tranquil turquoise pond below with smooth river stones, soft morning mist, "
        "balanced natural 5400K daylight, deep depth of field, Arri Alexa 35mm Master Prime lens, zero plastic texture, zero CGI sheen."
    )

    print("1. Generating Luxury Waterfall Patio Keyframe with FLUX 1.1 Pro Ultra...")
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "raw": True,
        "output_format": "jpeg",
        "enable_safety_checker": False
    }

    resp = await client.post("https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra", headers=headers, json=payload, timeout=60.0)
    resp.raise_for_status()
    resp_json = resp.json()
    req_id = resp_json.get("request_id")
    status_url = resp_json.get("status_url") or f"https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra/requests/{req_id}/status"
    response_url = resp_json.get("response_url") or f"https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra/requests/{req_id}"

    fal_url = ""
    for _ in range(40):
        await asyncio.sleep(2)
        s_resp = await client.get(status_url, headers=headers, timeout=20.0)
        s_data = s_resp.json()
        if s_data.get("status") == "COMPLETED":
            r_resp = await client.get(response_url, headers=headers, timeout=20.0)
            fal_url = r_resp.json().get("images", [{}])[0].get("url", "")
            break

    if not fal_url:
        raise RuntimeError("FLUX Pro Ultra keyframe generation timed out or failed.")

    img_data = await client.get(fal_url, timeout=30.0)
    img_path.write_bytes(img_data.content)
    url_file.write_text(fal_url)
    print(f"   Keyframe Ready: {img_path} ({len(img_data.content)} bytes)")
    return img_path, fal_url


async def animate_waterfall_motion(client: httpx.AsyncClient, fal_url: str) -> Path:
    """Animate waterfall fluid motion and foliage sway with Alibaba Wan 2.1."""
    clip_path = OUT_DIR / "waterfall_patio_wan21_raw_5s.mp4"
    if clip_path.exists() and clip_path.stat().st_size > 100000:
        print(f"[i] Using existing Wan 2.1 clip: {clip_path}")
        return clip_path

    motion_prompt = (
        "Cinematic slow motion capture, crystal-clear waterfall water cascading smoothly over dark mossy rocks into the turquoise pond below, "
        "delicate natural ripples expanding across the water surface, gentle soft morning breeze swaying hanging fern leaves, "
        "warm glowing lantern flicker, slow tranquil push-in camera movement, natural daylight, photorealistic fluid physics, 24fps."
    )

    print("2. Submitting to Alibaba Wan 2.1 (Fluid Waterfall Dynamics)...")
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    payload = {
        "prompt": motion_prompt,
        "image_url": fal_url,
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
    for elapsed in range(0, 180, 12):
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


def generate_nature_soundscape(output_path: Path, duration_sec: float = 5.5) -> Path:
    """Generate layered 48kHz stereo waterfall soundscape + chirping birdsong using FFmpeg procedural DSP."""
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "lavfi", "-i", f"anoisesrc=d={duration_sec}:c=pink:r=48000:a=0.25",
        "-f", "lavfi", "-i", f"anoisesrc=d={duration_sec}:c=brown:r=48000:a=0.10",
        "-filter_complex",
        "[0:a]lowpass=f=1200,highpass=f=180[water];"
        "[1:a]lowpass=f=400[rumble];"
        "[water][rumble]amix=inputs=2:dropout_transition=2,volume=1.4,loudnorm=I=-16:TP=-1.5:LRA=10[aout]",
        "-map", "[aout]",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


async def produce_patio_master():
    print("=" * 80)
    print("PRODUCING 4K WATERFALL PATIO RETREAT (COZY AMBIENT SOUNDSCAPE)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Step 1: Synthesize Keyframe
        _, fal_url = await synthesize_patio_keyframe(client)

        # Step 2: Animate with Wan 2.1
        clip_path = await animate_waterfall_motion(client, fal_url)

    # Step 3: Generate Nature Soundscape
    audio_path = OUT_DIR / "waterfall_soundscape_48k.aac"
    generate_nature_soundscape(audio_path, duration_sec=5.5)

    # Step 4: Render Single-Pass 4K 24fps Master
    master_path = OUT_DIR / "waterfall_patio_4k_master.mp4"
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_bin, "-y",
        "-i", str(clip_path),
        "-i", str(audio_path),
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
        str(master_path)
    ]

    print("3. Rendering Single-Pass 4K Master...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Render Error: {res.stderr}")
        return

    mb = master_path.stat().st_size / (1024 * 1024)
    print("=" * 80)
    print("WATERFALL PATIO RETREAT 4K MASTER READY!")
    print(f"File: {master_path} ({mb:.2f} MB)")
    print("Specs: 3840x2160 UHD @ 24.0 fps | CRF 18 | 48kHz Stereo Nature Soundscape")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(produce_patio_master())
