"""Unit tests for Vocal Performer Modality (Solo Male, Solo Female, Duet)

and Kids 3D Animation Safety Directive (Child safety & platform compliance).
100% deterministic, offline test suite ($0.00 spend - Rule 8).
"""

import pytest
from src.compositor.genre_strategies.vocal_cast_builder import (
    build_cast_and_visual_directives,
    build_vocal_suno_tags,
    is_kids_song_genre,
)
from src.compositor.vocal_title_card import resolve_song_mood_label
from src.services.character_archetypes import ArchetypeSpec


@pytest.fixture
def sample_cast():
    fem = ArchetypeSpec(
        name="Aarohi", age=24, face="almond eyes",
        hair="silky dark waves", skin="warm honey", palette="scarlet and gold", seed_offset=10001,
    )
    male = ArchetypeSpec(
        name="Kabir", age=26, face="sharp jawline",
        hair="tapered crop", skin="warm wheatish", palette="deep indigo and ivory", seed_offset=20002,
    )
    return fem, male


def test_is_kids_song_genre():
    assert is_kids_song_genre("kids_rhyme_song") is True
    assert is_kids_song_genre("nursery_rhyme") is True
    assert is_kids_song_genre("romantic_melody", "playful kids rhyme") is True
    assert is_kids_song_genre("romantic_melody", "soulful love story") is False


def test_build_vocal_suno_tags():
    # Kids song tags
    kids_male = build_vocal_suno_tags("kids_rhyme_song", culture="Indian", gender="male")
    assert "kids song" in kids_male
    assert "ukulele" in kids_male
    assert "glockenspiel" in kids_male
    assert "male vocals" in kids_male

    # Romantic female tags
    rom_fem = build_vocal_suno_tags("romantic_melody", culture="Bengali", gender="female")
    assert "romantic ballad" in rom_fem
    assert "female vocals" in rom_fem
    assert "acoustic guitar" in rom_fem

    # Duet tags
    rom_duet = build_vocal_suno_tags("romantic_melody", culture="Yoruba", gender="duet")
    assert "duet, male and female vocals" in rom_duet


def test_solo_male_directive(sample_cast):
    fem, male = sample_cast
    cast_dir, neg = build_cast_and_visual_directives(
        slot=1, fem=fem, male=male, culture="Indian", setting="River Promenade", gender="male", is_kids=False,
    )
    assert "SOLO MALE LEAD DIRECTIVE" in cast_dir
    assert male.name in cast_dir
    assert "chronograph watch strapped securely to his LEFT WRIST" in cast_dir
    assert "NO WOMEN" in cast_dir
    assert "NO FEMALE CHARACTERS" in cast_dir
    assert "woman" in neg
    assert "female" in neg


def test_solo_female_directive(sample_cast):
    fem, male = sample_cast
    cast_dir, neg = build_cast_and_visual_directives(
        slot=1, fem=fem, male=male, culture="Indian", setting="River Promenade", gender="female", is_kids=False,
    )
    assert "SOLO FEMALE LEAD DIRECTIVE" in cast_dir
    assert fem.name in cast_dir
    assert "4-ZONE ACCESSORIES" in cast_dir
    assert "NO MEN" in cast_dir
    assert "NO MALE CHARACTERS" in cast_dir
    assert "man" in neg
    assert "male" in neg


def test_kids_animation_safety_directive(sample_cast):
    fem, male = sample_cast
    # Kids Solo Boy
    cast_boy, neg_boy = build_cast_and_visual_directives(
        slot=1, fem=fem, male=male, culture="Indian", setting="Toy Village", gender="male", is_kids=True,
    )
    assert "3D Pixar / Disney animated storybook CGI render" in cast_boy
    assert "STRICT PROHIBITION against photorealistic real human children" in cast_boy
    assert "photorealistic" in neg_boy
    assert "real human photo" in neg_boy

    # Kids Solo Girl
    cast_girl, neg_girl = build_cast_and_visual_directives(
        slot=1, fem=fem, male=male, culture="African", setting="Savannah Playground", gender="female", is_kids=True,
    )
    assert "3D Pixar / Disney animated storybook CGI render" in cast_girl
    assert "photorealistic" in neg_girl


def test_kids_title_card_badge():
    badge = resolve_song_mood_label(sub_genre="kids_rhyme_song", mood="playful")
    assert "KIDS FUN & RHYME" in badge
    assert "•" in badge


def test_gemini_lyrics_perspective_directives():
    from src.compositor.genre_strategies.vocal_strategy import VocalStrategy
    strat = VocalStrategy()

    # Solo Male Prompt
    p_male = strat.build_gemini_prompt(
        title="Pyaar Ke Raste", duration_seconds=180, language="hi", gender="male", theme="love journey",
    )
    assert "VOCAL PERFORMER PERSPECTIVE (SOLO MALE)" in p_male
    assert "Strictly NO female lines" in p_male
    assert "male vocals" in p_male

    # Solo Female Prompt
    p_female = strat.build_gemini_prompt(
        title="Hawaaon Ke Sang", duration_seconds=210, language="hi", gender="female", theme="romantic melody",
    )
    assert "VOCAL PERFORMER PERSPECTIVE (SOLO FEMALE)" in p_female
    assert "Strictly NO male lines" in p_female
    assert "female vocals" in p_female

    # Duet Prompt
    p_duet = strat.build_gemini_prompt(
        title="Milan", duration_seconds=240, language="hi", gender="duet", theme="romantic duet",
    )
    assert "VOCAL PERFORMER PERSPECTIVE (DUET)" in p_duet
    assert "call-and-response couplets" in p_duet
    assert "duet, male and female vocals" in p_duet


