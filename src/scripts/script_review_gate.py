"""Interactive Script & Storyboard Review Gate for Video Studio Pipelines.

Displays a comprehensive, formatted review of the Gemini-generated screenplay:
1. Title, Mood, Hook Thesis
2. Character Profiles & Modest Context-Matched Wardrobe (Rule 12)
3. Structured Lyrics (Verses, Chorus, Hooks)
4. Multi-Camera Rig Scenes (1..N) with Camera IDs and local drone motion
5. Broadcast Switching Timeline Summary (Singing cuts vs Orchestra cuts)
6. Interactive Confirmation prompt allowing user to inspect/edit storyboard.json
Preserves Rule 4 (< 300 lines limit).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def display_script_review(storyboard_data: dict[str, Any], storyboard_path: Path) -> None:
    """Print an aesthetic, readable summary of the generated script and camera rig."""
    title_en = storyboard_data.get("title_en") or storyboard_data.get("title") or "Untitled Musical Performance"
    title_loc = storyboard_data.get("title_localized") or ""
    hook = storyboard_data.get("hook_thesis") or ""
    mood = storyboard_data.get("mood") or ""
    tempo = storyboard_data.get("tempo_bpm") or ""

    print("\n" + "=" * 74)
    print(" CINEAI STUDIO - SCRIPT & STORYBOARD REVIEW GATE")
    print("=" * 74)
    print(f" - Title (EN):       {title_en}")
    if title_loc:
        print(f" - Title (Native):   {title_loc}")
    country = storyboard_data.get("country") or ""
    language = storyboard_data.get("language") or ""
    if country or language:
        print(f" - Country / Lang:   {country} ({language.upper() if language else ''})")
    if hook:
        print(f" - Hook / Concept:   {hook}")
    if mood:
        print(f" - Musical Mood:     {mood} ({tempo} BPM)" if tempo else f" - Musical Mood:     {mood}")

    # Characters & Derived Wardrobe
    chars = storyboard_data.get("characters") or []
    if chars:
        print("\n [LEAD CAST & DERIVED WARDROBE (Rule 12 Compliant)]")
        for i, c in enumerate(chars, 1):
            name = c.get("name", f"Performer {i}")
            gender = c.get("gender", "female")
            age = c.get("age", 24)
            outfit = c.get("outfit_description", "Context-matched modest concert attire")
            print(f"   * Character {i}: {name} ({age}yo, {gender})")
            print(f"     Outfit: {outfit[:120]}..." if len(outfit) > 120 else f"     Outfit: {outfit}")

    # Lyrics
    lyrics = storyboard_data.get("lyrics") or ""
    if lyrics:
        print("\n [LYRICS PREVIEW]")
        lines = [line.strip() for line in lyrics.splitlines() if line.strip()]
        preview_lines = lines[:10]
        for l in preview_lines:
            print(f"   {l}")
        if len(lines) > 10:
            print(f"   ... ({len(lines) - 10} more lines in storyboard.json)")

    # Multi-Camera Rig Scenes
    scenes = storyboard_data.get("scenes") or []
    if scenes:
        print(f"\n [CAMERA RIG PERSPECTIVES ({len(scenes)} Physical Cameras)]")
        for sc in scenes:
            idx = sc.get("scene_index", 1)
            cam_id = sc.get("camera_id") or "camera"
            shot = sc.get("camera_shot_type", "shot")
            motion = sc.get("camera_motion") or (sc.get("local_drone") or {}).get("movement") or "steady"
            pose = sc.get("character_pose", "")[:90]
            print(f"   * Cam {idx} [{cam_id} | {shot} | {motion}]: {pose}...")

    # Broadcast Switching Timeline
    timeline = storyboard_data.get("broadcast_timeline") or []
    if timeline:
        singing_cuts = [c for c in timeline if c.get("is_singing")]
        orch_cuts = [c for c in timeline if not c.get("is_singing")]
        min_dur = min((c.get("duration_seconds", 4.0) for c in timeline), default=4.0)
        max_dur = max((c.get("duration_seconds", 4.0) for c in timeline), default=4.0)
        print(f"\n [BROADCAST SWITCHING TIMELINE]")
        print(f"   * Total Broadcast Cuts:   {len(timeline)} cuts (duration: {min_dur:.1f}s - {max_dur:.1f}s each)")
        print(f"   * Singing Vocal Cuts:     {len(singing_cuts)} cuts (with LatentSync lipsync)")
        print(f"   * Orchestra / Solos:      {len(orch_cuts)} cuts (wide shots, crane, instrument solos, zero lipsync)")

    print(f"\n [STORYBOARD ARTIFACT]")
    print(f"   * Location: {storyboard_path.resolve()}")
    print("=" * 74)


def prompt_script_review_gate(
    storyboard_data: dict[str, Any],
    storyboard_path: Path,
    auto_confirm: bool = False,
) -> tuple[bool, dict[str, Any]]:
    """Present the script review gate.

    Returns:
        (proceed: bool, active_storyboard: dict[str, Any])
    """
    display_script_review(storyboard_data, storyboard_path)

    if auto_confirm:
        print("[i] Auto-confirm flag (-y / --yes) active. Proceeding with video production.")
        return True, storyboard_data

    try:
        ans = input("\n[?] Review the script and storyboard above. Proceed with video production? [Y/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n[!] Input interrupted. Aborting production.")
        return False, storyboard_data

    if ans and ans not in ("y", "yes"):
        ep_id = storyboard_data.get("id") or storyboard_data.get("episode_id")
        print("\n" + "-" * 74)
        print("[i] Production paused by user at Script Review Gate.")
        print(f"    You can view or edit the screenplay directly at:")
        print(f"    {storyboard_path.resolve()}")
        if ep_id:
            print(f"\n    To resume this exact production after making changes, run with:")
            print(f"    --id {ep_id}")
        print("-" * 74 + "\n")
        return False, storyboard_data

    # If user made edits to storyboard.json while reviewing, reload them cleanly
    if storyboard_path.is_file():
        try:
            reloaded = json.loads(storyboard_path.read_text(encoding="utf-8"))
            return True, reloaded
        except Exception:
            pass

    return True, storyboard_data


__all__ = ["display_script_review", "prompt_script_review_gate"]
