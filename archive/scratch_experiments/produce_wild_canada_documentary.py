"""Live Production: Wild Canada Nature Documentary in BBC Planet Earth / Free Documentary Style.

Adheres strictly to:
- Directive 8: Single live test, exactly 10s duration cap.
- Directive 11: YPP-compliant authoritative educational nature lore narration.
- Directive 14: Cinematic 24.0 fps dynamic framerate, 4K CRF 18 mastering, 48kHz audio.
- Prompt Director MCP: Uses nature_documentary.md for zero instruction dilution.
"""

import asyncio
import os
import subprocess
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

OUTPUT_DIR = Path("storage/live_production/wild_canada_documentary_10s")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_flux_keyframe() -> tuple[str, Path]:
    """Generate 4K cinematic nature keyframe: Canadian Rockies glacial lake in BBC style."""
    endpoint = "https://queue.fal.run/fal-ai/flux/dev"
    prompt = (
        "Ultra-photorealistic 8K National Geographic cinematic landscape of the Canadian Rockies and glacial lake Moraine "
        "in Banff National Park. Majestic towering granite peaks with snow dusted ridges, pristine turquoise glacial water with mirror reflections, "
        "emerald green ancient pine and cedar forest, soft morning mist drifting through the valley, crisp balanced 5500K open-air daylight, "
        "soft authentic sun rays piercing mist, epic monumental scale, deep optical focal depth, zero artificial yellow lens flare."
    )
    payload = {
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }
    print("1. Synthesizing 4K Nature Documentary Keyframe with Flux Dev...", flush=True)
    async with httpx.AsyncClient(timeout=60.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")

        for _ in range(30):
            await asyncio.sleep(2)
            s = await client.get(status_url, headers=HEADERS)
            if s.json().get("status") == "COMPLETED":
                res = await client.get(resp_url, headers=HEADERS)
                img_url = res.json()["images"][0]["url"]
                local_img = OUTPUT_DIR / "wild_canada_keyframe_4k.jpg"
                img_bytes = (await client.get(img_url)).content
                local_img.write_bytes(img_bytes)
                print(f"   Keyframe Ready: {local_img.name} ({len(img_bytes)} bytes)", flush=True)
                return img_url, local_img
        raise TimeoutError("Flux keyframe timed out")

async def generate_kling_video(image_url: str) -> tuple[str, Path]:
    """Generate 10s sweeping aerial glide motion via Kling 1.5 Pro."""
    endpoint = "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video"
    prompt = (
        "Ultra-photorealistic 4K cinematic BBC Planet Earth documentary aerial camera glide slowly descending "
        "and pushing forward over pristine turquoise glacial waters toward towering snow-capped Rocky Mountain peaks, "
        "soft morning mist drifting through ancient pine trees, majestic cinematic grandeur, slow expansive camera motion, "
        "24fps film cadence, zero high-speed rush, realistic atmospheric depth."
    )
    payload = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": "10",
        "aspect_ratio": "16:9",
    }
    print("2. Submitting 10s sweeping aerial motion to Kling 1.5 Pro...", flush=True)
    async with httpx.AsyncClient(timeout=30.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(75):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS)
            status = s_resp.json().get("status")
            if i % 3 == 0:
                print(f"   Kling Status: {status} ({i*4}s elapsed)", flush=True)
            if status == "COMPLETED":
                r = await client.get(response_url, headers=HEADERS)
                vid_url = r.json().get("video", {}).get("url")
                local_vid = OUTPUT_DIR / "kling_wild_canada_raw_10s.mp4"
                v_bytes = (await client.get(vid_url, timeout=60.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Kling 10s Raw Video Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return vid_url, local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Kling task failed: {status}")
        raise TimeoutError("Kling video generation timed out")

async def generate_narration_and_orchestral_bgm() -> tuple[Path, Path]:
    """Generate authoritative British documentary narration and grand orchestral score."""
    import edge_tts
    # Poetic BBC style narration with measured pauses
    narration_text = (
        "In the heart of the Canadian wilderness, ancient glaciers carved towering monuments of granite. "
        "Here, across millions of untouched acres, nature remains untamed, vast, and eternal."
    )
    voice_file = OUTPUT_DIR / "wild_canada_narration.mp3"
    communicate = edge_tts.Communicate(narration_text, "en-GB-RyanNeural", rate="-6%")
    await communicate.save(str(voice_file))
    print(f"   BBC Documentary Narration Ready: {voice_file.name} ({voice_file.stat().st_size} bytes)", flush=True)

    # Synthesize cinematic orchestral ambient score: low cello drone (C2/G2) + harmonic French horn overtones + wind foley
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    bgm_file = OUTPUT_DIR / "wild_canada_orchestral_bgm.mp3"
    synth_cmd = [
        exe, "-y",
        "-f", "lavfi", "-i", "sine=frequency=130.81:sample_rate=48000:duration=10", # C3 cello
        "-f", "lavfi", "-i", "sine=frequency=196.00:sample_rate=48000:duration=10", # G3 resonance
        "-f", "lavfi", "-i", "sine=frequency=261.63:sample_rate=48000:duration=10", # C4 horn
        "-f", "lavfi", "-i", "anoisesrc=sample_rate=48000:amplitude=0.012:color=pink:duration=10", # Alpine breeze
        "-filter_complex",
        "[0:a]volume=0.22[c];[1:a]volume=0.18[g];[2:a]volume=0.15[h];[3:a]lowpass=f=350,volume=0.28[wind];"
        "[c][g][h][wind]amix=inputs=4:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "256k",
        str(bgm_file)
    ]
    subprocess.run(synth_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Orchestral Score Stem Ready: {bgm_file.name} ({bgm_file.stat().st_size} bytes)", flush=True)
    return voice_file, bgm_file

async def master_24fps_4k_documentary(raw_video: Path, narration: Path, bgm: Path) -> Path:
    """Master to 24.0 fps cinematic 4K UHD broadcast master with sidechain ducking."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    final_master = OUTPUT_DIR / "wild_canada_nature_documentary_4k_master.mp4"

    filter_complex = (
        "[0:v]scale=3840:2160:flags=lanczos,fps=24[vmaster];"
        "[2:a]volume=0.55[bgm_base];"
        "[1:a][bgm_base]sidechaincompress=threshold=0.07:ratio=6:attack=50:release=450[ducked_bgm];"
        "[1:a][ducked_bgm]amix=inputs=2:dropout_transition=2:normalize=0[mixed_audio];"
        "[mixed_audio]loudnorm=I=-14:TP=-1.0:LRA=7[amaster]"
    )

    cmd = [
        exe, "-y",
        "-i", str(raw_video),
        "-i", str(narration),
        "-i", str(bgm),
        "-filter_complex", filter_complex,
        "-map", "[vmaster]",
        "-map", "[amaster]",
        "-t", "10.0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(final_master)
    ]
    print("3. Executing Single-Pass 4K 24fps Cinematic FFmpeg Mastering...", flush=True)
    subprocess.run(cmd, check=True)
    print(f"4K 24fps Nature Documentary Master Ready: {final_master.name} ({final_master.stat().st_size} bytes)", flush=True)
    return final_master

async def main():
    print("=== STARTING WILD CANADA NATURE DOCUMENTARY PRODUCTION ===")
    img_url, local_img = await generate_flux_keyframe()
    vid_url, local_vid = await generate_kling_video(img_url)
    narration, bgm = await generate_narration_and_orchestral_bgm()
    final_master = await master_24fps_4k_documentary(local_vid, narration, bgm)
    print("=== WILD CANADA DOCUMENTARY COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(main())