def test_scene_0_title_card_generation(tmp_path):
    from PIL import Image
    from src.compositor.vocal_title_card import create_vocal_title_card

    base_img = tmp_path / "scene_01.jpg"
    Image.new("RGB", (3840, 2160), color=(30, 45, 60)).save(base_img, format="JPEG")

    out_card = tmp_path / "scene_00.jpg"
    res = create_vocal_title_card(
        base_image_path=base_img,
        output_path=out_card,
        title_localized="हवाओं के संग",
        title_en="Hawaaon Ke Sang",
        song_type="Romantic Song",
        language="hi",
    )
    assert res.is_file()
    assert res.stat().st_size > 1000
    with Image.open(res) as im:
        assert im.size == (3840, 2160)


def test_high_ctr_dynamic_pose_directives():
    from src.compositor.genre_strategies.vocal_poses import (
        build_environmental_pose_directive,
        get_offline_dynamic_scene_poses,
    )
    from src.compositor.genre_strategies.vocal_strategy import VocalStrategy

    # Test Female Pose Directive
    fem_dir = build_environmental_pose_directive(gender="female", theme="Alpine Romance", num_scenes=3)
    assert "AUTONOMOUS CONTEXT-DRIVEN POSE & FRAMING DIRECTIVE (NO HARDCODED POSES)" in fem_dir
    assert "AUTONOMOUS SOLO FEMALE SENSORY IMMERSION" in fem_dir
    assert "UNIVERSAL FEMALE COMPOSITION & ACCESSORIES" in fem_dir
    assert "AUTONOMOUS CONTEXTUAL ACCESSORIES IN EVERY SCENE" in fem_dir

    # Test Duet Pose Directive
    duet_dir = build_environmental_pose_directive(gender="duet", theme="Lake Romance", num_scenes=4)
    assert "AUTONOMOUS DUET INTERACTION & CHEMISTRY DERIVATION (NO HARDCODED TEMPLATES)" in duet_dir
    assert "STRICT BAN ON OFF-SCREEN REACHING & DISEMBODIED HANDS" in duet_dir
    assert "UNIVERSAL FEMALE COMPOSITION & ACCESSORIES" in duet_dir

    # Test Offline Mock Poses
    offline_scenes = get_offline_dynamic_scene_poses(
        country="Switzerland", culture="Indian", character_desc="Anya", gender="female", num_scenes=3
    )
    assert len(offline_scenes) == 3

    # Test VocalStrategy prompt injection
    strat = VocalStrategy()
    prompt = strat.build_gemini_prompt(
        title="Hawaaon Ke Sang", duration_seconds=180, language="hi", gender="female", theme="Alpine Wildflowers", num_images=3,
    )
    assert "AUTONOMOUS CONTEXT-DRIVEN POSE & FRAMING DIRECTIVE (NO HARDCODED POSES)" in prompt
    assert "UNIVERSAL FEMALE COMPOSITION & ACCESSORIES" in prompt


def test_outfit_and_modesty_standards(sample_cast):
    fem, male = sample_cast
    # Solo female directive
    f_dir, f_neg = build_cast_and_visual_directives(
        slot=1, fem=fem, male=male, culture="Indian", setting="Alpine Meadow", gender="female", is_kids=False,
    )
    assert "BEAUTIFUL, COLORFUL, ELEGANT WITH DESIGNS" in f_dir
    assert "CURATED 4-ZONE ACCESSORIES" in f_dir
    assert "LEGS & ANKLES" in f_dir
    assert "HANDS & WRISTS" in f_dir
    assert "anklet" in f_dir
    assert "STRICT MODESTY" in f_dir
    assert "ZERO NUDITY" in f_dir
    assert "nudity" in f_neg
    assert "cleavage" in f_neg
    assert "sexualized outfit" in f_neg

    # Solo male directive
    m_dir, m_neg = build_cast_and_visual_directives(
        slot=1, fem=fem, male=male, culture="Indian", setting="Alpine Meadow", gender="male", is_kids=False,
    )
    assert "CONTEXT-MATCHING ELEGANT & ATTRACTIVE MALE OUTFIT" in m_dir
    assert "ZERO NUDITY" in m_dir
    assert "nudity" in m_neg
    assert "bare chest" in m_neg

    # Duet directive
    d_dir, d_neg = build_cast_and_visual_directives(
        slot=1, fem=fem, male=male, culture="Indian", setting="Alpine Meadow", gender="duet", is_kids=False,
    )
    assert "Context-Matching & Attractive" in d_dir
    assert "CURATED 4-ZONE ACCESSORIES" in d_dir
    assert "anklet" in d_dir
    assert "ZERO NUDITY" in d_dir
    assert "nudity" in d_neg


