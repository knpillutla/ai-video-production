"""Test Suite for Cultural Derivation, Character Consistency, and Gender-Matched Audio."""

import pytest
from uuid import uuid4
from src.domain.repo import repo
from src.domain.user import User
from src.mcp.model_selector.cultural_catalog import (
    lookup_costume_stack,
    lookup_cultural_stack,
    lookup_dance_stack,
    resolve_cultural_voice,
)
from src.services.character_consistency import (
    build_character_prompt_prefix,
    get_or_create_character_anchor,
    inject_character_consistency,
)
from src.services.cultural_derivation import derive_cultural_context


def test_gender_matched_regional_voices():
    """Verify gender-matched neural voices for Telugu, Australian, Italian, Mexican, and Indian English."""
    # Telugu
    assert resolve_cultural_voice("indian_south", "te", gender="male") == "te-IN-MohanNeural"
    assert resolve_cultural_voice("indian_south", "te", gender="female") == "te-IN-ShrutiNeural"

    # Australian
    assert resolve_cultural_voice("australian", "en", gender="male") == "en-AU-WilliamNeural"
    assert resolve_cultural_voice("australian", "en", gender="female") == "en-AU-NatashaNeural"

    # Italian
    assert resolve_cultural_voice("italian", "it", gender="male") == "it-IT-DiegoNeural"
    assert resolve_cultural_voice("italian", "it", gender="female") == "it-IT-ElsaNeural"

    # Mexican
    assert resolve_cultural_voice("mexican", "es", gender="male") == "es-MX-JorgeNeural"
    assert resolve_cultural_voice("mexican", "es", gender="female") == "es-MX-DaliaNeural"

    # Indian English
    assert resolve_cultural_voice("indian_north", "en", gender="male") == "en-IN-PrabhatNeural"
    assert resolve_cultural_voice("indian_north", "en", gender="female") == "en-IN-NeerjaNeural"


def test_dance_and_traditional_costume_stacks():
    """Verify dance models, authentic clothing, jewelry, and LoRAs for international dances."""
    # Italian Tarantella
    dance_it = lookup_dance_stack("italian_tarantella")
    assert "tarantella" in dance_it["dance_name"].lower()
    assert dance_it["motion_model"] == "fal-mimic-motion"
    assert "accordion" in dance_it["music_style"].lower()
    costume_it = lookup_costume_stack("italian_tarantella_folk", gender="female")
    assert "corset" in costume_it["prompt_enhancer"].lower() or "bodice" in costume_it["prompt_enhancer"].lower()
    assert costume_it["recommended_lora"]["path"] == "loras/italian_tarantella_costume_v1.safetensors"

    # Mexican Folklórico / Jarabe Tapatío
    dance_mx = lookup_dance_stack("mexican_folklore")
    assert "zapateado" in dance_mx["prompt_decorations"].lower() or "jalisco" in dance_mx["dance_name"].lower()
    costume_mx = lookup_costume_stack("mexican_jalisco_charro", gender="female")
    assert "ribbon" in costume_mx["prompt_enhancer"].lower()
    assert costume_mx["recommended_lora"]["path"] == "loras/mexican_folklore_jalisco_v1.safetensors"

    # Indian Classical (Bharatanatyam / Kuchipudi)
    dance_in = lookup_dance_stack("indian_classical")
    assert "mudra" in dance_in["prompt_decorations"].lower()
    costume_in = lookup_costume_stack("indian_traditional_saree", gender="female")
    assert "kanchipuram" in costume_in["prompt_enhancer"].lower()
    assert costume_in["jewelry_lora"]["path"] == "loras/temple_jewelry_gold_v1.safetensors"

    # Chinese Hanfu Water Sleeves
    dance_cn = lookup_dance_stack("chinese_water_sleeves")
    assert "shuixiu" in dance_cn["prompt_decorations"].lower()
    costume_cn = lookup_costume_stack("chinese_hanfu_water_sleeves", gender="female")
    assert "hanfu" in costume_cn["prompt_enhancer"].lower()


def test_music_video_costume_and_jewelry_by_genre():
    """Verify genre-specific clothing and jewelry adaptations for American music videos."""
    # Hip-Hop: Streetwear and Cuban link chains
    hiphop_ctx = derive_cultural_context(
        script_text="High-energy trap music video with heavy 808 bass in Brooklyn",
        video_format="music_video",
        genre="hip_hop",
        gender="male",
    )
    assert hiphop_ctx.clothing_style == "american_hiphop_streetwear"
    assert "cuban link" in hiphop_ctx.jewelry_description.lower()
    assert any("cuban_link" in l.get("path", "") for l in hiphop_ctx.recommended_loras)

    # Country / Western: Stetson, snap shirt, cowboy boots
    country_ctx = derive_cultural_context(
        script_text="Nashville acoustic country song video",
        video_format="music_video",
        genre="country",
        gender="male",
    )
    assert country_ctx.clothing_style == "american_western_country"
    assert "cowboy" in country_ctx.outfit_description.lower() or "stetson" in country_ctx.outfit_description.lower()

    # Rock: Leather jacket, studs, combat boots
    rock_ctx = derive_cultural_context(
        script_text="Electric guitar solo rock concert video",
        video_format="music_video",
        genre="rock",
        gender="female",
    )
    assert rock_ctx.clothing_style == "american_rock_leather"
    assert "leather" in rock_ctx.outfit_description.lower()


