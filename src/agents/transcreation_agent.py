"""Cultural Transcreation & Multilingual Localization Agent."""

from pathlib import Path
from typing import Any
from src.core.telemetry import logger
from src.scripts.local_subtitles import generate_kinetic_ass, generate_srt
from src.scripts.local_translator import get_subtitle_bundle_languages, translate_dialogue


class TranscreationAgent:
    """Specialized Agent for regional cultural adaptation and multi-language subtitle suites."""

    def transcreate_dialogue(self, dialogue_text: str, source_lang: str, target_lang: str) -> str:
        """Transcreate speech lines with idiomatic cultural flavor (Telugu/Hindi)."""
        return translate_dialogue(dialogue_text, source_lang, target_lang)

    def generate_multilingual_subtitle_bundle(
        self,
        base_segments: list[dict[str, Any]],
        output_dir: Path | str,
        primary_language: str = "te",
    ) -> dict[str, Any]:
        """Generate a complete bundle of localized subtitles (SRT and kinetic ASS)."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        target_langs = get_subtitle_bundle_languages(primary_language)
        manifest: dict[str, dict[str, str]] = {}

        for lang in target_langs:
            # Transcreate each subtitle segment into target language
            localized_segs = []
            for seg in base_segments:
                trans_text = self.transcreate_dialogue(seg["text"], source_lang=primary_language, target_lang=lang)
                localized_segs.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": trans_text,
                })

            srt_file = out_dir / f"captions_{lang}.srt"
            ass_file = out_dir / f"kinetic_{lang}.ass"

            generate_srt(localized_segs, srt_file)
            generate_kinetic_ass(localized_segs, ass_file, language=lang)

            manifest[lang] = {
                "srt": str(srt_file),
                "ass": str(ass_file),
                "is_default": (lang == "en" if primary_language != "en" else True),
            }

        logger.info(f"transcreation_bundle_generated: {len(target_langs)} languages in {out_dir}")
        return {
            "primary_language": primary_language,
            "bundle_languages": target_langs,
            "default_subtitle_language": "en" if primary_language != "en" else primary_language,
            "manifest": manifest,
        }


transcreation_agent = TranscreationAgent()

__all__ = ["TranscreationAgent", "transcreation_agent"]
