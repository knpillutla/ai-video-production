"""End-to-End 4K Multi-Camera Live Stadium Concert Production Pipeline.

Independent concert studio orchestrator featuring:
1. Dynamic episode folder naming from Gemini generated title_en slug (e.g. prana_dhumukulu/ep-001).
2. Rule 7 Pre-flight script validation gate prompting user confirmation before generation.
3. Multilingual stadium concerts in any language with optional --prompt description.
4. Exactly 1 character plate + 5 distinct concert cutaways (Instrument, Orchestra, Stadium, Audience, Pyro).
5. Fail-fast Suno audio synthesis with zero foley degradation.
6. Targeted LatentSync lipsync on Cam 1 singing cuts + single-pass FFmpeg 4K broadcast assembly.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import re
import shutil
import time
from typing import Any, Optional

from src.compositor.virtual_artist_broadcast_service import assemble_broadcast_cuts
from src.compositor.vocal_compositor import probe_audio_duration
from src.compositor.vocal_packaging import export_vocal_production_bundle
from src.compositor.vocal_subtitles import build_vocal_subtitles
from src.compositor.vocal_title_card import create_vocal_title_card, resolve_song_type_label
from src.core.config import settings
from src.core.telemetry import logger
from src.core.utils.duration_parser import parse_duration
from src.domain.creative import Episode
from src.domain.repo import repo
from src.providers.llm import get_llm_adapter, resolve_llm_model, resolve_llm_provider
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.studios.concert_studio.concert_audio_service import synthesize_concert_audio
from src.studios.concert_studio.concert_director import synthesize_concert_broadcast_cuts, synthesize_concert_motion
from src.studios.concert_studio.concert_image_service import synthesize_concert_camera_rig
from src.studios.concert_studio.concert_prompt_engine import build_concert_gemini_prompt, build_concert_gemini_schema, get_offline_concert_broadcast_timeline
from src.studios.concert_studio.concert_review_gate import prompt_audio_timeline_review, prompt_broadcast_cuts_review, prompt_script_review, prompt_visual_plates_review
from src.studios.concert_studio.concert_setting_catalog import resolve_concert_setting
from src.studios.concert_studio.concert_style_catalog import resolve_concert_style
from src.studios.concert_studio.concert_workspace import resolve_concert_workspace, restore_concert_workspace_inputs


async def produce_concert_video(
    title: str | None = None, prompt: str | None = None, chars: str = "Radha", language: str = "te",
    duration: int | str = 60, instrument: str = "mic", has_orchestra: bool = True, theme: str | None = None,
    style: str | None = None, setting: str | None = None, venue_type: str | None = None,
    time_of_day: str | None = None, stage_setting: str | None = None, background: str | None = None,
    weather: str | None = None, image_model: str = "z-image", motion_model: str = "h3-max",
    model: str = "z-image", lora_model: str = "z-image", dataset_model: str = "z-image",
    network: str = "telugu_rhythms", force_live: bool = False, enable_lipsync: bool = True,
    use_kling: bool = False, episode_id: str | None = None, auto_confirm: bool = False,
    is_prod: bool = False, lipsync_model: str | None = "wav2lip", gender: str | None = None,
    position: str | None = None, is_dj: bool = False, spatial_3d_engine: str | None = None,
    onepass_bytedance: bool = False, llm_provider: str | None = None, llm_model: str | None = None,
    lora_scale: float = 0.82,
) -> Path:
    """Execute end-to-end multi-camera live concert production."""
    eff_image_model = image_model or model
    user = repo.get_default_user()
    ep_dur = parse_duration(duration) if duration is not None else None
    ep_ws, episode = resolve_concert_workspace(episode_id, network, user, title)
    scenes_dir, stems_dir, renders_dir, thumbs_dir = ep_ws / "scenes", ep_ws / "audio_stems", ep_ws / "master_renders", ep_ws / "thumbnails"
    for d in (scenes_dir, stems_dir, renders_dir, thumbs_dir): d.mkdir(parents=True, exist_ok=True)

    # Restore saved parameters on resumption
    cur_p = restore_concert_workspace_inputs(ep_ws, {
        "title": title, "chars": chars, "language": language, "prompt": prompt, "theme": theme,
        "style": style, "setting": setting, "venue_type": venue_type, "time_of_day": time_of_day,
        "stage_setting": stage_setting, "background": background, "weather": weather,
        "instrument": instrument, "position": position, "lipsync_model": lipsync_model,
        "spatial_3d_engine": spatial_3d_engine, "motion_model": motion_model, "is_prod": is_prod, "is_dj": is_dj,
        "onepass_bytedance": onepass_bytedance, "duration": duration, "duration_seconds": ep_dur,
        "llm_provider": llm_provider, "llm_model": llm_model, "lora_scale": lora_scale,
    })
    title, chars, language, prompt, theme = cur_p["title"], cur_p["chars"], cur_p["language"], cur_p["prompt"], cur_p["theme"]
    stage_setting, background, weather = cur_p["stage_setting"], cur_p["background"], cur_p["weather"]
    instrument = cur_p.get("instrument") or instrument or "mic"
    position, lipsync_model, is_prod, is_dj = cur_p["position"], cur_p["lipsync_model"], cur_p["is_prod"], cur_p["is_dj"]
    spatial_3d_engine, motion_model = cur_p.get("spatial_3d_engine") or spatial_3d_engine, cur_p.get("motion_model") or motion_model
    onepass_bytedance = cur_p.get("onepass_bytedance", onepass_bytedance)
    if ep_dur is None and (cur_p.get("duration_seconds") or cur_p.get("timeline_duration")):
        ep_dur = float(cur_p.get("duration_seconds") or cur_p.get("timeline_duration"))
    eff_motion_model = "kling" if use_kling else (motion_model or "wan")
    eff_3d_eng = spatial_3d_engine or ("h3_max" if (spatial_3d_engine and "h3" in spatial_3d_engine.lower()) else "kling")

    eff_llm_prov = resolve_llm_provider(cur_p.get("llm_provider") or llm_provider)
    eff_llm_model = resolve_llm_model(eff_llm_prov, cur_p.get("llm_model") or llm_model)

    if is_dj:
        if instrument == "mic": instrument = "dj_controller"
        if not style and not theme: style = "dj"

    preset = resolve_concert_style(style or ("dj" if is_dj else theme), prompt)
    v_preset = resolve_concert_setting(
        setting, venue_type=venue_type, time_of_day=time_of_day,
        stage_setting=stage_setting, background=background, weather=weather,
    )
    eff_pos = (position or getattr(preset, "default_position", "standing")).lower().strip()
    dj_prefix = "Live DJ Set • " if is_dj else ""
    eff_theme = f"{dj_prefix}{preset.display_name} @ {v_preset.display_name} ({eff_pos})"
    eff_lipsync_model = "bytedance" if onepass_bytedance else (lipsync_model or "wav2lip")
    is_soft = any(k in eff_theme.lower() for k in ("soft", "melody", "ballad", "acoustic", "slow", "soulful", "carnatic", "hindustani"))

    artist_banner = f"DJ {chars}" if is_dj else chars
    print(f"\n{'='*70}\n🎙️ 4K VIRTUAL ARTIST CONCERT PRODUCER: {artist_banner} [{language.upper()}] ({eff_pos})\n{'='*70}")
    print(f"📁 Workspace: {ep_ws}\n⏱️ Duration:  {ep_dur}s | Cameras: 6 Multi-Angle Rig | Setting: {v_preset.display_name}\n{'='*70}")

    u_inputs = {
        "title": title, "prompt": prompt, "theme": eff_theme, "style": style or preset.style_id, "setting": setting or v_preset.setting_id,
        "venue_type": v_preset.venue_type, "time_of_day": v_preset.time_of_day, "stage_setting": v_preset.stage_setting,
        "background": v_preset.background, "weather": v_preset.weather,
        "chars": chars, "gender": gender, "position": eff_pos, "is_dj": is_dj, "language": language, "duration_seconds": ep_dur, "instrument": instrument, "has_orchestra": has_orchestra,
        "llm_provider": eff_llm_prov, "llm_model": eff_llm_model,
        "model": model, "lora_model": lora_model, "dataset_model": dataset_model, "is_prod": is_prod, "lipsync_model": eff_lipsync_model,
        "spatial_3d_engine": eff_3d_eng, "motion_model": eff_motion_model, "onepass_bytedance": bool(onepass_bytedance),
        "network": network, "episode_id": str(episode.id), "pipeline_strategy": "concert_studio", "execution_mode": "live" if force_live else "test",
    }
    (ep_ws / "user_inputs.json").write_text(json.dumps(u_inputs, indent=2), encoding="utf-8")

    # Stage 1: Storyboard & 6-Camera Rig Generation
    sb_path = ep_ws / "storyboard.json"
    sc_path = ep_ws / "song_screenplay.json"
    g_prompt = build_concert_gemini_prompt(
        language=language, chars=chars, prompt=prompt, title=title, duration_seconds=ep_dur,
        instrument=instrument, has_orchestra=has_orchestra, theme=theme, style=style, setting=setting,
        venue_type=venue_type, time_of_day=time_of_day, stage_setting=stage_setting, background=background, weather=weather,
        network=network, gender=gender, position=eff_pos, is_dj=is_dj,
    )
    schema = build_concert_gemini_schema()
    prov_slug = eff_llm_prov.lower()
    in_meta = {"llm_provider": eff_llm_prov, "llm_model": eff_llm_model, "prompt": g_prompt}
    (ep_ws / f"{prov_slug}_inputs.json").write_text(json.dumps(in_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    (ep_ws / f"{prov_slug}_schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    (ep_ws / "llm_inputs.json").write_text(json.dumps(in_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    (ep_ws / "llm_schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    other_prov = "gemini" if prov_slug == "openai" else "openai"
    for st in (ep_ws / f"{other_prov}_inputs.json", ep_ws / f"{other_prov}_schema.json"):
        if st.is_file():
            try: st.unlink()
            except Exception: pass

    existing_sb = json.loads(sb_path.read_text(encoding="utf-8")) if (sb_path.is_file() and sb_path.stat().st_size > 1000) else {}
    has_new_plates = any(sc.get("camera_id") == "singer_orchestra_stage" for sc in existing_sb.get("scenes", []))
    if existing_sb and has_new_plates:
        print("[+] Stage 1: Reusing existing concert storyboard ($0.00 spend)")
        sb_data = existing_sb
    elif sc_path.is_file() and sc_path.stat().st_size > 1000:
        print("[+] Stage 1: Reusing existing song screenplay & lyrics from song_screenplay.json ($0.00 spend)")
        sb_data = json.loads(sc_path.read_text(encoding="utf-8"))
    elif not force_live:
        print("[+] Stage 1: Generating deterministic offline concert screenplay ($0.00 spend)")
        from src.studios.concert_studio.concert_directorial_engine import get_offline_concert_storyboard
        sb_data = get_offline_concert_storyboard(title=title, language=language, chars=chars, duration_seconds=ep_dur, instrument=instrument)
        for p in (sb_path, sc_path): p.write_text(json.dumps(sb_data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(f"[~] Stage 1: Directing 4K 1-plate concert screenplay with {eff_llm_prov.upper()} ({eff_llm_model})...")
        sb_data = await get_llm_adapter(provider=eff_llm_prov, model=eff_llm_model, strict=True).generate_structured(g_prompt, schema=schema)
        if not sb_data or not isinstance(sb_data, dict):
            raise RuntimeError(f"Script Generation Error: {eff_llm_prov.upper()} returned empty output. Fallbacks disabled.")
        for p in (sb_path, sc_path): p.write_text(json.dumps(sb_data, indent=2, ensure_ascii=False), encoding="utf-8")
    sb_data["id"], sb_data["episode_id"] = str(episode.id), str(episode.id)
    sb_data["is_dj"], sb_data["instrument"] = is_dj, instrument
    sb_data["llm_provider"], sb_data["llm_model"] = eff_llm_prov, eff_llm_model

    t_en = sb_data.get("title_en") or sb_data.get("title") or sb_data.get("song_title") or title
    if not t_en or t_en.strip().lower() in ("concert song", "live concert", "concert", "untitled"):
        raise RuntimeError("Script Generation Error: Model failed to produce a valid song title. Fallbacks disabled.")
    t_loc = sb_data.get("title_localized") or sb_data.get("localized_title") or t_en
    sb_data["title_en"], sb_data["title_localized"], episode.title = t_en, t_loc, t_en
    for p in (sb_path, sc_path): p.write_text(json.dumps(sb_data, indent=2, ensure_ascii=False), encoding="utf-8")
    repo.save_episode(episode)
    clean_slug = re.sub(r"[^a-zA-Z0-9]+", "_", t_en.lower()).strip("_") or "concert"
    if not episode_id and ep_ws.parent.name in ("new_concert", "telugu_stadium_concert", "live_concert", "concert_draft"):
        target_ws = Path(settings.storage.local_storage_root) / user.storage_container_name / "networks" / network / "music_video" / clean_slug / "ep-001"
        if target_ws != ep_ws:
            target_ws.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(ep_ws), str(target_ws))
            ep_ws = target_ws
            scenes_dir, stems_dir, renders_dir, thumbs_dir = ep_ws / "scenes", ep_ws / "audio_stems", ep_ws / "master_renders", ep_ws / "thumbnails"
            sb_path = ep_ws / "storyboard.json"
            print(f"[+] Workspace anchored to song title: {ep_ws}")

    # Stage 1: Review Gate
    t_loc = sb_data.get("title_localized") or t_en
    if not prompt_script_review(
        t_en, t_loc, chars, language, instrument, v_preset.display_name,
        sb_data.get("lyrics", ""), llm_provider=eff_llm_prov, llm_model=eff_llm_model, auto_confirm=auto_confirm,
    ):
        return sb_path

    # Stage 2: Audio Master (Fail-fast Suno synthesis)
    audio_path = await synthesize_concert_audio(
        storyboard_data=sb_data, stems_dir=stems_dir, duration_seconds=ep_dur or 60.0,
        title=t_en, episode_id=episode.id, force_live=force_live, language=language, is_soft=is_soft,
    )
    probed_dur = probe_audio_duration(audio_path) or (float(ep_dur) if ep_dur else 60.0)
    actual_dur = float(ep_dur) if (ep_dur and probed_dur > (float(ep_dur) + 3.0)) else probed_dur
    if actual_dur < probed_dur:
        trim_audio = stems_dir / f"music_master_{int(actual_dur)}s.mp3"
        if not (trim_audio.is_file() and trim_audio.stat().st_size > 10_000):
            import imageio_ffmpeg, subprocess
            fade_s = max(1.0, actual_dur - 3.0)
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-i", str(audio_path), "-t", str(actual_dur), "-af", f"afade=t=out:st={fade_s:.1f}:d=3.0", "-c:a", "libmp3lame", str(trim_audio)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if trim_audio.is_file() and trim_audio.stat().st_size > 10_000: audio_path = trim_audio

    # Stage 2.5: Real-Time Audio VAD Slicing & Synchronized Directorial Timeline
    from src.studios.concert_studio.concert_audio_slicer import slice_concert_audio
    from src.studios.concert_studio.concert_directorial_engine import direct_concert_broadcast_timeline

    c_direct_file = ep_ws / "concert_directorial_screenplay.json"
    cuts_tl = None
    if sb_path.is_file() and c_direct_file.is_file() and c_direct_file.stat().st_size > 1000:
        try: cuts_tl = json.loads(c_direct_file.read_text(encoding="utf-8")).get("broadcast_timeline")
        except Exception: pass
    if not cuts_tl:
        print(f"[~] Stage 2.5: Directing synchronized multi-camera timeline with {eff_llm_prov.upper()} ({eff_llm_model})...")
        audio_segs = slice_concert_audio(audio_path, actual_dur, export_stems_dir=None)
        llm = get_llm_adapter(provider=eff_llm_prov, model=eff_llm_model, strict=True) if force_live else None
        cuts_tl = await direct_concert_broadcast_timeline(
            llm=llm, segments=audio_segs, lyrics=sb_data.get("lyrics", ""),
            language=language, artist_name=chars, instrument=instrument,
            style=preset.display_name, force_live=force_live,
            audio_path=audio_path, stems_dir=None,
        )
        c_direct_doc = {
            "title_en": t_en, "title_localized": t_loc, "artist": chars, "instrument": instrument,
            "duration_seconds": actual_dur, "total_cuts": len(cuts_tl), "broadcast_timeline": cuts_tl,
        }
        c_direct_file.write_text(json.dumps(c_direct_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(f"[~] Stage 2.5: Reusing existing directorial screenplay ({len(cuts_tl)} cuts)...")
        total_tl_dur = max(float(c.get("end_time", 0.0)) for c in cuts_tl) if cuts_tl else 0.0
        if (duration is None or not duration) and total_tl_dur > 0:
            actual_dur = total_tl_dur
            if (stems_dir / "music_master.mp3").is_file(): audio_path = stems_dir / "music_master.mp3"
    sb_data["broadcast_timeline"] = cuts_tl
    sb_path.write_text(json.dumps(sb_data, indent=2, ensure_ascii=False), encoding="utf-8")
    if not prompt_audio_timeline_review(audio_path, actual_dur, cuts_tl or [], auto_confirm):
        return sb_path

    # Stage 3: Camera Rig 4K Keyframes & Static Scene 00 Title Card
    eff_img_model = image_model or model or ("flux" if is_prod else "z-image")
    eng_name = "Fal.ai Kling 3D" if "kling" in eff_3d_eng.lower() else "Minimax H3 Max"
    print(f"[~] Stage 3: Synthesizing master 4K camera plates via Option B 3D Spatial Video [{eng_name}]...")
    img_paths = await synthesize_concert_camera_rig(
        storyboard_data=sb_data, scenes_dir=scenes_dir, user_id=str(user.id),
        network=network, force_live=force_live, episode_id=episode.id, chars=chars,
        instrument=instrument, model=eff_img_model, lora_model=lora_model, dataset_model=dataset_model,
        motion_model=eff_motion_model, spatial_3d_engine=eff_3d_eng, lora_scale=float(cur_p.get("lora_scale", lora_scale)),
    )
    scene_00 = scenes_dir / "scene_00.jpg"
    if not (scene_00.is_file() and scene_00.stat().st_size > 1000):
        st_lbl = resolve_song_type_label(theme="Grand Arena Concert", idea="", genre="vocal", music_style="Live Concert", storyboard_data=sb_data, suno_tags=sb_data.get("suno_tags"), hook_thesis=sb_data.get("hook_thesis"), song_type=sb_data.get("song_type"), mood=sb_data.get("mood"))
        create_vocal_title_card(base_image_path=img_paths[0], output_path=scene_00, title_localized=t_loc, title_en=t_en, song_type=st_lbl, language=language)
    if not prompt_visual_plates_review(scenes_dir, img_paths, auto_confirm):
        return sb_path

    # Stage 4: Camera Motion Synthesis
    print(f"[~] Stage 4: Synthesizing camera motion [model={motion_model}] for {len(img_paths)} stage plates...")
    motion_map = await synthesize_concert_motion(
        storyboard_data=sb_data, scenes_dir=scenes_dir, audio_path=audio_path,
        use_kling=use_kling, force_live=force_live, episode_id=episode.id, motion_model=motion_model,
    )

    # Stage 5: Directorial Switching Assembly with Targeted Cut Lip-Sync
    print(f"[~] Stage 5: Slicing cuts & applying lip-sync [model={eff_lipsync_model}] strictly to Cam 1 singing cuts...")
    cuts = await synthesize_concert_broadcast_cuts(
        storyboard_data=sb_data, scenes_dir=scenes_dir, audio_path=audio_path,
        motion_map=motion_map, force_live=force_live, episode_id=episode.id,
        enable_lipsync=enable_lipsync, lipsync_model=eff_lipsync_model,
        onepass_bytedance=bool(onepass_bytedance),
    )
    if not prompt_broadcast_cuts_review(cuts, eff_lipsync_model, auto_confirm):
        return sb_path

    out_ass = ep_ws / f"subtitles_{language}.ass"
    sub_path, _ = build_vocal_subtitles(sb_data, language, out_ass, actual_dur, audio_path=audio_path)
    final_render = renders_dir / f"master_concert_ep{episode.id}_{language}.mp4"
    render_valid = final_render.is_file() and final_render.stat().st_size > 10_000_000 and probe_audio_duration(final_render) >= (actual_dur - 3.0)
    if not render_valid:
        print("[~] Stage 6: Assembling single-pass 4K broadcast with 2.5D camera glides...")
        await assemble_broadcast_cuts(cuts=cuts, song_path=audio_path, sub_path=sub_path, out_video_path=final_render, total_duration=actual_dur)
    else:
        print(f"[+] Stage 6: Reusing existing 4K concert broadcast ({actual_dur:.1f}s) ($0.00 spend)")

    # Stage 7 & 8: Thumbnail & Packaging Export
    thumb_path = thumbs_dir / f"thumb_{language}.jpg"
    if not (thumb_path.is_file() and thumb_path.stat().st_size > 10_000):
        generate_episodic_thumbnail(output_path=thumb_path, base_image_path=img_paths[0], badge_config=EpisodicBadgeConfig(episode_number=1, language=language, style="pill", position="top_left", custom_label=f"LIVE CONCERT • {language.upper()}"), headline=t_loc, enable_vfx=True)
    else:
        print(f"[+] Stage 7: Reusing existing thumbnail: {thumb_path.name} ($0.00 spend)")
    export_vocal_production_bundle(episode=episode, ep_dir=ep_ws, sb_data=sb_data, actual_dur=actual_dur, t_start=time.time(), language=language, keyframe_path=img_paths[0], master_video_path=final_render)
    print(f"\n{'='*70}\n✅ 4K CONCERT BROADCAST READY: {final_render.name} ({actual_dur:.1f}s)\n{'='*70}")
    return final_render

__all__ = ["produce_concert_video", "resolve_concert_workspace"]
