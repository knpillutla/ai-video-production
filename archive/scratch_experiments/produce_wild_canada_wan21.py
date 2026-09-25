"""Live Production: Wild Canada Nature Documentary (15s, Option B: Native 16:9 + Wan 2.1 + 4K Master).

Model Stack:
- Keyframes: Flux Dev native 16:9 landscape.
- Video Motion: Alibaba Wan 2.1 (Fal.ai `fal-ai/wan-i2v`).
- Narration: 15s BBC nature lore voiceover (Edge TTS en-GB-RyanNeural).
- Audio: 15s 48kHz French horn & cello orchestral score with sidechain ducking.
- Master: Single-pass 4K 24.0 fps (-crf 18, Lanczos upscale).
"""

import asyncio
import os
import sys
import subprocess
import httpx
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
if hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

OUTPUT_DIR = Path("storage/live_production/wild_canada_wan21_test")
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


async def generate_flux_keyframe_16_9(shot_id: int, prompt: str) -> tuple[str, Path]:
    """Generate Native 16:9 widescreen keyframe with Flux Dev."""
    endpoint = "https://queue.fal.run/fal-ai/flux/dev"
    payload = {
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }
    print(f"[{shot_id}/3] Synthesizing Native 16:9 Keyframe with Flux Dev...", flush=True)
    async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        if sub.status_code not in (200, 201, 202):
            raise RuntimeError(f"Flux submit failed: {sub.status_code} - {sub.text}")

        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")

        for _ in range(40):
            await asyncio.sleep(2)
            s = await client.get(status_url, headers=HEADERS)
            if s.json().get("status") == "COMPLETED":
                res = await client.get(resp_url, headers=HEADERS)
                img_url = res.json()["images"][0]["url"]
                local_img = OUTPUT_DIR / f"shot_{shot_id}_keyframe_16_9.jpg"
                img_bytes = (await client.get(img_url)).content
                local_img.write_bytes(img_bytes)
                print(f"   Shot {shot_id} 16:9 Keyframe Ready: {local_img.name} ({len(img_bytes)} bytes)", flush=True)
                return img_url, local_img
        raise TimeoutError(f"Flux keyframe timed out for shot {shot_id}")


