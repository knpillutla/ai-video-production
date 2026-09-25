"""River Water Dynamics Comparison: Linear Downstream Flow (Hunyuan 1080p vs Wan 2.1).

Features:
- Generates 1 new clean downstream river keyframe with FLUX 1.1 Pro Ultra (smooth laminar water, zero frozen splatter).
- Renders Motion with Hunyuan Video 1080p (downstream push-in).
- Renders Motion with Wan 2.1 (downstream push-in).
- Masters both to 4K 24fps Lanczos with identical BBC voiceover and French horn/cello score.
- Extracts snapshot frames for side-by-side water fluid analysis.
"""

import asyncio
import os
import sys
import subprocess
import httpx
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
if hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

OUTPUT_DIR = Path("storage/live_production/river_water_comparison")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _extract_video_url(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    for k in ("video", "output", "file"):
        v = payload.get(k)
        if isinstance(v, dict) and v.get("url"):
            return str(v["url"])
        if isinstance(v, str) and v.startswith("http"):
            return v
    for v in payload.values():
        if isinstance(v, str) and (v.endswith(".mp4") or "fal.media" in v):
            return v
        if isinstance(v, dict) and isinstance(v.get("url"), str) and ("fal.media" in v["url"] or v["url"].endswith(".mp4")):
            return str(v["url"])
    return None


async def get_or_generate_river_keyframe() -> tuple[str, Path]:
    """Generate clean downstream river keyframe with FLUX 1.1 Pro Ultra."""
    local_img = OUTPUT_DIR / "river_downstream_pro_ultra.jpg"
    if local_img.exists() and local_img.stat().st_size > 500_000:
        print(f"[i] Reusing existing river keyframe: {local_img.name}", flush=True)
        from src.providers.fal_storage import upload_to_fal
        img_url = await upload_to_fal(local_img, api_key=FAL_KEY)
        return img_url, local_img

    endpoint = "https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra"
    prompt = (
        "Ultra-photorealistic 8K cinematic landscape looking downstream along a majestic turquoise mountain river "
        "flowing smoothly through a dense emerald pine forest in Banff National Park. Continuous smooth glassy water surface, "
        "gentle natural ripples, towering granite peaks in the distant background, soft morning mist, crisp balanced 5400K natural daylight, "
        "deep optical depth-of-field, Arri Alexa 35mm Master Prime lens, zero frozen splash splatter, zero plastic sheen."
    )
    payload = {"prompt": prompt, "aspect_ratio": "16:9", "output_format": "jpeg", "raw": True}
    print("1. Synthesizing Clean Downstream River Keyframe with FLUX 1.1 Pro Ultra...", flush=True)

    async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")

        for _ in range(40):
            await asyncio.sleep(2)
            s = await client.get(status_url, headers=HEADERS)
            if s.json().get("status") == "COMPLETED":
                res = (await client.get(resp_url, headers=HEADERS)).json()
                img_url = res.get("images", [{}])[0].get("url") or res.get("image", {}).get("url")
                img_bytes = (await client.get(img_url)).content
                local_img.write_bytes(img_bytes)
                print(f"   River Keyframe Ready: {local_img.name} ({len(img_bytes)} bytes)", flush=True)
                return img_url, local_img
        raise TimeoutError("River keyframe generation timed out")


async def render_hunyuan_river(image_url: str) -> Path:
    """Render 5s downstream river motion with Hunyuan Video 1080p."""
    local_vid = OUTPUT_DIR / "river_hunyuan_raw_5s.mp4"
    if local_vid.exists() and local_vid.stat().st_size > 1_000_000:
        print(f"[i] Reusing existing Hunyuan clip: {local_vid.name}")
        return local_vid

    endpoint = "https://queue.fal.run/fal-ai/hunyuan-video-image-to-video"
    prompt = (
        "Cinematic 24fps camera slowly pushing forward looking downstream as the turquoise glacial river flows naturally "
        "away through the emerald pine forest, smooth laminar water ripples, realistic gentle fluid motion, deep optical perspective."
    )
    payload = {"prompt": prompt, "image_url": image_url}
    print("2A. Submitting river motion to Hunyuan Video 1080p...", flush=True)

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        for i in range(225):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS, params={"logs": "1"})
            res_data = s_resp.json()
            status = res_data.get("status")
            if i % 5 == 0:
                print(f"   Hunyuan River Status: {status} ({i*4}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Hunyuan River Clip Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Hunyuan task failed: {res_data}")
        raise TimeoutError("Hunyuan river timed out")


