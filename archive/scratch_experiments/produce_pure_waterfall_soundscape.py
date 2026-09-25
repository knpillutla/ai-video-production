"""Produce a pure, crystal-clear waterfall soundscape (Suno AI or Organic Multi-Band DSP)

Eliminates synthetic noise/hiss and remuxes with the Kling 4K video master:
storage/live_production/waterfall_patio_retreat/comparison/patio_waterfall_kling_4k_master.mp4
"""

import asyncio
import os
import subprocess
import httpx
import imageio_ffmpeg
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUNO_API_KEY = os.getenv("SUNO_API_KEY") or os.getenv("MUSICAPI_KEY")
OUT_DIR = Path("storage/live_production/waterfall_patio_retreat/pure_audio")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_MASTER = Path("storage/live_production/waterfall_patio_retreat/comparison/patio_waterfall_kling_4k_master.mp4")


def generate_organic_dsp_waterfall(output_path: Path, duration_sec: float = 5.5) -> Path:
    """Synthesize organic multi-band waterfall trickle + deep pool resonance without harsh pink noise."""
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    
    # Use multi-stage tuned acoustic bandpass filters with dynamic tremolo and soft lowpass
    # to mimic real water tumbling into a pool (removing harsh high-frequency static hiss)
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "lavfi", "-i", f"anoisesrc=d={duration_sec}:c=brown:r=48000:a=0.35",
        "-f", "lavfi", "-i", f"anoisesrc=d={duration_sec}:c=pink:r=48000:a=0.08",
        "-filter_complex",
        "[0:a]lowpass=f=450,volume=1.8[deep_rumble];"
        "[1:a]highpass=f=250,lowpass=f=950,tremolo=f=4.5:d=0.35,volume=1.2[organic_trickle];"
        "[deep_rumble][organic_trickle]amix=inputs=2:weights=1.0 0.8,alimiter=limit=0.9,loudnorm=I=-16.0:TP=-1.5:LRA=7.0[aout]",
        "-map", "[aout]",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"[+] Organic DSP Audio Ready: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path


async def generate_suno_ambient_waterfall(output_path: Path, duration_sec: float = 30.0) -> Path:
    """Generate commercial master nature track using Suno v3.5 Pro API."""
    if output_path.exists() and output_path.stat().st_size > 50000:
        print(f"[i] Using existing Suno stem: {output_path}")
        return output_path

    if not SUNO_API_KEY:
        print("[!] SUNO_API_KEY not set in .env, falling back to Organic DSP.")
        return generate_organic_dsp_waterfall(output_path, duration_sec=duration_sec)

    prompt = (
        "[ambient nature], crystal-clear mountain waterfall, soothing gentle water splash and babbling brook, "
        "soft acoustic meditative harp and bamboo flute, zero hiss, pure organic water flow, 48kHz broadcast master"
    )
    print(f"[*] Submitting Suno Ambient Request: {prompt[:60]}...")
    headers = {"Authorization": f"Bearer {SUNO_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "tags": "ambient, nature, waterfall, meditation, acoustic, crystal clear",
        "title": "Waterfall Patio Pure Ambience",
        "make_instrumental": True,
        "wait_audio": True
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post("https://api.musicapi.ai/api/v1/sonic/create", headers=headers, json=payload)
        if resp.status_code == 200:
            audio_url = resp.json().get("audio_url")
            if audio_url:
                aud_data = await client.get(audio_url)
                output_path.write_bytes(aud_data.content)
                print(f"[+] Suno Audio Downloaded: {output_path}")
                return output_path

    print("[!] Suno API returned non-200, falling back to Organic DSP.")
    return generate_organic_dsp_waterfall(output_path, duration_sec=duration_sec)


def remux_4k_master(video_path: Path, audio_path: Path, output_master: Path):
    """Mux the 4K Kling video with the new clean audio stem."""
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin, "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(output_master)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"[SUCCESS] Pristine Master Ready: {output_master} ({output_master.stat().st_size / (1024*1024):.2f} MB)")


async def main():
    print("=" * 80)
    print("PURIFYING WATERFALL PATIO SOUNDSCAPE (ZERO HISS / ORGANIC ACOUSTICS)")
    print("=" * 80)

    # 1. Generate Organic Multi-Band DSP Audio Stem (Warm bubbling trickle + pool resonance)
    dsp_audio = OUT_DIR / "waterfall_organic_dsp_clean.aac"
    generate_organic_dsp_waterfall(dsp_audio, duration_sec=5.0)

    # 2. Remux with Kling 4K Master
    clean_kling_master = OUT_DIR / "patio_waterfall_kling_4k_pure_sound.mp4"
    if VIDEO_MASTER.exists():
        remux_4k_master(VIDEO_MASTER, dsp_audio, clean_kling_master)
    else:
        print(f"[!] Video master not found at {VIDEO_MASTER}")

    print("=" * 80)
    print(f"Master Video with Pure Waterfall Audio: {clean_kling_master}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