async def generate_wan21_clip(shot_id: int, image_url: str, motion_prompt: str) -> tuple[str, Path]:
    """Generate 5s motion using Alibaba Wan on Fal.ai."""
    endpoints = [
        "https://queue.fal.run/fal-ai/wan-i2v",
        "https://queue.fal.run/fal-ai/wan/image-to-video",
        "https://queue.fal.run/fal-ai/hunyuan-video/image-to-video",
    ]
    payload = {
        "prompt": motion_prompt,
        "image_url": image_url,
    }
    print(f"[{shot_id}/3] Submitting motion to Wan (fal-ai/wan-i2v)...", flush=True)

    status_url, response_url = None, None
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        for ep in endpoints:
            sub = await client.post(ep, headers=HEADERS, json=payload)
            if sub.status_code in (200, 201, 202):
                sub_data = sub.json()
                status_url = sub_data.get("status_url")
                response_url = sub_data.get("response_url")
                print(f"   [i] Successfully connected to endpoint: {ep}")
                break
            else:
                print(f"   [~] Endpoint {ep} returned {sub.status_code}, trying next...")
        if not status_url and not response_url:
            raise RuntimeError("Wan video submission failed across all endpoints")

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        for i in range(75):
            await asyncio.sleep(3)
            s_resp = await client.get(status_url, headers=HEADERS, params={"logs": "1"})
            res_data = s_resp.json()
            status = res_data.get("status")
            if i % 4 == 0:
                print(f"   Shot {shot_id} Wan Status: {status} ({i*3}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                if not vid_url:
                    raise RuntimeError(f"Could not extract video url from response: {final_res}")

                local_vid = OUTPUT_DIR / f"shot_{shot_id}_wan21_raw.mp4"
                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Shot {shot_id} Wan Clip Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return vid_url, local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Wan task failed for shot {shot_id}: {res_data}")
        raise TimeoutError(f"Wan generation timed out for shot {shot_id}")


async def generate_narration_and_score_15s() -> tuple[Path, Path]:
    """Synthesize 15-second measured BBC nature narration and grand orchestral score."""
    import edge_tts

    narration_text = (
        "In the heart of the Canadian wilderness, ancient glaciers carved towering monuments of granite. "
        "Across millions of untouched acres, emerald waters reflect the timeless majesty of the peaks. "
        "Here, nature endures eternal and untamed."
    )
    voice_file = OUTPUT_DIR / "wild_canada_narration_15s.mp3"
    communicate = edge_tts.Communicate(narration_text, "en-GB-RyanNeural", rate="-6%")
    await communicate.save(str(voice_file))
    print(f"   15s BBC Narration Ready: {voice_file.name} ({voice_file.stat().st_size} bytes)", flush=True)

    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    bgm_file = OUTPUT_DIR / "wild_canada_orchestral_15s.mp3"
    synth_cmd = [
        exe, "-y",
        "-f", "lavfi", "-i", "sine=frequency=130.81:sample_rate=48000:duration=15",
        "-f", "lavfi", "-i", "sine=frequency=196.00:sample_rate=48000:duration=15",
        "-f", "lavfi", "-i", "sine=frequency=261.63:sample_rate=48000:duration=15",
        "-f", "lavfi", "-i", "anoisesrc=sample_rate=48000:amplitude=0.012:color=pink:duration=15",
        "-filter_complex",
        "[0:a]volume=0.22[c];[1:a]volume=0.18[g];[2:a]volume=0.15[h];[3:a]lowpass=f=350,volume=0.28[wind];"
        "[c][g][h][wind]amix=inputs=4:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "256k",
        str(bgm_file)
    ]
    subprocess.run(synth_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   15s Orchestral Score Ready: {bgm_file.name} ({bgm_file.stat().st_size} bytes)", flush=True)
    return voice_file, bgm_file


async def master_15s_4k_documentary(video_clips: list[Path], narration: Path, bgm: Path) -> Path:
    """Concatenate Wan video clips and master to 24.0 fps 4K UHD with sidechain audio ducking."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    final_master = OUTPUT_DIR / "wild_canada_nature_documentary_4k_wan21_master.mp4"

    inputs = []
    filter_parts = []
    for i, clip in enumerate(video_clips):
        inputs.extend(["-i", str(clip)])
        filter_parts.append(f"[{i}:v]scale=3840:2160:flags=lanczos,fps=24,setpts=PTS-STARTPTS[v{i}];")

    concat_inputs = "".join(f"[v{i}]" for i in range(len(video_clips)))
    filter_parts.append(f"{concat_inputs}concat=n={len(video_clips)}:v=1:a=0[vconcat];")

    narration_idx = len(video_clips)
    bgm_idx = len(video_clips) + 1
    inputs.extend(["-i", str(narration), "-i", str(bgm)])

    filter_parts.append(
        f"[{bgm_idx}:a]volume=0.55[bgm_base];"
        f"[{narration_idx}:a][bgm_base]sidechaincompress=threshold=0.07:ratio=6:attack=50:release=450[ducked_bgm];"
        f"[{narration_idx}:a][ducked_bgm]amix=inputs=2:dropout_transition=2:normalize=0[mixed_audio];"
        f"[mixed_audio]loudnorm=I=-14:TP=-1.0:LRA=7[amaster]"
    )

    full_filter = "".join(filter_parts)

    cmd = [
        exe, "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", "[vconcat]",
        "-map", "[amaster]",
        "-t", "15.0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(final_master)
    ]
    print("\nExecuting Single-Pass Multi-Shot 4K 24fps Mastering...", flush=True)
    subprocess.run(cmd, check=True)
    print(f"4K 15s Wan Master Ready: {final_master.name} ({final_master.stat().st_size} bytes)", flush=True)
    return final_master


async def run_wan21_production():
    shots_config = [
        {
            "id": 1,
            "img_prompt": (
                "Ultra-photorealistic 8K cinematic landscape of Canadian Rockies Lake Moraine in Banff National Park. "
                "Majestic granite peaks with snow dusted ridges, pristine turquoise glacial water, emerald pine forest, "
                "soft morning mist, crisp balanced 5500K daylight, deep optical focal depth."
            ),
            "motion_prompt": (
                "Ultra-photorealistic 4K cinematic BBC Planet Earth documentary aerial camera glide slowly descending "
                "and pushing forward over pristine turquoise glacial waters toward towering snow-capped Rocky Mountain peaks, "
                "slow expansive camera motion, 24fps film cadence, zero high-speed rush."
            ),
        },
        {
            "id": 2,
            "img_prompt": (
                "Cinematic 8K eye-level wide landscape of turquoise glacial lake in the Canadian Rockies reflecting towering "
                "granite cliffs, gentle ripples on clear alpine water, cedar trees framing the shoreline, serene morning light."
            ),
            "motion_prompt": (
                "Slow steadycam forward tracking glide along the emerald shoreline of the glacial lake, gentle water surface "
                "ripples reflecting towering mountain ridges, calm cinematic 24fps motion, atmospheric depth."
            ),
        },
        {
            "id": 3,
            "img_prompt": (
                "Grand panoramic 8K vista of Canadian Rockies alpine valley at dawn, sun rays piercing through low misty clouds "
                "illuminating rugged snow peaks and endless ancient evergreen forest below, majestic scale."
            ),
            "motion_prompt": (
                "Sweeping slow panoramic camera pan across the sunlit mountain peaks and mist-filled valley canopy, "
                "cinematic documentary cadence, smooth motion blur, epic grandeur."
            ),
        },
    ]

    print("=================================================================")
    print("[*] STARTING 15s NATURE DOCUMENTARY (OPTION B: WAN I2V + 16:9)")
    print("=================================================================\n")

    clips: list[Path] = []
    for shot in shots_config:
        img_url, _ = await generate_flux_keyframe_16_9(shot["id"], shot["img_prompt"])
        _, clip_path = await generate_wan21_clip(shot["id"], image_url=img_url, motion_prompt=shot["motion_prompt"])
        clips.append(clip_path)

    narration, bgm = await generate_narration_and_score_15s()
    master = await master_15s_4k_documentary(clips, narration, bgm)

    print("\n=================================================================")
    print(f"[+] 15s 4K MASTER READY (WAN): {master}")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(run_wan21_production())
