"""Concert Style Catalog: Turnkey Pre-Defined Concert Styles and Built-In Prompts.

Eliminates user guesswork by providing battle-tested, cinema-grade defaults for:
- Concept prompts
- Stage ensemble configurations
- Suno musical tag templates
- Autonomous wardrobe & accessory aesthetics
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class ConcertStylePreset:
    """Pre-defined concert style configuration with curated audio-visual directions."""

    style_id: str
    display_name: str
    prompt: str
    suno_tags_template: str
    stage_ensemble: str
    wardrobe_guidance: str
    default_instrument: str = "mic"
    default_bpm: int = 120
    default_position: str = "standing"  # "standing" or "sitting"


CONCERT_STYLES: dict[str, ConcertStylePreset] = {
    "carnatic": ConcertStylePreset(
        style_id="carnatic",
        display_name="Carnatic Classical Grand Concert",
        prompt="Grand Carnatic classical vocal concert with melodic raga, mridangam percussion, violin accompaniment, and powerful rhythmic sahityam",
        suno_tags_template="carnatic classical vocal concert, melodic raga, acoustic violin, mridangam percussion, traditional gamakas, expressive vocals, 120 bpm",
        stage_ensemble="Traditional Carnatic concert ensemble (acoustic violin accompanist, mridangam percussionist on carpeted stage riser, ghatam, and subtle acoustic drone)",
        wardrobe_guidance="Exquisite royal Kanjivaram silk ensemble adorned with intricate gold zardozi and temple border, closed high-mandarin collar with delicate gold choker, temple jhumkas, and fresh jasmine in her hair.",
        default_bpm=120,
        default_position="sitting",
    ),
    "carnatic-fusion": ConcertStylePreset(
        style_id="carnatic-fusion",
        display_name="Electric Carnatic Fusion Concert",
        prompt="Electric Carnatic fusion concert with blazing electric violin, syncopated mridangam rhythms, synth bass grooves, and powerful raga melodies",
        suno_tags_template="carnatic fusion concert, electric violin, driving mridangam, synth bass, fusion drums, energetic vocal melody, 128 bpm",
        stage_ensemble="Carnatic fusion band (electric violinist stage-right, mridangam master with acoustic pickup, synth keyboardist, bassist, fusion drum kit)",
        wardrobe_guidance="Contemporary Indo-western fusion ensemble with gold brocade accents, high mandarin collar, delicate modern choker, and polished stage styling.",
        default_bpm=128,
        default_position="standing",
    ),
    "hindustani": ConcertStylePreset(
        style_id="hindustani",
        display_name="Hindustani Classical Khyal Concert",
        prompt="Soulful Hindustani classical vocal concert with deep raag development, sarangi, sitar accompaniment, and crisp tabla rhythmic improvisation",
        suno_tags_template="hindustani classical vocal concert, soulful raag, sarangi, sitar accompaniment, crisp tabla rhythmic beats, classical vocals, 110 bpm",
        stage_ensemble="Traditional Hindustani ensemble (tabla player on stage riser, sitar and sarangi accompanists, harmonium, tanpura)",
        wardrobe_guidance="Regal Banarasi silk anarkali with delicate zari embroidery, high jewel neckline, pearl and gold choker, matching earrings, and traditional wrist bangles.",
        default_bpm=110,
        default_position="sitting",
    ),
    "party": ConcertStylePreset(
        style_id="party",
        display_name="High-Octane Concert Party Banger",
        prompt="Explosive concert party anthem with driving 4-on-the-floor kick, pumping synth bass, festival lasers, confetti blasts, and massive singalong chorus",
        suno_tags_template="high-octane party concert banger, 4-on-the-floor kick drum, pumping synth bass, festival laser synths, massive party crowd chorus, 130 bpm",
        stage_ensemble="Festival stage setup (DJ and electronic synth deck on illuminated riser, electric rhythm guitarist, energetic percussionist, live brass section)",
        wardrobe_guidance="Glittering metallic ruby or gold tailored stage outfit with high jewel collar, iridescent accents, delicate jewelry, polished performance boots.",
        default_bpm=130,
        default_position="standing",
    ),
    "entertainer": ConcertStylePreset(
        style_id="entertainer",
        display_name="Megastar High-Energy Entertainer Concert",
        prompt="Megastar high-energy stadium entertainer concert with powerhouse brass fanfares, thunderous stadium drums, crowd call-and-response chants, and electric showmanship",
        suno_tags_template="megastar stadium entertainer anthem, powerhouse brass fanfares, thunderous drums, crowd call-and-response chants, charismatic vocals, 132 bpm",
        stage_ensemble="Grand stadium spectacle band (twin electric guitarists, thunderous double-kick drummer, dynamic horn section, synth risers)",
        wardrobe_guidance="Regal showstopper tailored velvet coat in royal sapphire or crimson with gold bullion embroidery, high bandhgala collar, precision chronograph watch on left wrist.",
        default_bpm=132,
        default_position="standing",
    ),
    "beach": ConcertStylePreset(
        style_id="beach",
        display_name="Coastal Sunset Beach Concert Party",
        prompt="Breezy coastal sunset beach concert with acoustic guitars, tropical bongo percussion, lush ocean breeze ambiance, and uplifting celebratory melodies",
        suno_tags_template="coastal sunset beach concert, acoustic guitars, bongo percussion, tropical island rhythm, uplifting breezy melody, warm vocals, 118 bpm",
        stage_ensemble="Acoustic beach troupe (acoustic steel-string guitarist, bongo and cajon percussionist, ukulele accompanist, upright acoustic bassist)",
        wardrobe_guidance="Elegant tropical resort chic attire in sunset coral or turquoise with delicate linen patterns, high elegant neckline, delicate seashell and pearl necklace.",
        default_bpm=118,
        default_position="standing",
    ),
    "rock": ConcertStylePreset(
        style_id="rock",
        display_name="High-Energy Stadium Rock Concert",
        prompt="High-energy live stadium rock concert anthem with driving drums, distorted electric guitar riffs, punchy bassline, and explosive crowd chorus",
        suno_tags_template="high-energy live stadium rock concert anthem, driving drums, distorted electric guitar riffs, punchy bassline, stadium crowd chants, rock vocals, 130 bpm",
        stage_ensemble="Live rock band (lead electric guitarist stage-right, drummer on riser behind acrylic kit, bassist, synthesizer)",
        wardrobe_guidance="Tailored royal sapphire blue structured anarkali coat with gold metallic accents, high mandarin collar, delicate gold choker, polished leather boots.",
        default_bpm=130,
        default_position="standing",
    ),
    "pop": ConcertStylePreset(
        style_id="pop",
        display_name="Modern Stadium Pop Concert",
        prompt="Upbeat modern stadium concert pop anthem with synth arpeggios, punchy acoustic drums, catchy vocal hooks, and synchronized laser show",
        suno_tags_template="modern concert pop anthem, synth arpeggios, punchy acoustic drums, melodic vocal hooks, upbeat dance groove, 126 bpm",
        stage_ensemble="Contemporary pop band (synth keyboardist, acoustic drummer on illuminated riser, electric guitarist, bassist)",
        wardrobe_guidance="Chic modern jewel-toned concert gown in emerald or ruby with fine silver threadwork, high elegant neckline, delicate choker, slim wrist cuffs.",
        default_bpm=126,
        default_position="standing",
    ),
    "folk": ConcertStylePreset(
        style_id="folk",
        display_name="Vibrant High-Energy Folk Concert",
        prompt="Vibrant high-energy traditional folk concert anthem with energetic dhol and dafli percussion, festive melody, and lively crowd call-and-response",
        suno_tags_template="vibrant folk concert anthem, energetic dhol, dafli, shehnai accents, festive rhythm, folk vocals, 135 bpm",
        stage_ensemble="Folk percussion ensemble (dhol master on riser, dafli players, acoustic flutist, acoustic rhythm section)",
        wardrobe_guidance="Vibrant festive ethnic attire with rich mirrorwork borders, sunflower yellow and ruby red palette, high covered neckline, traditional silver jhumkas.",
        default_bpm=135,
        default_position="standing",
    ),
    "romantic": ConcertStylePreset(
        style_id="romantic",
        display_name="Soulful Acoustic Concert Ballad",
        prompt="Soulful romantic concert ballad with acoustic guitar, lush string orchestra, gentle piano chords, and emotive vocal phrasing",
        suno_tags_template="soulful acoustic concert ballad, acoustic guitar, lush string quartet, gentle grand piano, warm bass, emotive vocals, 90 bpm",
        stage_ensemble="Acoustic chamber ensemble (acoustic guitarist, grand pianist, cello and violin duo)",
        wardrobe_guidance="Graceful pastel peach silk evening attire, high neckline with delicate pearl pendant necklace, soft floral hair pins, minimal elegant styling.",
        default_bpm=90,
        default_position="standing",
    ),
    "qawwali": ConcertStylePreset(
        style_id="qawwali",
        display_name="High-Octane Sufi Qawwali Concert",
        prompt="High-octane Sufi qawwali concert with vigorous harmonium leads, rhythmic handclaps, energetic tabla, and soaring spiritual chorus harmonies",
        suno_tags_template="sufi qawwali concert, vigorous harmonium, rhythmic handclaps, energetic tabla, powerful chorus harmonies, sufi vocals, 125 bpm",
        stage_ensemble="Traditional Qawwali party (harmonium player, tabla player, chorus clapping troupe on carpeted stage)",
        wardrobe_guidance="Regal emerald green velvet sherwani-cut suit with antique gold embroidery, high bandhgala collar, traditional gold studs, dignified stage presence.",
        default_bpm=125,
        default_position="sitting",
    ),
    "dj": ConcertStylePreset(
        style_id="dj",
        display_name="Live Electronic DJ Concert Set",
        prompt="Electric live festival DJ set with pumping sub-bass, build-ups, massive beat drops, euphoric synth leads, and crowd hype chants",
        suno_tags_template="festival edm dj set, pumping sub-bass, euphoric synth leads, drum build-ups, massive beat drop, festival crowd vocals, 128 bpm",
        stage_ensemble="Illuminated DJ console riser (multi-channel DJ mixer, Pioneer CDJ decks, modular audio interface, laser banks, LED visual wall)",
        wardrobe_guidance="Sleek modern DJ performance streetwear or tailored bomber, premium over-ear DJ headphones around neck or over one ear, chronograph watch on left wrist.",
        default_instrument="dj_controller",
        default_bpm=128,
        default_position="standing",
    ),
}

DEFAULT_STYLE_KEY = "rock"


def resolve_concert_style(
    style_or_theme: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> ConcertStylePreset:
    """Resolve user input to a canonical ConcertStylePreset with optional custom prompt override."""
    target = str(style_or_theme or "").lower().strip()
    target_clean = re.sub(r"[^a-z0-9]+", "", target)

    # 1. Exact or longest substring match against style catalog keys
    matched_key: Optional[str] = None
    for key in sorted(CONCERT_STYLES.keys(), key=len, reverse=True):
        key_clean = re.sub(r"[^a-z0-9]+", "", key)
        if key == target or key_clean == target_clean or key in target or key_clean in target_clean:
            matched_key = key
            break

    # 2. Check display names for aliases
    if not matched_key:
        if "fusion" in target:
            matched_key = "carnatic-fusion"
        elif "dj" in target or "edm" in target or "electronic" in target or "remix" in target:
            matched_key = "dj"
        elif "carnatic" in target or "classic" in target:
            matched_key = "carnatic"
        elif "hindustani" in target or "khyal" in target:
            matched_key = "hindustani"
        elif "party" in target or "club" in target or "banger" in target:
            matched_key = "party"
        elif "entertain" in target or "showman" in target or "megastar" in target:
            matched_key = "entertainer"
        elif "beach" in target or "coastal" in target or "tropical" in target:
            matched_key = "beach"
        elif "rock" in target or "metal" in target:
            matched_key = "rock"
        elif "pop" in target or "synth" in target:
            matched_key = "pop"
        elif "folk" in target or "mass" in target:
            matched_key = "folk"
        elif "ballad" in target or "romantic" in target:
            matched_key = "romantic"
        elif "qawwali" in target or "sufi" in target:
            matched_key = "qawwali"

    base_preset = CONCERT_STYLES.get(matched_key or DEFAULT_STYLE_KEY, CONCERT_STYLES[DEFAULT_STYLE_KEY])

    # If user provided custom prompt, return preset with user's prompt overridden
    if custom_prompt and custom_prompt.strip():
        return ConcertStylePreset(
            style_id=base_preset.style_id,
            display_name=base_preset.display_name,
            prompt=custom_prompt.strip(),
            suno_tags_template=base_preset.suno_tags_template,
            stage_ensemble=base_preset.stage_ensemble,
            wardrobe_guidance=base_preset.wardrobe_guidance,
            default_instrument=base_preset.default_instrument,
            default_bpm=base_preset.default_bpm,
            default_position=base_preset.default_position,
        )

    return base_preset


def list_available_styles() -> list[str]:
    """Return all canonical pre-defined style identifiers."""
    return list(CONCERT_STYLES.keys())


__all__ = ["ConcertStylePreset", "CONCERT_STYLES", "resolve_concert_style", "list_available_styles"]
