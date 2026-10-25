"""Studio CLI: Produce 4K Multi-Camera Live Stadium Concert Broadcast Video.

Delegates entirely to the independent src.studios.concert_studio package:
- Multilingual stadium concert support in any language with optional --prompt description.
- Dynamic folder naming matching the Gemini generated title_en slug (e.g. prana_dhumukulu/ep-001).
- Script validation gate prompting user confirmation before audio/video generation.
- Exactly 1 character plate + 5 distinct concert cutaways (Instrument, Orchestra, Stadium, Audience, Pyro).
- Zero impact or dependencies on standard music video code.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.studios.concert_studio import produce_concert_video


def main():
    parser = argparse.ArgumentParser(description="Produce 4K Multi-Camera Live Virtual Artist Concert Video")
    parser.add_argument("--id", type=str, default=None, help="Episode ID or folder name to resume (e.g. ep-001)")
    parser.add_argument("--title", type=str, default=None, help="Song title (defaults to Gemini generated title)")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="Song creative concept, theme, or narrative description")
    parser.add_argument("--theme", type=str, default=None, help="Concert theme (defaults to style preset)")
    parser.add_argument("--style", "-s", type=str, default=None, help="Pre-defined concert style (carnatic, hindustani, rock, pop, folk, romantic, qawwali)")
    parser.add_argument("--setting", "--venue", dest="setting", type=str, default=None, help="Concert setting preset or seed")
    parser.add_argument("--venue-type", "--canvas", dest="venue_type", type=str, default=None, choices=["indoor", "outdoor", "hybrid"], help="Venue architecture type (indoor, outdoor, hybrid)")
    parser.add_argument("--time-of-day", "--light-setting", dest="time_of_day", type=str, default=None, help="Time of day / lighting (dawn, morning, noon, golden_hour, sunset, twilight, evening, night)")
    parser.add_argument("--stage-setting", dest="stage_setting", type=str, default=None, help="Global stage setup (stadium, festival_stage, rooftop, balcony, beach_platform, temple_hall, cathedral, jazz_club, tiny_desk, warehouse, garden_courtyard, yacht_deck, opera_house, sofa_lounge, living_room, amphitheatre, club_deck, plaza, desert_oasis, cavern)")
    parser.add_argument("--background", dest="background", type=str, default=None, help="Backdrop scenery (arena_crowd, city_skyline, beach_ocean, forest_woods, mountain_peaks, desert_dunes, heritage_monument, opera_auditorium, lakefront, tokyo_neon, cathedral_nave, botanical_garden, mediterranean_coast, industrial_brick)")
    parser.add_argument("--weather", dest="weather", type=str, default=None, help="Atmospheric weather condition (clear, cloudy, rain, snow, mist_fog)")
    parser.add_argument("--artist-name", "--chars", dest="chars", type=str, default=None, help="Lead singer artist name")
    parser.add_argument("--gender", type=str, default=None, choices=["male", "female"], help="Vocal & artist gender (defaults to inferred from artist name / LoRA)")
    parser.add_argument("--solo-female", dest="solo_female", action="store_true", default=False, help="Solo female vocalist performance")
    parser.add_argument("--solo-male", dest="solo_male", action="store_true", default=False, help="Solo male vocalist performance")
    parser.add_argument("--position", "--posture", dest="position", type=str, default=None, choices=["standing", "sitting"], help="Performer position (standing or sitting, defaults to style default)")
    parser.add_argument("--language", "-l", type=str, default=None, help="Language code (te, hi, ta, kn, pa, en, es, fr, etc.)")
    parser.add_argument("--duration", "-d", type=str, default=None, help="Duration (e.g. 60s, 120s)")
    parser.add_argument("--instrument", type=str, default="mic", help="Lead instrument (mic [default], acoustic_guitar, violin, sitar)")
    parser.add_argument("--no-orchestra", dest="orchestra", action="store_false", default=True, help="Disable live backing orchestra")
    import os
    env_img = os.getenv("IMAGE_MODEL", "z-image")
    env_lora = "flux" if "flux" in env_img.lower() else "z-image"
    parser.add_argument("--image-model", "--model", dest="image_model", type=str, default=env_img, help="Image model (flux, flux-dev, flux-pro-ultra, z-image)")
    parser.add_argument("--motion-model", dest="motion_model", type=str, default=None, help="Motion model (h3-max [default, Minimax H3 Max 3D], kling [Kling 3D], drone, sadtalker, wan)")
    parser.add_argument("--lora-model", type=str, default=env_lora, help="LoRA model (default: z-image)")
    parser.add_argument("--dataset-model", type=str, default=env_lora, help="Turnaround dataset model (default: z-image)")
    parser.add_argument("--network", type=str, default="telugu_rhythms", help="Distribution network")
    parser.add_argument("--live", action="store_true", default=False, help="Enable live paid API generation")
    parser.add_argument("--prod", action="store_true", default=False, help="Enable production models (defaults lipsync to Kling)")
    parser.add_argument("--lipsync-model", "--lipsync", dest="lipsync_model", type=str, default="wav2lip", help="Lipsync model (wav2lip [default CPU ONNX], kling [Fal Kling AI], sadtalker, sync-lipsync)")
    parser.add_argument("--no-lipsync", action="store_false", dest="enable_lipsync", help="Disable lipsync")
    parser.add_argument("--3d-engine", "--spatial-3d-model", "--orbit-engine", dest="spatial_3d_engine", type=str, default=None, choices=["kling", "kling-3d", "king-3d", "king", "h3-max", "h3", "minimax"], help="Option B 3D Spatial Video Engine: kling (Kling 3D 10s, default) or h3-max (Minimax H3 Max 5s)")
    parser.add_argument("--use-kling", action="store_true", default=False, help="Use Kling 3D for spatial video and cutaway motion")
    parser.add_argument("--onepass-bytedance", "--bytedance-1pass", "--omnihuman", "--bytedance", dest="onepass_bytedance", action="store_true", default=False, help="1-pass ByteDance OmniHuman audio-driven movement + lip-sync (takes precedence over 2-step pipeline)")
    parser.add_argument("--dj", dest="is_dj", action="store_true", default=False, help="Produce as a live DJ concert set with DJ console, multi-channel mixer, CDJ jog wheels, and over-ear headphones")
    parser.add_argument("--llm-provider", dest="llm_provider", type=str, default="gemini", choices=["gemini", "openai"], help="LLM provider for scriptwriting and screenplay (default: gemini)")
    parser.add_argument("--llm-model", dest="llm_model", type=str, default=None, help="Specific LLM model (e.g. gpt-4o, o3-mini, chatgpt-4o-latest, gpt-4.5-preview)")
    parser.add_argument("--lora-scale", dest="lora_scale", type=float, default=0.82, help="LoRA scale for character consistency (default: 0.82)")
    parser.add_argument("-y", "--yes", action="store_true", default=False, help="Auto-confirm script validation gate")
    args = parser.parse_args()

    if args.llm_provider:
        import os
        os.environ["LLM_PROVIDER"] = args.llm_provider
    if args.llm_model:
        import os
        if args.llm_provider == "gemini":
            os.environ["GEMINI_MODEL"] = args.llm_model
        else:
            os.environ["OPENAI_MODEL"] = args.llm_model
    if args.lora_scale is not None:
        import os
        os.environ["LORA_SCALE"] = str(args.lora_scale)

    # If --use-kling was set, map to motion_model kling
    eff_motion_model = "kling" if args.use_kling else args.motion_model
    eff_3d_engine = "kling" if (args.use_kling or (eff_motion_model and any(k in eff_motion_model.lower() for k in ("kling", "king")))) else args.spatial_3d_engine

    eff_img_model = args.image_model
    eff_lora_model = args.lora_model
    eff_dataset_model = args.dataset_model
    if args.prod or (eff_img_model and "flux" in eff_img_model.lower()):
        if eff_img_model == "z-image" and args.prod:
            eff_img_model = "flux"
        if args.lora_model == "z-image":
            eff_lora_model = "flux"
        if args.dataset_model == "z-image":
            eff_dataset_model = "flux"

    asyncio.run(produce_concert_video(
        title=args.title,
        prompt=args.prompt,
        episode_id=args.id,
        theme=args.theme,
        style=args.style,
        setting=args.setting,
        venue_type=args.venue_type,
        time_of_day=args.time_of_day,
        stage_setting=args.stage_setting,
        background=args.background,
        weather=args.weather,
        chars=args.chars,
        gender="female" if args.solo_female else ("male" if args.solo_male else args.gender),
        position=args.position,
        is_dj=args.is_dj,
        language=args.language,

        duration=args.duration,
        instrument=args.instrument,
        has_orchestra=args.orchestra,
        image_model=eff_img_model,
        motion_model=eff_motion_model,
        model=eff_img_model,
        lora_model=eff_lora_model,
        dataset_model=eff_dataset_model,
        network=args.network,
        force_live=args.live,
        enable_lipsync=args.enable_lipsync,
        use_kling=args.use_kling,
        auto_confirm=args.yes,
        is_prod=args.prod,
        lipsync_model=args.lipsync_model,
        spatial_3d_engine=eff_3d_engine,
        onepass_bytedance=args.onepass_bytedance,
        llm_provider=args.llm_provider,
        llm_model=args.llm_model,
        lora_scale=args.lora_scale,
    ))


if __name__ == "__main__":
    main()
