"""Interactive Image Quality Gate for Keyframe Review & Directional Recreation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from src.core.telemetry import logger


@dataclass
class ImageQualityGateDecision:
    """Decision outcome from the interactive image quality gate."""

    action: str  # "proceed" | "recreate_specific" | "recreate_all" | "recreate_script" | "cancel"
    target_scene_indices: list[int] = field(default_factory=list)
    prompt_overrides: dict[int, str] = field(default_factory=dict)


def _format_scene_row(idx: int, sc: dict[str, Any], scenes_dir: Path) -> str:
    """Format single scene row for terminal display."""
    shot_type = sc.get("shot_type", "medium").upper()
    dur = float(sc.get("duration_seconds", sc.get("duration", 4.0)))
    img_path = scenes_dir / f"scene_{idx:02d}.jpg"
    size_str = f"{img_path.stat().st_size // 1024} KB" if (img_path.is_file() and img_path.stat().st_size > 0) else "MISSING"
    raw_prompt = sc.get("visual_prompt") or sc.get("visual_description") or ""
    prompt_snippet = (raw_prompt[:65] + "...") if len(raw_prompt) > 65 else (raw_prompt or "Scene visual description")
    return f"  Scene {idx:02d}: [{shot_type:<6}] {dur:4.1f}s | {size_str:>8} | {img_path.name}\n            \"{prompt_snippet}\""


def execute_image_quality_gate(
    scenes_list: list[dict[str, Any]],
    scenes_dir: Path,
    auto_confirm: bool = False,
    custom_input_fn: Any = None,
) -> ImageQualityGateDecision:
    """Display generated scene keyframes and prompt user to approve, recreate specific/all, or cancel.

    Args:
        scenes_list: List of scene definitions from storyboard.
        scenes_dir: Directory where scene_XX.jpg keyframes reside.
        auto_confirm: If True (CI/test/automation), automatically approve all images.
        custom_input_fn: Optional mockable input function for automated testing.

    Returns:
        ImageQualityGateDecision: User's directorial choice.
    """
    if auto_confirm:
        logger.info("image_quality_gate: auto_confirm=True -> approving all keyframes")
        return ImageQualityGateDecision(action="proceed")

    input_func = custom_input_fn or input

    print("\n" + "=" * 78)
    print(" PHASE 2 IMAGE QUALITY GATE: KEYFRAME VISUAL REVIEW & APPROVAL")
    print("=" * 78)
    print(" Review all generated scene keyframes before costly MP4 & motion synthesis:\n")

    for i, sc in enumerate(scenes_list):
        idx = sc.get("scene_index", sc.get("scene_number", i))
        print(_format_scene_row(idx, sc, scenes_dir))

    print("-" * 78)
    print(" Storage Path:", str(scenes_dir))
    print("-" * 78)
    print(" Select Action:")
    print("  [Enter] / [1]  Approve all images & Proceed to Video Motion & MP4 Creation")
    print("  [2]            Recreate Specific Image(s) (select scene numbers)")
    print("  [3]            Recreate All Images (keep current script & storyboard)")
    print("  [4]            Recreate Script & All Images (regenerate LLM script + images)")
    print("  [E] / [5]      Cancel / Abort Production (zero video motion/music credits spent)")
    print("=" * 78)

    try:
        raw_choice = input_func("\nSelect action [Enter/1/2/3/4/E]: ").strip().lower()
    except Exception:
        return ImageQualityGateDecision(action="proceed")

    if raw_choice in ("", "1", "p", "proceed", "y", "yes", "approve"):
        return ImageQualityGateDecision(action="proceed")

    if raw_choice in ("e", "exit", "q", "cancel", "n", "no", "5"):
        print("[!] Production cancelled at Image Quality Gate. Zero motion/video credits spent.\n")
        return ImageQualityGateDecision(action="cancel")

    if raw_choice in ("3", "all", "recreate_all"):
        return ImageQualityGateDecision(action="recreate_all")

    if raw_choice in ("4", "script", "recreate_script"):
        return ImageQualityGateDecision(action="recreate_script")

    if raw_choice in ("2", "specific", "recreate_specific"):
        print("\nEnter scene number(s) to recreate (e.g. 0 or 0, 2):")
        try:
            raw_scenes = input_func("Scene index(es): ").strip()
        except (EOFError, KeyboardInterrupt):
            raw_scenes = ""

        target_indices: list[int] = []
        for part in raw_scenes.replace(";", ",").split(","):
            part_clean = part.strip()
            if part_clean.isdigit():
                target_indices.append(int(part_clean))

        if not target_indices:
            print("[!] No valid scene numbers provided. Proceeding with existing images.")
            return ImageQualityGateDecision(action="proceed")

        # Optional prompt override for selected scenes
        overrides: dict[int, str] = {}
        for s_idx in target_indices:
            try:
                ov = input_func(f"Optional new prompt for Scene {s_idx:02d} (or press Enter to reuse): ").strip()
                if ov:
                    overrides[s_idx] = ov
            except (EOFError, KeyboardInterrupt):
                break

        return ImageQualityGateDecision(
            action="recreate_specific",
            target_scene_indices=target_indices,
            prompt_overrides=overrides,
        )

    return ImageQualityGateDecision(action="proceed")


__all__ = ["ImageQualityGateDecision", "execute_image_quality_gate"]
