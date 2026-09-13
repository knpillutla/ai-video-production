import json
from pathlib import Path

from src.scripts.local_translator import (
    LANGUAGE_NAMES,
    get_subtitle_bundle_languages,
    is_indian_language,
    translate_dialogue,
)


def format_timestamp_srt(seconds: float) -> str:
    """Format float seconds to SRT timecode: HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format float seconds to WebVTT timecode: HH:MM:SS.mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"


def format_timestamp_ass(seconds: float) -> str:
    """Format float seconds to ASS timecode: H:MM:SS.cc (centiseconds)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{centis:02d}"


def generate_srt(
    segments: list[dict],
    output_path: Path | str,
) -> Path:
    """Generate standard YouTube-compatible SRT subtitle file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    for idx, seg in enumerate(segments, 1):
        start_ts = format_timestamp_srt(seg["start"])
        end_ts = format_timestamp_srt(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{idx}\n{start_ts} --> {end_ts}\n{text}\n")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def generate_vtt(
    segments: list[dict],
    output_path: Path | str,
) -> Path:
    """Generate HTML5 browser-standard WebVTT subtitle file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = ["WEBVTT\n"]
    for idx, seg in enumerate(segments, 1):
        start_ts = format_timestamp_vtt(seg["start"])
        end_ts = format_timestamp_vtt(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{idx}\n{start_ts} --> {end_ts}\n{text}\n")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def generate_kinetic_ass(
    segments: list[dict],
    output_path: Path | str,
    language: str = "en",
    font_size: int = 42,
) -> Path:
    """Generate Hormozi-style kinetic typography ASS subtitle file with yellow highlight boxes."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Unicode font selection per regional language
    font_name = "Arial Black"
    if language == "te":
        font_name = "Suranna"
    elif language == "hi":
        font_name = "Baloo 2"
    elif language in ("ta", "kn", "ml"):
        font_name = "Segoe UI"

    ass_header = f"""[Script Info]
Title: CineAI Studio Kinetic Subtitles ({language})
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticDefault,{font_name},{font_size},&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,2.0,2,40,40,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogue_lines = []
    for seg in segments:
        start_ts = format_timestamp_ass(seg["start"])
        end_ts = format_timestamp_ass(seg["end"])
        raw_text = seg["text"].strip().replace("\n", " ")
        animated_text = f"{{\\fscx108\\fscy108}}{raw_text}"
        dialogue_lines.append(
            f"Dialogue: 0,{start_ts},{end_ts},KineticDefault,,0,0,0,,{animated_text}"
        )

    full_content = ass_header + "\n".join(dialogue_lines) + "\n"
    out.write_text(full_content, encoding="utf-8")
    return out


def generate_subtitle_bundle(
    base_segments: list[dict],
    base_language: str,
    output_dir: Path | str,
    default_subtitle_lang: str = "en",
) -> dict:
    """Generate complete multi-language subtitle tracks (.ass, .srt, .vtt) with manifest."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bundle_langs = get_subtitle_bundle_languages(base_language)
    if default_subtitle_lang not in bundle_langs:
        bundle_langs.insert(0, default_subtitle_lang)

    tracks_metadata = []
    burned_ass_path = None

    for lang in bundle_langs:
        # Translate segments for this language
        translated_segments = []
        for seg in base_segments:
            trans_text = translate_dialogue(seg["text"], base_language, lang)
            translated_segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": trans_text,
            })

        ass_file = out_dir / f"kinetic_{lang}.ass"
        srt_file = out_dir / f"{lang}.srt"
        vtt_file = out_dir / f"{lang}.vtt"

        generate_kinetic_ass(translated_segments, ass_file, language=lang)
        generate_srt(translated_segments, srt_file)
        generate_vtt(translated_segments, vtt_file)

        is_default = (lang == default_subtitle_lang)
        if is_default:
            burned_ass_path = ass_file

        tracks_metadata.append({
            "language_code": lang,
            "language_name": LANGUAGE_NAMES.get(lang, lang.upper()),
            "is_default": is_default,
            "ass_file": ass_file.name,
            "srt_file": srt_file.name,
            "vtt_file": vtt_file.name,
        })

    manifest = {
        "content_language": base_language,
        "default_subtitle_language": default_subtitle_lang,
        "is_indian_bundle": is_indian_language(base_language),
        "total_languages": len(bundle_langs),
        "tracks": tracks_metadata,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "manifest": manifest,
        "burned_ass_path": burned_ass_path or (out_dir / f"kinetic_{default_subtitle_lang}.ass"),
        "bundle_languages": bundle_langs,
    }


__all__ = [
    "format_timestamp_srt",
    "format_timestamp_vtt",
    "format_timestamp_ass",
    "generate_srt",
    "generate_vtt",
    "generate_kinetic_ass",
    "generate_subtitle_bundle",
]