def test_cultural_derivation_from_user_home_country():
    """Verify user home country derives culture, regional neural voice, and music."""
    # Australia
    au_ctx = derive_cultural_context(user_home_country="AU", language="en", gender="male")
    assert au_ctx.culture == "australian"
    assert au_ctx.voice_id == "en-AU-WilliamNeural"
    assert "aussie" in au_ctx.music_style.lower() or "australian" in au_ctx.music_style.lower()

    # Italy
    it_ctx = derive_cultural_context(user_home_country="IT", language="it", gender="female")
    assert it_ctx.culture == "italian"
    assert it_ctx.voice_id == "it-IT-ElsaNeural"

    # Mexico
    mx_ctx = derive_cultural_context(user_home_country="MX", language="es", gender="male")
    assert mx_ctx.culture == "mexican"
    assert mx_ctx.voice_id == "es-MX-JorgeNeural"

    # India
    in_ctx = derive_cultural_context(user_home_country="IN", language="te", gender="female")
    assert in_ctx.culture == "indian_south"
    assert in_ctx.voice_id == "te-IN-ShrutiNeural"


def test_cultural_derivation_from_script_keywords():
    """Verify script keywords deterministically guide regional culture and costumes."""
    # Hyderabad Charminar -> South Indian culture and saree
    hyd_ctx = derive_cultural_context(script_text="Visiting Charminar and enjoying biryani in Hyderabad")
    assert hyd_ctx.culture == "indian_south"
    assert "South Asian" in hyd_ctx.primary_ethnicity
    assert hyd_ctx.clothing_style == "indian_traditional_saree"

    # Rome Tarantella -> Italian
    rome_ctx = derive_cultural_context(script_text="Folk festival in Rome with traditional pizzica dancers")
    assert rome_ctx.culture == "italian"
    assert rome_ctx.clothing_style == "italian_tarantella_folk"


def test_character_consistency_anchor_and_seed_locking():
    """Verify character consistency engine creates and locks visual anchor, seed, and LoRAs."""
    repo.clear()
    uid = uuid4()
    sid = uuid4()

    # Create character anchor for Telugu protagonist Ananya
    anchor1 = get_or_create_character_anchor(
        user_id=uid, show_id=sid, character_name="Ananya",
        culture="indian_south", costume_style="indian_traditional_saree", gender="female",
    )
    assert anchor1.name == "Ananya"
    assert anchor1.gender == "female"
    assert anchor1.seed >= 42819
    assert len(anchor1.loras) >= 2  # saree LoRA + temple jewelry LoRA

    # Verify second retrieval returns identical seed and anchor
    anchor2 = get_or_create_character_anchor(
        user_id=uid, show_id=sid, character_name="Ananya",
        culture="indian_south", costume_style="indian_traditional_saree", gender="female",
    )
    assert anchor2.character_id == anchor1.character_id
    assert anchor2.seed == anchor1.seed
    assert anchor2.appearance_anchor == anchor1.appearance_anchor

    # Verify prompt prefix and LoRA injection
    prompt = "Walking through bustling Hyderabad bazaar"
    enhanced_prompt, loras, seed = inject_character_consistency(prompt, anchor1)
    assert "Protagonist Ananya" in enhanced_prompt
    assert "kanchipuram" in enhanced_prompt.lower() or "saree" in enhanced_prompt.lower()
    assert seed == anchor1.seed
    assert len(loras) == len(anchor1.loras)


def test_telugu_monsoon_rain_dance_and_costume_derivation():
    """Verify Telugu monsoon rain dance and costume resolution."""
    from src.mcp.model_selector.dance_catalog import lookup_dance_stack

    rain_ctx = derive_cultural_context(
        script_text="Olammo Vanammo Telugu village rain dance in monsoon paddy fields",
        video_format="music_video",
        genre="dance",
        gender="female",
        language="te",
    )
    assert rain_ctx.culture == "indian_south"
    assert rain_ctx.clothing_style == "telugu_rain_folk_saree"
    assert "cotton saree" in rain_ctx.outfit_description.lower()
    assert "jhumkas" in rain_ctx.jewelry_description.lower()
    assert rain_ctx.voice_id == "te-IN-ShrutiNeural"

    dance_stack = lookup_dance_stack("telugu_monsoon_rain_dance")
    assert dance_stack is not None
    assert "Monsoon Rain Folk" in dance_stack["dance_name"]
    assert dance_stack["costume_style"] == "telugu_rain_folk_saree"
    assert dance_stack["visual_model"] == "flux-1-dev"

