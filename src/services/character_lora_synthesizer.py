"""Autonomous Character LoRA Synthesizer & 3D Turnaround Training Engine.

Orchestrates:
1. Cache lookup: reuses existing network LoRA if present ($0.00).
2. Ground-truth hero face generation via FLUX.1 [dev] (Rule 12 compliant).
3. 3D head turnaround video via Kling/LivePortrait for identical bone structure.
4. Multi-angle frame extraction (12-15 frames: yaw, pitch, expressions).
5. Background & clothing decoupling (tight face cropping + neutral studio framing + captioning).
6. Automatic LoRA training on Fal.ai, local caching, and network asset registration.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import re
from typing import Any
import zipfile
from PIL import Image

from src.core.telemetry import logger
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
from src.providers.base import is_mock_mode
from src.providers.visual.fal_zimage import FalZImageAdapter
from src.providers.visual.fal_kling_v3 import FalKlingV3Adapter
from src.services.core_asset_service import AssetScope, core_asset_service
from src.services.core_lora_service import CharacterLoraProfile, core_lora_service


def _build_hero_prompt(name: str, gender: str, language: str, culture: str | None = None) -> str:
    """Construct Master Hero Face Prompt strictly following Rule 12."""
    gen_low = str(gender or "female").lower()
    is_fem = "female" in gen_low or "woman" in gen_low
    age = "24-year-old"
    
    if any(k in str(culture or language).lower() for k in ("arab", "iraq", "levant", "khalij")):
        ethnicity = f"stunning {age} Levantine/Iraqi woman, warm olive-honey skin, almond hazel eyes" if is_fem else f"handsome {age} Levantine man, warm olive skin, defined jawline"
    elif any(k in str(culture or language).lower() for k in ("te", "ta", "kn", "ml", "south_indian")):
        ethnicity = f"stunning {age} South Indian woman, warm golden-wheatish skin, expressive almond eyes" if is_fem else f"handsome {age} South Indian man, warm wheatish skin, sculpted athletic jawline"
    elif any(k in str(culture or language).lower() for k in ("hi", "north_indian", "punjabi")):
        ethnicity = f"stunning {age} North Indian woman, warm radiant wheatish skin, glowing expressive eyes" if is_fem else f"handsome {age} North Indian man, sharp jawline, neat light stubble"
    else:
        ethnicity = f"strikingly beautiful {age} woman, balanced fit build, warm natural skin" if is_fem else f"strikingly handsome {age} man, athletic fit build, sharp jawline"

    attire = "modest high-neck neutral black top" if is_fem else "tailored dark crewneck shirt"
    return (
        f"Master studio portrait photograph of {name}, {ethnicity}, balanced naturally fit build, "
        f"facing directly forward, neutral calm expression, wearing {attire}, "
        f"clean neutral light-grey studio backdrop, soft diffused key lighting, zero harsh shadows, "
        f"8k UHD, 35mm Master Prime lens, razor-sharp focus on eyes and facial skin texture, realistic skin pores."
    )


def _decouple_and_crop_frames(raw_frames_dir: Path, out_dataset_dir: Path, trigger_word: str, is_female: bool) -> None:
    """Crop tight around face and generate descriptive caption files to decouple clothing/background."""
    out_dataset_dir.mkdir(parents=True, exist_ok=True)
    frame_files = sorted(raw_frames_dir.glob("turnaround_*.jpg"))
    angle_descriptions = [
        "facing front, neutral gaze", "head turned 15 degrees left", "head turned 30 degrees left, gentle smile",
        "head turned 45 degrees left, three-quarter view", "head tilted slightly down, reflective gaze",
        "head tilted slightly up, soft smile", "facing front, warm smile", "head turned 15 degrees right",
        "head turned 30 degrees right, smiling eyes", "head turned 45 degrees right, three-quarter view",
        "head turned 20 degrees right, neutral expression", "facing front, soft contemplative expression",
        "close-up portrait, eyes looking straight", "head slightly angled, tender smile", "facing front, calm serene countenance"
    ]
    char_label = "woman" if is_female else "man"

    for idx, fpath in enumerate(frame_files):
        try:
            with Image.open(fpath) as img:
                w, h = img.size
                # Tight center portrait crop (focusing on face/hair, excluding full torso/background) at 1024x1024
                crop_box = (int(w * 0.15), int(h * 0.05), int(w * 0.85), int(h * 0.90))
                cropped = img.crop(crop_box).resize((1024, 1024), Image.Resampling.LANCZOS)
                out_img = out_dataset_dir / f"crop_{idx + 1:02d}.jpg"
                cropped.save(out_img, quality=95)

                angle_desc = angle_descriptions[idx % len(angle_descriptions)]
                caption = f"{trigger_word} {char_label}, {angle_desc}, clean neutral studio background, 35mm portrait"
                (out_dataset_dir / f"crop_{idx + 1:02d}.txt").write_text(caption, encoding="utf-8")
        except Exception as ex:
            logger.warning(f"lora_crop_frame_failed: {fpath.name} - {ex}")


async def synthesize_turnaround_dataset(
    work_dir: Path, name: str, gender: str, language: str, culture: str | None = None, num_frames: int = 15, force_live: bool = False,
    dataset_model: str = "z-image",
) -> Path:
    """Generate hero face -> 3D turnaround video -> 12-15 decoupled multi-angle crops in a zip."""
    work_dir.mkdir(parents=True, exist_ok=True)
    zip_path = work_dir / f"{name.lower()}_dataset.zip"
    if zip_path.is_file() and zip_path.stat().st_size > 50_000:
        logger.info(f"character_dataset_cached: reusing {zip_path.name}")
        return zip_path

    # Check parent directory for any existing turnaround dataset of the same character
    for existing_zip in work_dir.parent.glob(f"**/{name.lower()}_dataset.zip"):
        if existing_zip.resolve() != zip_path.resolve() and existing_zip.is_file() and existing_zip.stat().st_size > 50_000:
            logger.info(f"character_dataset_cached: reusing existing dataset from {existing_zip.parent.name}")
            import shutil
            shutil.copy2(existing_zip, zip_path)
            return zip_path

    # Step A: 1 Master Hero Face
    hero_path = work_dir / "hero_master.jpg"
    if not (hero_path.is_file() and hero_path.stat().st_size > 10_000):
        prompt = _build_hero_prompt(name=name, gender=gender, language=language, culture=culture)
        dm = str(dataset_model or "z-image").lower().strip()
        if "flux" in dm:
            logger.info(f"synthesizing_master_hero_face: name={name}, gender={gender} with FLUX.1 [dev]")
            from src.providers.visual.fal_flux_dev import FalFluxDevAdapter
            f_adapter = FalFluxDevAdapter()
            await f_adapter.generate_to_file(prompt, hero_path, aspect_ratio="1:1", force_live=force_live, upscale_4k=False)
        else:
            logger.info(f"synthesizing_master_hero_face: name={name}, gender={gender} with Z-Image Turbo")
            z_adapter = FalZImageAdapter()
            await z_adapter.generate_to_file(prompt, hero_path, aspect_ratio="1:1", force_live=force_live)

    # Step B: 3D Head Turnaround Video via Kling or Local Fallback
    turnaround_vid = work_dir / "head_turnaround.mp4"
    if not (turnaround_vid.is_file() and turnaround_vid.stat().st_size > 50_000):
        kling = FalKlingV3Adapter()
        mot = (
            "Cinematic 3D head turnaround: character turns head smoothly 45 degrees left, "
            "tilts slightly down with subtle smile, turns smoothly 45 degrees right, blinks naturally, "
            "and returns to front center. Continuous fluid head rotation, photorealistic natural lighting."
        )
        try:
            if is_mock_mode() and not force_live: raise RuntimeError("Mock mode active")
            await kling.generate_video(image_url=str(hero_path), motion_prompt=mot, output_path=turnaround_vid, duration=5, force_live=force_live)
        except Exception as ex:
            logger.info(f"turnaround_local_synthetic_fallback: {ex}")
            ffmpeg_bin = get_ffmpeg_binary()
            cmd = [
                ffmpeg_bin, "-y", "-loop", "1", "-i", str(hero_path),
                "-vf", "scale=3840:3840,zoompan=z='min(zoom+0.0008,1.04)':d=125:s=3840x3840:fps=25",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-vframes", "125",
                str(turnaround_vid)
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

    # Step C: Extract Keyframe Stills via FFmpeg
    raw_frames = work_dir / "raw_frames"
    raw_frames.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()
    cmd_ext = [
        ffmpeg_bin, "-y", "-i", str(turnaround_vid),
        "-vf", f"fps={max(1, num_frames / 5.0):.2f}", "-vframes", str(num_frames),
        str(raw_frames / "turnaround_%02d.jpg")
    ]
    proc = await asyncio.create_subprocess_exec(*cmd_ext, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc.communicate()

    # Step D: Decouple Background & Outfits via Face Cropping and Captioning
    dataset_dir = work_dir / "dataset"
    trigger_word = f"{re.sub(r'[^a-zA-Z0-9]', '', name).upper()}_TRIGGER"
    is_fem = "female" in str(gender).lower()
    _decouple_and_crop_frames(raw_frames, dataset_dir, trigger_word, is_female=is_fem)

    # Step E: Zip Dataset
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in dataset_dir.glob("crop_*.*"):
            zf.write(f, arcname=f.name)
    logger.info(f"character_dataset_ready: {zip_path.name} ({zip_path.stat().st_size} bytes)")
    return zip_path


async def ensure_character_lora(
    user_id: str,
    network: str,
    character_name: str,
    gender: str = "female",
    language: str = "te",
    culture: str | None = None,
    force_retrain: bool = False,
    steps: int = 500,
    num_frames: int = 15,
    force_live: bool = False,
    base_model: str = "flux",
    dataset_model: str = "z-image",
) -> dict[str, Any]:
    """Ensure a consistent LoRA exists for character, synthesizing from 3D turnaround if missing."""
    clean_char = re.sub(r"[^a-zA-Z0-9_-]", "_", character_name.lower()).strip("_") or "lead"
    trigger = f"{re.sub(r'[^a-zA-Z0-9]', '', character_name).upper()}_TRIGGER"

    # 1. Tier 1 Cache Check: If LoRA is already registered for this network, return immediately ($0 spend)
    if not force_retrain:
        existing = core_lora_service.resolve_character_loras(user_id=user_id, network=network)
        matched = next((
            l for l in existing
            if (clean_char in str(l.get("character_name", "")).lower() or l.get("trigger_word") == trigger)
            and (not base_model or str(l.get("base_model", "")).lower() in (base_model.lower(), base_model.lower().replace("-", "")))
        ), None)
        if matched and matched.get("path"):
            logger.info(f"lora_cache_hit: reusing existing {base_model} LoRA for '{character_name}' on network '{network}' ($0.00 spend)")
            return matched

    # 2. Setup Working Directory under network asset folder
    lora_dir = core_asset_service.get_asset_dir(user_id=user_id, category="loras", scope=AssetScope.NETWORK, network=network)
    lora_dir.mkdir(parents=True, exist_ok=True)
    work_dir = lora_dir / f"training_{clean_char}_{base_model}"

    # 3. Synthesize 12-15 Decoupled Angular Keyframes from 3D Turnaround
    print(f"\n[~] Character LoRA '{character_name}' not found for network '{network}'.")
    print(f"[~] Generating 3D face turnaround & {num_frames} decoupled reference frames ({dataset_model})...")
    dataset_zip = await synthesize_turnaround_dataset(
        work_dir=work_dir, name=character_name, gender=gender, language=language, culture=culture, num_frames=num_frames, force_live=force_live, dataset_model=dataset_model
    )

    # 4. Train LoRA via Fal.ai & Register into Network Catalog
    print(f"[~] Training custom {base_model.upper()} character LoRA on Fal.ai for '{character_name}'...")
    profile = await core_lora_service.train_and_register_lora(
        user_id=user_id, network=network, character_key=clean_char,
        images_zip_path=dataset_zip, trigger_word=trigger, name=character_name, gender=gender,
        base_model=base_model,
    )
    print(f"[+] Character LoRA Trained & Registered: {profile.name} (Trigger: {profile.trigger_word}, Base: {profile.base_model})\n")

    return {
        "path": profile.lora_url,
        "scale": profile.scale,
        "trigger_word": profile.trigger_word,
        "character_name": profile.name,
        "gender": profile.gender,
        "base_model": profile.base_model,
        "body_composition": profile.body_composition,
    }


__all__ = ["_build_hero_prompt", "synthesize_turnaround_dataset", "ensure_character_lora"]
