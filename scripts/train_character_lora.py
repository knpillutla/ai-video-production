#!/usr/bin/env python3
"""Reusable CLI Script to Train and Register a 3D-Turnaround Character LoRA.

Usage:
    python scripts/train_character_lora.py --name "Kavitha" --network "telugu_rhythms" --gender "female" --language "te" --live
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys

_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from src.core.telemetry import logger
from src.services.character_lora_synthesizer import ensure_character_lora


def main():
    p = argparse.ArgumentParser(description="Train and register a custom FLUX character LoRA from 3D turnaround frames.")
    p.add_argument("--name", required=True, type=str, help="Character name (e.g. 'Kavitha')")
    p.add_argument("--network", required=True, type=str, help="Network or channel slug (e.g. 'telugu_rhythms')")
    p.add_argument("--gender", type=str, default="female", choices=["female", "male", "non_binary"], help="Character gender")
    p.add_argument("--language", type=str, default="te", help="Language code (e.g. 'te', 'hi', 'en')")
    p.add_argument("--culture", type=str, default=None, help="Cultural heritage key (e.g. 'south_indian', 'north_indian')")
    p.add_argument("--steps", type=int, default=500, help="Number of LoRA training steps (default: 500)")
    p.add_argument("--frames", type=int, default=15, help="Number of 3D turnaround angle frames to extract (default: 15)")
    p.add_argument("--force-retrain", action="store_true", default=False, help="Force retrain even if LoRA already exists")
    p.add_argument("--user-id", type=str, default="knpillutla@gmail.com", help="User container scope")
    p.add_argument("--live", dest="force_live", action="store_true", default=False, help="Force live generation via Fal.ai")

    args = p.parse_args()

    print(f"\n[~] Character LoRA Pipeline Started for '{args.name}' on Network '{args.network}'...")
    res = asyncio.run(
        ensure_character_lora(
            user_id=args.user_id,
            network=args.network,
            character_name=args.name,
            gender=args.gender,
            language=args.language,
            culture=args.culture,
            force_retrain=args.force_retrain,
            steps=args.steps,
            num_frames=args.frames,
            force_live=args.force_live,
        )
    )
    print(f"[SUCCESS] Character LoRA Ready:")
    print(f"  - Name: {res.get('character_name')}")
    print(f"  - Trigger Word: {res.get('trigger_word')}")
    print(f"  - LoRA Path/URL: {res.get('path')}")
    print(f"  - Scale: {res.get('scale', 1.0)}\n")


if __name__ == "__main__":
    main()
