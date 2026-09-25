"""Re-test Exact Shot 2 Keyframe with Updated Water Physics Motion Prompt (Hunyuan 1080p vs Wan 2.1).

Uses the exact 2.12 MB image:
`storage/live_production/wild_canada_hunyuan_3shot_ep1/shot_2_keyframe_pro_ultra.jpg`

Applies the updated Directive 20 motion prompt:
- Downstream linear flow alignment
- Explicit fluid negative tokens (zero gelatinous morphing, zero foam melting)
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

OUTPUT_DIR = Path("storage/live_production/shot2_exact_retest")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SRC_SHOT2_IMG = Path("storage/live_production/wild_canada_hunyuan_3shot_ep1/shot_2_keyframe_pro_ultra.jpg")
SRC_URL_FILE = Path("storage/live_production/wild_canada_hunyuan_3shot_ep1/shot_2_keyframe.fal_url")

UPDATED_MOTION_PROMPT = (
    "Cinematic 24fps camera slowly pushing forward looking downstream, smooth continuous fluid water motion "
    "cascading over granite boulders, natural laminar water flow, realistic river surface displacement, "
    "zero gelatinous morphing, zero frozen foam melting, 24fps film cadence."
)


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


async def get_shot2_url() -> tuple[str, Path]:
    """Retrieve Fal URL for the exact existing Shot 2 keyframe."""
    if not SRC_SHOT2_IMG.exists():
        raise FileNotFoundError(f"Shot 2 image not found at {SRC_SHOT2_IMG}")

    if SRC_URL_FILE.exists():
        cached_url = SRC_URL_FILE.read_text().strip()
        if cached_url.startswith("http"):
            print(f"[i] Using cached Shot 2 Fal URL: {cached_url}", flush=True)
            return cached_url, SRC_SHOT2_IMG

    from src.providers.fal_storage import upload_to_fal
    print(f"Uploading existing Shot 2 image ({SRC_SHOT2_IMG.stat().st_size} bytes)...", flush=True)
    uploaded_url = await upload_to_fal(SRC_SHOT2_IMG, api_key=FAL_KEY)
    SRC_URL_FILE.write_text(uploaded_url)
    return uploaded_url, SRC_SHOT2_IMG


async def render_hunyuan_shot2(image_url: str) -> Path:
    """Render Shot 2 with Hunyuan Video 1080p using updated prompt."""
    local_vid = OUTPUT_DIR / "shot2_updated_hunyuan_raw_5s.mp4"
    endpoint = "https://queue.fal.run/fal-ai/hunyuan-video-image-to-video"
    payload = {"prompt": UPDATED_MOTION_PROMPT, "image_url": image_url}
    print("1. Submitting exact Shot 2 image to Hunyuan Video 1080p with updated fluid prompt...", flush=True)

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
                print(f"   Hunyuan Status: {status} ({i*4}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Hunyuan Shot 2 Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Hunyuan task failed: {res_data}")
        raise TimeoutError("Hunyuan generation timed out")


async def render_wan21_shot2(image_url: str) -> Path:
    """Render Shot 2 with Alibaba Wan 2.1 using updated prompt."""
    local_vid = OUTPUT_DIR / "shot2_updated_wan21_raw_5s.mp4"
    endpoint = "https://queue.fal.run/fal-ai/wan-i2v"
    payload = {"prompt": UPDATED_MOTION_PROMPT, "image_url": image_url}
    print("2. Submitting exact Shot 2 image to Alibaba Wan 2.1 with updated fluid prompt...", flush=True)

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
                print(f"   Wan 2.1 Status: {status} ({i*3}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Wan 2.1 Shot 2 Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Wan 2.1 task failed: {res_data}")
        raise TimeoutError("Wan 2.1 generation timed out")


def master_clip_4k(raw_clip: Path, model_name: str) -> Path:
    """Master to 4K Lanczos with narration and orchestral BGM."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_master = OUTPUT_DIR / f"shot2_exact_{model_name}_4k_master.mp4"

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

    snap_frame = OUTPUT_DIR / f"shot2_exact_{model_name}_f2s.jpg"
    snap_cmd = [exe, "-y", "-ss", "2.0", "-i", str(out_master), "-vframes", "1", "-q:v", "2", str(snap_frame)]
    subprocess.run(snap_cmd, check=True, capture_output=True)
    print(f"Master Complete: {out_master.name}")
    return out_master


async def main():
    print("================================================================================")
    print("RE-TESTING EXACT SHOT 2 KEYFRAME WITH UPDATED WATER FLUID MOTION PROMPT")
    print(f"Image: {SRC_SHOT2_IMG} ({SRC_SHOT2_IMG.stat().st_size} bytes)")
    print("================================================================================")
    img_url, img_path = await get_shot2_url()

    # Run Hunyuan and Wan 2.1 concurrently on the exact same keyframe
    h_task = render_hunyuan_shot2(img_url)
    w_task = render_wan21_shot2(img_url)
    h_vid, w_vid = await asyncio.gather(h_task, w_task)

    h_master = master_clip_4k(h_vid, "hunyuan")
    w_master = master_clip_4k(w_vid, "wan21")

    print("================================================================================")
    print("RE-TEST COMPLETE ON EXACT SHOT 2 IMAGE!")
    print(f"- Hunyuan 4K Master: {h_master}")
    print(f"- Wan 2.1 4K Master: {w_master}")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(main())