async def render_wan21_river(image_url: str) -> Path:
    """Render 5s downstream river motion with Alibaba Wan 2.1."""
    local_vid = OUTPUT_DIR / "river_wan21_raw_5s.mp4"
    if local_vid.exists() and local_vid.stat().st_size > 1_000_000:
        print(f"[i] Reusing existing Wan 2.1 clip: {local_vid.name}")
        return local_vid

    endpoint = "https://queue.fal.run/fal-ai/wan-i2v"
    prompt = (
        "Cinematic 24fps camera slowly pushing forward looking downstream as the turquoise glacial river flows naturally "
        "away through the emerald pine forest, smooth laminar water ripples, realistic gentle fluid motion, deep optical perspective."
    )
    payload = {"prompt": prompt, "image_url": image_url}
    print("2B. Submitting river motion to Alibaba Wan 2.1...", flush=True)

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        for i in range(120):
            await asyncio.sleep(3)
            s_resp = await client.get(status_url, headers=HEADERS, params={"logs": "1"})
            res_data = s_resp.json()
            status = res_data.get("status")
            if i % 4 == 0:
                print(f"   Wan 2.1 River Status: {status} ({i*3}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Wan 2.1 River Clip Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Wan 2.1 task failed: {res_data}")
        raise TimeoutError("Wan 2.1 river timed out")


def master_river_clip(raw_clip: Path, name: str) -> Path:
    """Master single river clip to 4K Lanczos with narration & audio."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_master = OUTPUT_DIR / f"river_{name}_4k_master.mp4"

    # Reuse audio stems from 3-shot ep1
    voice = Path("storage/live_production/wild_canada_hunyuan_test/wild_canada_narration_5s.mp3")
    score = Path("storage/live_production/wild_canada_hunyuan_test/wild_canada_orchestral_5s.mp3")

    filter_complex = (
        "[0:v]fps=24,scale=3840:2160:flags=lanczos,setsar=1[v4k];"
        "[2:a]volume=0.18[bgm_quiet];"
        "[1:a][bgm_quiet]amix=inputs=2:duration=first:dropout_transition=0,volume=1.3[aout]"
    )

    cmd = [
        exe, "-y",
        "-i", str(raw_clip),
        "-i", str(voice),
        "-i", str(score),
        "-filter_complex", filter_complex,
        "-map", "[v4k]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-movflags", "+faststart",
        str(out_master)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Extract snapshot frame
    snap_frame = OUTPUT_DIR / f"river_{name}_snapshot_f2s.jpg"
    snap_cmd = [exe, "-y", "-ss", "2.0", "-i", str(out_master), "-vframes", "1", "-q:v", "2", str(snap_frame)]
    subprocess.run(snap_cmd, check=True, capture_output=True)
    print(f"Master Complete: {out_master.name}")
    return out_master


async def main():
    print("================================================================================")
    print("RIVER WATER DYNAMICS: Hunyuan 1080p vs Wan 2.1 (Downstream Linear Flow)")
    print("================================================================================")
    img_url, img_path = await get_or_generate_river_keyframe()
    
    # Run Hunyuan and Wan 2.1 concurrently
    h_task = render_hunyuan_river(img_url)
    w_task = render_wan21_river(img_url)
    h_vid, w_vid = await asyncio.gather(h_task, w_task)

    h_master = master_river_clip(h_vid, "hunyuan")
    w_master = master_river_clip(w_vid, "wan21")
    print("================================================================================")
    print("COMPARISON COMPLETE!")
    print(f"- Hunyuan 4K Master: {h_master}")
    print(f"- Wan 2.1 4K Master: {w_master}")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(main())
