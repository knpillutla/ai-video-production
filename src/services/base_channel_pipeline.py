"""Unified Base Channel Pipeline Engine for Ambient & Relaxation Channels.

Provides centralized 3-stage execution (Photos -> 4K Master -> Long-Play Stretch),
Human-in-the-Loop review gates, resilient --id resumption banners, and reusable CLI parsers.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.telemetry import logger
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.notification import notification_service
from src.studios.ambient_world.ambient_producer import AmbientWorldProducer
from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


@dataclass
class ChannelPipelineConfig:
    """Metadata and defaults for a specific automated niche channel."""
    channel_name: str
    channel_handle: str
    output_dir: Path
    script_name: str
    default_hours: float = 3.0
    default_fade_black_hours: Optional[float] = None
    default_motion_model: str = "auto"
    strategy_description: str = ""


class BaseChannelPipeline:
    """Reusable pipeline runner executing all stages and review gates."""

    def __init__(self, config: ChannelPipelineConfig):
        self.config = config
        self.producer = AmbientWorldProducer(output_base_dir=config.output_dir)

    async def execute(
        self,
        sb: AmbientStoryboard,
        episode_id: Optional[str] = None,
        motion_model: str = "auto",
        long_play_hours: Optional[float] = None,
        fade_to_black_hours: Optional[float] = None,
        generate_short: bool = True,
        photos_only: bool = False,
        no_bgm: bool = False,
        auto_stretch: bool = False,
        allow_fallback: bool = False,
        uncompressed: bool = False,
    ) -> Dict[str, Any]:
        """Execute standardized 3-stage pipeline workflow with review gates and --id banners."""
        effective_hours = long_play_hours or self.config.default_hours
        effective_fade = fade_to_black_hours or self.config.default_fade_black_hours
        eff_model = motion_model or self.config.default_motion_model
        crf_val = 16 if uncompressed else 22

        logger.info(f"starting_channel_job: {self.config.channel_name} id={episode_id} motion={eff_model} photos_only={photos_only} no_bgm={no_bgm}")
        print(f"\n[DECISION - CHANNEL PIPELINE INITIALIZED]")
        print(f"   * Channel:  {self.config.channel_name} ({self.config.channel_handle})")
        print(f"   * Title:    {sb.title}")
        if self.config.strategy_description:
            print(f"   * Strategy: {self.config.strategy_description}")

        # Stage 1: Keyframe Photos or Full Master
        result = await self.producer.produce(
            sb=sb,
            episode_id=episode_id,
            motion_model=eff_model,
            long_play_hours=None,
            fade_to_black_hours=None,
            generate_short=generate_short,
            photos_only=photos_only,
            no_bgm=no_bgm,
            allow_fallback=allow_fallback,
        )

        ep_id = result["episode_id"]

        # Stage 1 Gate: Photos Review
        if photos_only:
            await notification_service.notify_keyframes_ready(
                channel_name=self.config.channel_name,
                episode_id=ep_id,
                title=sb.title,
                keyframe_paths=result["keyframes"],
                pipeline_script=self.config.script_name,
            )
            print("\n" + "=" * 70)
            print(f"[STAGE 1 COMPLETE] 4K KEYFRAME PHOTOS READY ({len(result['keyframes'])} Images)!")
            print(f"Episode ID:  {ep_id}")
            for idx, kf in enumerate(result["keyframes"], 1):
                print(f"Shot {idx} Photo: {kf}")
            print(f"\n[NEXT STEPS] TO PROCEED TO STAGE 2 (Generate 4K Video Motion & Master Audio):")
            print(f"   python scripts/channels/{self.config.script_name} --id {ep_id}")
            print("=" * 70 + "\n")
            return result

        # Stage 2 Gate: 4K Master Video Review
        master_path = Path(result["master_video_path"])
        nature_master_path = Path(result["master_nature_video_path"]) if result.get("master_nature_video_path") else None
        actual_dur = int(sb.total_duration)
        print("\n" + "=" * 70)
        print(f"[STAGE 2 COMPLETE] {actual_dur}-SECOND 4K MASTER READY ({len(sb.scenes)} Shots)!")
        print(f"Episode ID:       {ep_id}")
        print(f"Music Master:     {master_path.resolve()}")
        if nature_master_path and nature_master_path.is_file() and nature_master_path.resolve() != master_path.resolve():
            print(f"Pure Nature 4K:   {nature_master_path.resolve()}")
        if result.get("bgm_path"):
            print(f"Audio Track:      {result['bgm_path']}")
        if result.get("short_video_path"):
            print(f"9:16 Teaser:      {result['short_video_path']}")
        print("=" * 70)

        await notification_service.notify_channel_master_ready(
            channel_name=self.config.channel_name,
            episode_id=ep_id,
            title=result["title"],
            master_video_path=str(master_path.resolve()),
            short_video_path=result.get("short_video_path"),
            long_play_hours=effective_hours,
            stretch_script=self.config.script_name,
        )

        if not auto_stretch:
            stretch_cmd = f"python scripts/channels/{self.config.script_name} --id {ep_id} --auto-stretch --hours {effective_hours}"
            if effective_fade is not None:
                stretch_cmd += f" --fade-black {effective_fade}"
            print(f"\n[NEXT STEPS] TO PROCEED TO STAGE 3 (Lossless {effective_hours}-Hour Long-Play Stretch):")
            print(f"   {stretch_cmd}")
            print(f"   (Or click 'Approve & Stretch' in your review email)\n")
            print("=" * 70 + "\n")
            return result

        # Stage 3: Long-Play Stretch Execution
        fade_txt = f" (Fade-to-Black at {effective_fade}h)" if effective_fade else ""
        print(f"\n[STAGE 3 AUTO-STRETCH] Auto-stretching {actual_dur}s master to {effective_hours} Hours Long-Play{fade_txt}...")
        target_sec = effective_hours * 3600.0
        hour_label = int(effective_hours) if effective_hours.is_integer() else effective_hours
        
        suffix = f"_{int(effective_fade)}h_black" if effective_fade else ""
        long_play_path = master_path.parent / f"master_4k_{hour_label}hour{suffix}_broadcast.mp4"

        if not long_play_path.is_file() or long_play_path.stat().st_size < 1000:
            export_long_play_broadcast(
                source_4k_video=master_path,
                output_long_play=long_play_path,
                target_duration_seconds=target_sec,
                fade_to_black_hours=effective_fade,
                crf=crf_val,
            )

        # Stretch pure nature master if present
        if nature_master_path and nature_master_path.is_file() and nature_master_path.resolve() != master_path.resolve():
            lp_nature_path = master_path.parent / f"master_4k_{hour_label}hour_nature_only{suffix}_broadcast.mp4"
            if not lp_nature_path.is_file() or lp_nature_path.stat().st_size < 1000:
                print(f"[STAGE 3 AUTO-STRETCH] Auto-stretching Pure Nature master to {effective_hours} Hours (CRF {crf_val})...")
                export_long_play_broadcast(
                    source_4k_video=nature_master_path,
                    output_long_play=lp_nature_path,
                    target_duration_seconds=target_sec,
                    fade_to_black_hours=effective_fade,
                    crf=crf_val,
                )
            result["long_play_nature_video_path"] = str(lp_nature_path)

        result["long_play_video_path"] = str(long_play_path)
        print(f"[STAGE 3 COMPLETE] Long-Play Video Ready: {long_play_path.resolve()}\n")
        return result


def create_base_channel_parser(
    description: str,
    primary_choices: List[str],
    default_primary: str,
    default_hours: float = 3.0,
    default_fade_black: Optional[float] = None,
    supports_secondary: bool = False,
    secondary_default: Optional[str] = None,
) -> argparse.ArgumentParser:
    """Construct standard CLI parser for any channel pipeline."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--primary" if supports_secondary else "--archetype", dest="primary", type=str, default=default_primary, choices=primary_choices, help="Primary theme/archetype")
    if supports_secondary:
        parser.add_argument("--secondary", type=str, default=secondary_default or "rain", help="Secondary atmospheric element")
    parser.add_argument("--id", type=str, default=None, help="Episode ID to resume or reuse cached artifacts")
    parser.add_argument("--motion-model", type=str, default="auto", choices=["auto", "kling_v3", "kling_4k", "wan", "kling", "hunyuan", "lanczos"], help="Motion model (default: auto -> kling_v3 for <=5 shots)")
    parser.add_argument("--master-duration", type=float, default=None, choices=[60.0, 90.0, 120.0], help="Master duration in seconds")
    parser.add_argument("--shots", type=int, default=None, choices=[1, 2, 3, 4], help="Explicit visual shot count (1, 2, 3, or 4)")
    parser.add_argument("--hours", type=float, default=default_hours, help=f"Long-play target duration in hours (default: {default_hours})")
    parser.add_argument("--sleep", action="store_true", help="Enable circadian fade-to-black sleep mode (fades to black after 2.0h)")
    parser.add_argument("--fade-black", type=float, default=default_fade_black, help="Explicit hours after which video fades to black (e.g. 2.0)")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="Custom prompt or atmospheric mood enhancement (e.g. 'Warm stone fireplace with crackling oak logs and glowing embers')")
    parser.add_argument("--no-bgm", action="store_true", help="Disable external Suno BGM and preserve 100% natural audio from video clips (e.g. fireplace crackle, rain, wind)")
    parser.add_argument("--photos-only", action="store_true", help="Stage 1: Generate keyframe photos only for review")
    parser.add_argument("--no-short", action="store_true", help="Disable vertical short generation")
    parser.add_argument("--auto-stretch", action="store_true", help="Automatically stretch without waiting for approval")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow zoom-pan fallback if live diffusion fails")
    parser.add_argument("--keep-uncompressed", "--uncompressed", dest="uncompressed", action="store_true", help="Preserve uncompressed high-bitrate broadcast (CRF 16) instead of default optimized CRF 22")
    return parser

