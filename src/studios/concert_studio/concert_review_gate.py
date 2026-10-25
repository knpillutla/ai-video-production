"""Interactive Multi-Stage Production Review Gates for Concert Studio.

Enforces step-by-step user review when running without -y / --yes:
- Stage 1: Script, Screenplay, Style, and Venue Review
- Stage 2: Audio Master & Directorial Multi-Camera Timeline Review
- Stage 3: Master 4K Keyframes & 3D Arena Flight Plates Review
- Stage 5: Broadcast Sliced Cuts & Lip-Sync Review before final master assembly
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence


def _ask_user(prompt_text: str, auto_confirm: bool = False) -> bool:
    if auto_confirm:
        return True
    try:
        resp = input(f"\n[?] {prompt_text} [Y/n]: ").strip().lower()
        if resp in ("n", "no", "q", "quit"):
            print("\n[!] Production paused by user for review. Workspace preserved.")
            print("[*] To resume this production later, run with --id <episode_id>.")
            return False
        return True
    except (KeyboardInterrupt, EOFError):
        print("\n[!] Production interrupted. Workspace preserved.")
        return False


def prompt_script_review(
    title_en: str,
    title_loc: str,
    artist: str,
    language: str,
    instrument: str,
    venue_display: str,
    lyrics_preview: str,
    llm_provider: str = "",
    llm_model: str = "",
    auto_confirm: bool = False,
) -> bool:
    """Stage 1: Review generated song script, lyrics, and setting."""
    print(f"\n{'='*70}\n📋 STAGE 1 REVIEW: SCRIPT & VENUE SPECIFICATION\n{'='*70}")
    print(f"🎵 Title:      {title_en} ({title_loc})")
    print(f"🎤 Artist:     {artist} | Language: {language.upper()} | Lead: {instrument}")
    if llm_provider:
        m_txt = f" ({llm_model})" if llm_model else ""
        print(f"🤖 Script LLM: {llm_provider.upper()}{m_txt}")
    print(f"🏛️ Setting:    {venue_display}")
    print(f"🎼 Lyrics Preview (First 250 chars):\n{lyrics_preview.strip()[:250]}...\n{'='*70}")
    return _ask_user("Proceed to Stage 2 (Audio Synthesis & Stems)?", auto_confirm)


def prompt_audio_timeline_review(
    audio_path: Path,
    actual_dur: float,
    cuts_tl: Sequence[dict[str, Any]],
    auto_confirm: bool = False,
) -> bool:
    """Stage 2: Review synthesized audio master and directorial cuts timeline."""
    print(f"\n{'='*70}\n🎧 STAGE 2 REVIEW: AUDIO MASTER & DIRECTORIAL TIMELINE\n{'='*70}")
    print(f"🎶 Audio Master: {audio_path.name} ({actual_dur:.1f}s)")
    print(f"🎬 Broadcast Timeline: {len(cuts_tl)} synchronized camera cuts planned:")
    for c in cuts_tl[:6]:
        idx = c.get("cut_index", 0)
        cam = c.get("camera_id", "cam")
        st, et = float(c.get("start_time", 0.0)), float(c.get("end_time", 0.0))
        mot = c.get("local_drone_motion", "steady")
        sing = " [SINGING]" if c.get("is_singing") else ""
        print(f"   • Cut {idx:02d}: {st:4.1f}s - {et:4.1f}s ({et-st:3.1f}s) | {cam:<24} | {mot}{sing}")
    if len(cuts_tl) > 6:
        print(f"   ... and {len(cuts_tl) - 6} more cuts.")
    print(f"{'='*70}")
    return _ask_user("Proceed to Stage 3 (4K Camera Plates & 3D Flight)?", auto_confirm)


def prompt_visual_plates_review(
    scenes_dir: Path,
    img_paths: Sequence[Path],
    auto_confirm: bool = False,
) -> bool:
    """Stage 3: Review generated 4K stage camera plates and 3D flight plates."""
    print(f"\n{'='*70}\n📸 STAGE 3 REVIEW: 4K VISUAL CAMERA PLATES\n{'='*70}")
    print(f"📁 Scenes Directory: {scenes_dir}")
    print(f"🖼️ Master Stage Plates ({len(img_paths)} angles created):")
    for p in img_paths:
        sz_kb = (p.stat().st_size / 1024) if p.is_file() else 0
        print(f"   • {p.name:<20} ({sz_kb:5.1f} KB)")
    flight = scenes_dir / "stadium_3d_flight.mp4"
    if flight.is_file():
        print(f"   • {flight.name:<20} (3D 360-degree Arena Orbit Plate)")
    print(f"{'='*70}")
    return _ask_user("Proceed to Stage 4 & 5 (Master Singer Lipsync & Slicing)?", auto_confirm)


def prompt_broadcast_cuts_review(
    cuts: Sequence[dict[str, Any]],
    lipsync_model: str,
    auto_confirm: bool = False,
) -> bool:
    """Stage 5: Review sliced cuts and lip-sync clips before final assembly."""
    print(f"\n{'='*70}\n✂️ STAGE 5 REVIEW: BROADCAST CUTS & LIP-SYNC\n{'='*70}")
    print(f"🎬 Ready Cuts:   {len(cuts)} broadcast cuts resolved")
    print(f"👄 Lip-Sync:     Model: {lipsync_model} (Stream B Vocal Sync)")
    sing_cuts = sum(1 for c in cuts if c.get("is_singing"))
    print(f"🎤 Vocal Cuts:   {sing_cuts} singing cuts | {len(cuts) - sing_cuts} cutaways/instruments")
    print(f"{'='*70}")
    return _ask_user("Proceed to Stage 6 (Final 4K Broadcast Master Assembly)?", auto_confirm)


__all__ = [
    "prompt_script_review",
    "prompt_audio_timeline_review",
    "prompt_visual_plates_review",
    "prompt_broadcast_cuts_review",
]
