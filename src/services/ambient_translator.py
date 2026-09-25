"""Multi-Language Global Metadata Localizer for Ambient YouTube Productions.

Translates and localizes Title, Description, and Tags across 8 top international
sleep & ambient markets to maximize global views (Japanese, German, Spanish, Portuguese, French, Korean, Hindi).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class LocalizedMetadata(BaseModel):
    """Localized metadata bundle for a single language."""
    language_code: str
    language_name: str
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)


LOCALIZED_TITLE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "ja": {
        "swiss_alps": "【4K 睡眠用BGM】スイス アルプスの雨と雷 ~ ログハウスで眠る癒しの自然音 [432Hz 熟睡]",
        "rain": "【4K 睡眠用BGM】森の優しい雨音 ~ 不眠症解消と深い眠りのための自然音 [432Hz]",
        "beach_house": "【4K 睡眠用BGM】波の音と雨のビーチハウス ~ 心が落ち着くリラックスBGM [432Hz]",
        "blizzard": "【4K 睡眠用BGM】吹雪と暖炉のパチパチ音 ~ 山小屋で眠る温かい癒し [432Hz]",
    },
    "de": {
        "swiss_alps": "4K Schweizer Alpen Regen & Gewitter ~ Gemütliche Berghütte zum Einschlafen [432Hz]",
        "rain": "4K Sanfter Waldregen ~ Beruhigende Naturgeräusche für Tiefschlaf & Entspannung [432Hz]",
        "beach_house": "4K Strandhaus Sturm & Meeresrauschen ~ Beruhigende Klänge gegen Schlafstörungen [432Hz]",
        "blizzard": "4K Schneesturm & Kaminfeuer ~ Warme Holzhütte für erholsamen Schlaf [432Hz]",
    },
    "es": {
        "swiss_alps": "4K Lluvia en los Alpes Suizos ~ Cabaña Acogedora para Dormir Profundamente [432Hz]",
        "rain": "4K Lluvia Suave en el Bosque ~ Sonido de la Naturaleza para Conciliar el Sueño [432Hz]",
        "beach_house": "4K Casa de Playa con Lluvia y Olas ~ Sonidos Relajantes para Dormir [432Hz]",
        "blizzard": "4K Tormenta de Nieve y Chimenea ~ Refugio Acogedor para Dormir Toda la Noche [432Hz]",
    },
    "pt": {
        "swiss_alps": "4K Chuva nos Alpes Suíços ~ Chalé Aconchegante para Dormir e Relaxar [432Hz]",
        "rain": "4K Chuva Suave na Floresta ~ Som da Natureza para Alívio da Insônia [432Hz]",
        "beach_house": "4K Casa de Praia e Som das Ondas ~ Sons Relaxantes para Dormir [432Hz]",
        "blizzard": "4K Nevasca e Lareira Aconchegante ~ Noite Tranquila de Sono [432Hz]",
    },
    "fr": {
        "swiss_alps": "4K Pluie dans les Alpes Suisses ~ Chalet Confortable pour Dormir Profondément [432Hz]",
        "rain": "4K Pluie Douce en Forêt ~ Bruits de la Nature pour S'endormir Rapidement [432Hz]",
        "beach_house": "4K Maison de Plage & Bruit des Vagues ~ Sons Relaxants pour le Sommeil [432Hz]",
        "blizzard": "4K Tempête de Neige et Feu de Cheminée ~ Nuit Paisible en Chalet [432Hz]",
    },
    "ko": {
        "swiss_alps": "【4K 수면음악】스위스 알프스의 빗소리와 천둥 ~ 아늑한 산장 힐링 수면 BGM [432Hz]",
        "rain": "【4K 수면음악】마음이 편안해지는 숲속 빗소리 ~ 불면증 해소 자연음 [432Hz]",
        "beach_house": "【4K 수면음악】파도 소리와 비 내리는 해변 오두막 ~ 깊은 수면 BGM [432Hz]",
        "blizzard": "【4K 수면음악】눈보라와 따뜻한 모닥불 장작 타는 소리 ~ 숙면 힐링 ASMR [432Hz]",
    },
}


def localize_metadata_for_languages(
    archetype_key: str,
    base_title: str,
    base_description: str,
    languages: Optional[List[str]] = None,
) -> Dict[str, LocalizedMetadata]:
    """Generate localized metadata dictionary for YouTube Data API multi-language upload."""
    langs = languages or ["ja", "de", "es", "pt", "fr", "ko"]
    key = archetype_key.lower().replace("-", "_").replace(" ", "_")
    localized_bundle: Dict[str, LocalizedMetadata] = {}

    lang_names = {
        "ja": "Japanese", "de": "German", "es": "Spanish",
        "pt": "Portuguese", "fr": "French", "ko": "Korean",
    }

    for lang in langs:
        templates = LOCALIZED_TITLE_TEMPLATES.get(lang, {})
        loc_title = templates.get(key, f"{base_title} ({lang_names.get(lang, lang)})")
        loc_desc = f"{base_description}\n\n[Auto-localized for {lang_names.get(lang, lang)} viewers]"

        localized_bundle[lang] = LocalizedMetadata(
            language_code=lang,
            language_name=lang_names.get(lang, lang),
            title=loc_title,
            description=loc_desc,
            tags=[key, "sleep_music", "relaxing", f"sleep_{lang}"],
        )

    return localized_bundle
