"""Live Production Test: Wild Canada Nature Documentary (Single 5s Test Shot - Hunyuan + Flux Pro Ultra).

Adheres to:
- Directive 8: Single test shot to minimize cost (~$0.37 total API cost).
- Directive 14: Cinematic 24.0 fps, 4K CRF 18 Lanczos mastering, 48kHz audio.
- Reuses existing FLUX 1.1 Pro Ultra keyframe (zero redundant image cost).
- Uses Fal endpoint: fal-ai/hunyuan-video-image-to-video.
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

OUTPUT_DIR = Path("storage/live_production/wild_canada_hunyuan_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _extract_video_url(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    val = payload.get("video")
    if isinstance(val, dict) and val.get("url"):
        return str(val["url"])
    if isinstance(val, str) and val.startswith("http"):
        return val
    out_val = payload.get("output")
    if isinstance(out_val, dict):
        if isinstance(out_val.get("video"), dict) and out_val["video"].get("url"):
            return str(out_val["video"]["url"])
        if isinstance(out_val.get("video"), str) and out_val["video"].startswith("http"):
            return str(out_val["video"])
        if isinstance(out_val.get("url"), str) and out_val["url"].startswith("http"):
            return str(out_val["url"])
    f_val = payload.get("file")
    if isinstance(f_val, dict) and f_val.get("url"):
        return str(f_val["url"])
    if isinstance(payload.get("url"), str) and payload["url"].startswith("http"):
        return str(payload["url"])
    for v in payload.values():
        if isinstance(v, str) and (v.endswith(".mp4") or "fal.media" in v):
            return v
        if isinstance(v, dict) and isinstance(v.get("url"), str) and ("fal.media" in v["url"] or v["url"].endswith(".mp4")):
            return str(v["url"])
    return None


async def get_flux_pro_ultra_keyframe() -> tuple[str, Path]:
    """Retrieve or generate 16:9 Ultra-HD keyframe with FLUX 1.1 Pro Ultra."""
    local_img = OUTPUT_DIR / "shot_1_keyframe_pro_ultra.jpg"
    if local_img.exists() and local_img.stat().st_size > 500_000:
        print(f"[i] Reusing existing FLUX Pro Ultra keyframe: {local_img.name} ({local_img.stat().st_size} bytes)", flush=True)
        return f"file://{local_img}", local_img

    endpoint = "https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra"
    prompt = (
        "Ultra-photorealistic 8K cinematic landscape of Canadian Rockies Lake Moraine in Banff National Park. "
        "Majestic granite peaks with snow dusted ridges, pristine turquoise glacial water, emerald pine forest, "
        "soft morning mist, crisp balanced 5500K daylight, deep optical focal depth."
    )
    payload = {"prompt": prompt, "aspect_ratio": "16:9", "output_format": "jpeg", "raw": True}
    print("1. Synthesizing Ultra-HD Keyframe with FLUX 1.1 Pro Ultra...", flush=True)
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
                print(f"   Keyframe Ready: {local_img.name} ({len(img_bytes)} bytes)", flush=True)
                return img_url, local_img
        raise TimeoutError("Flux Pro Ultra keyframe timed out")


async def generate_hunyuan_clip(image_url: str) -> tuple[str, Path]:
    """Generate 5s native 1080p motion using Tencent Hunyuan Video on Fal.ai."""
    actual_img_url = image_url
    if actual_img_url.startswith("file://"):
        from src.providers.fal_storage import upload_to_fal
        actual_img_url = await upload_to_fal(Path(actual_img_url.replace("file://", "")), api_key=FAL_KEY)

    endpoint = "https://queue.fal.run/fal-ai/hunyuan-video-image-to-video"
    prompt = (
        "Ultra-photorealistic 4K cinematic BBC Planet Earth documentary aerial camera glide slowly descending "
        "and pushing forward over pristine turquoise glacial waters toward towering snow-capped Rocky Mountain peaks, "
        "slow expansive camera motion, 24fps film cadence, zero high-speed rush."
    )
    payload = {"prompt": prompt, "image_url": actual_img_url}
    print("2. Submitting single test motion to Hunyuan Video 1080p (fal-ai/hunyuan-video-image-to-video)...", flush=True)

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        if sub.status_code not in (200, 201, 202):
            raise RuntimeError(f"Hunyuan submit failed: {sub.status_code} - {sub.text}")
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")
        print(f"   [i] Successfully connected to Hunyuan endpoint: {endpoint}")

    local_vid = OUTPUT_DIR / "hunyuan_test_raw_5s.mp4"
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        for i in range(225):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS, params={"logs": "1"})
            res_data = s_resp.json()
            status = res_data.get("status")
            if i % 4 == 0:
                print(f"   Hunyuan Status: {status} ({i*4}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                if not vid_url:
                    raise RuntimeError(f"Could not extract video url from response: {final_res}")

                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Hunyuan 1080p Clip Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return vid_url, local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Hunyuan task failed: {res_data}")
        raise TimeoutError("Hunyuan generation timed out (exceeded 15m)")


async def generate_narration_and_score_5s() -> tuple[Path, Path]:
    """Synthesize 5-second measured BBC nature narration and grand orchestral score."""
    import edge_tts

    narration_text = "In the heart of the Canadian wilderness, ancient glaciers carved towering monuments of granite."
    voice_file = OUTPUT_DIR / "wild_canada_narration_5s.mp3"
    communicate = edge_tts.Communicate(narration_text, "en-GB-RyanNeural", rate="-6%")
    await communicate.save(str(voice_file))

    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    bgm_file = OUTPUT_DIR / "wild_canada_orchestral_5s.mp3"
    synth_cmd = [
        exe, "-y",
        "-f", "lavfi", "-i", "sine=frequency=130.81:sample_rate=48000:duration=6",
        "-f", "lavfi", "-i", "sine=frequency=196.00:sample_rate=48000:duration=6",
        "-f", "lavfi", "-i", "anoisesrc=sample_rate=48000:amplitude=0.012:color=pink:duration=6",
        "-filter_complex",
        "[0:a]volume=0.22[c];[1:a]volume=0.18[g];[2:a]lowpass=f=350,volume=0.28[wind];"
        "[c][g][wind]amix=inputs=3:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "256k",
        str(bgm_file)
    ]
    subprocess.run(synth_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return voice_file, bgm_file


async def master_4k_documentary(video_clip: Path, narration: Path, bgm: Path) -> Path:
    """Master to 24.0 fps 4K UHD with Lanczos upscaling and sidechain audio ducking."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    final_master = OUTPUT_DIR / "wild_canada_hunyuan_4k_master.mp4"

    filter_complex = (
        "[0:v]scale=3840:2160:flags=lanczos,fps=24[vmaster];"
        "[2:a]volume=0.55[bgm_base];"
        "[1:a][bgm_base]sidechaincompress=threshold=0.07:ratio=6:attack=50:release=450[ducked_bgm];"
        "[1:a][ducked_bgm]amix=inputs=2:dropout_transition=2:normalize=0[mixed_audio];"
        "[mixed_audio]loudnorm=I=-14:TP=-1.0:LRA=7[amaster]"
    )

    cmd = [
        exe, "-y",
        "-i", str(video_clip),
        "-i", str(narration),
        "-i", str(bgm),
        "-filter_complex", filter_complex,
        "-map", "[vmaster]",
        "-map", "[amaster]",
        "-shortest",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(final_master)
    ]
    print("3. Executing Single-Pass 4K 24fps Mastering...", flush=True)
    subprocess.run(cmd, check=True)
    print(f"4K Hunyuan Master Ready: {final_master.name} ({final_master.stat().st_size} bytes)", flush=True)
    return final_master


async def main():
    print("=================================================================")
    print("[*] COST-SAVING TEST: HUNYUAN 1080p + FLUX 1.1 PRO ULTRA")
    print("=================================================================\n")

    img_url, local_img = await get_flux_pro_ultra_keyframe()
    vid_url, local_vid = await generate_hunyuan_clip(img_url)
    narration, bgm = await generate_narration_and_score_5s()
    master = await master_4k_documentary(local_vid, narration, bgm)

    print("\n=================================================================")
    print(f"[+] 4K HUNYUAN MASTER READY: {master}")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
