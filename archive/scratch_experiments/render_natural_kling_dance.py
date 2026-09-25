import asyncio
import httpx
import subprocess
from pathlib import Path
from PIL import Image
import numpy as np
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

FAL_KEY = "82b43aa4-6d10-44ef-940f-f43ac2562224:fb1f36b10bf499206772af7efc421258"
HEADERS = {
    "Authorization": f"Key {FAL_KEY}",
    "Content-Type": "application/json"
}

IMAGE_URL = "https://v3b.fal.media/files/b/0aab3e09/a-Gn6qhLAUI7ez3hRO3Wt.jpg"

async def main():
    print("=== Submitting Natural Daylight Dance to Kling 1.5 Pro (Single 5s Test) ===")
    prompt = (
        "Ultra-photorealistic 4K cinematic broadcast, 24-year-old South Indian woman dynamically dancing with joyful energy "
        "in the open-air rustic village courtyard under natural crisp daylight, fluid authentic hand mudras and waist sway, "
        "crimson saree moving with realistic physics, natural smile, fluid human motion, zero lens flare, balanced natural lighting."
    )
    endpoint = "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video"
    payload = {
        "prompt": prompt,
        "image_url": IMAGE_URL,
        "duration": "5",
        "aspect_ratio": "16:9"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        print(f"Queued Kling task: {sub_data.get('request_id')}")
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")

    video_url = None
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(60):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS)
            status = s_resp.json().get("status")
            if i % 3 == 0:
                print(f"Status: {status} ({i*4}s elapsed)")
            if status == "COMPLETED":
                r = await client.get(response_url, headers=HEADERS)
                video_url = r.json().get("video", {}).get("url")
                break
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Kling failed with status {status}")

    if not video_url:
        raise TimeoutError("Kling video synthesis timed out")

    print(f"Kling Video Ready: {video_url}")
    out_dir = Path("storage/live_production/job_2_surrumantadiro")
    raw_video = out_dir / "natural_daylight_kling_raw.mp4"

    async with httpx.AsyncClient(timeout=60.0) as client:
        v_bytes = (await client.get(video_url)).content
        raw_video.write_bytes(v_bytes)
    print(f"Downloaded raw Kling video: {raw_video.stat().st_size} bytes")

    # Master to 4K with audio sync
    audio_file = out_dir / "surrumantadiro_song.mp3"
    master_4k = out_dir / "surrumantadiro_natural_daylight_4k_master.mp4"
    ffmpeg_bin = get_ffmpeg_binary()

    cmd = [
        ffmpeg_bin, "-y",
        "-i", str(raw_video),
        "-i", str(audio_file),
        "-filter_complex",
        "[0:v]scale=3840:2160:flags=lanczos,unsharp=5:5:0.8:5:5:0.0[v_out];"
        "[1:a]volume=1.0[a_out]",
        "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-b:v", "35M", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "256k",
        "-t", "5.0",
        str(master_4k)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg mastering failed: {res.stderr[-400:]}")
    print(f"4K Master Created: {master_4k.name} ({master_4k.stat().st_size} bytes)")

    # Extract sample frame from new master to compute warmth index
    sample_dir = Path("scratch/analysis/natural_dance_master")
    sample_dir.mkdir(parents=True, exist_ok=True)
    extract_cmd = [
        ffmpeg_bin, "-y", "-i", str(master_4k),
        "-vf", "fps=1", "-vframes", "3",
        str(sample_dir / "frame_%02d.jpg")
    ]
    subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    frames = list(sample_dir.glob("frame_*.jpg"))
    if frames:
        arr = np.array(Image.open(frames[0]).convert("RGB"), dtype=np.float32)
        r, g, b = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
        yellow_cast = ((r + g) / 2.0) - b
        print(f"\n=== Color Verification on Final Video Frame ===")
        print(f"RGB Means: R={r:.1f}, G={g:.1f}, B={b:.1f}")
        print(f"Warmth / Yellow Cast Index: {yellow_cast:.1f} (Original overblown yellow was +61.2)")

if __name__ == "__main__":
    asyncio.run(main())
