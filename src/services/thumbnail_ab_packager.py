"""3-Variant A/B/C Thumbnail Prompt & Packaging Generator for YouTube Test & Compare."""

from typing import Dict, List
from pydantic import BaseModel


class ThumbnailVariant(BaseModel):
    """Specification for an A/B test thumbnail variant."""
    variant_id: str  # variant_a, variant_b, variant_c
    name: str
    description: str
    prompt: str


class ThumbnailABPackage(BaseModel):
    """Complete 3-variant thumbnail pack for YouTube A/B optimization."""
    archetype_key: str
    variants: List[ThumbnailVariant]


def generate_thumbnail_ab_variants(archetype_key: str) -> ThumbnailABPackage:
    """Generate 3 psychologically distinct thumbnail prompts for YouTube Test & Compare."""
    clean_key = archetype_key.lower().replace("-", "_").replace(" ", "_")
    name = archetype_key.replace("_", " ").title()

    # Variant A: Cozy First-Person Interior POV
    var_a = ThumbnailVariant(
        variant_id="variant_a_interior_pov",
        name="Cozy First-Person Interior POV",
        description="Steaming ceramic tea mug on rustic wooden table, rain/frost on window, warm amber interior lamp.",
        prompt=(
            f"Masterpiece 4K YouTube thumbnail photograph. First-person point of view inside a cozy timber room looking out at {name}. "
            "A rustic wooden table in foreground with a steaming ceramic coffee mug and open book, delicate rain droplets on the window glass. "
            "Warm glowing golden amber lamp inside contrasting against the dramatic cool blue atmosphere outside, 35mm f/1.4 lens, 8k, zero text."
        ),
    )

    # Variant B: Expansive Sanctuary Vista
    var_b = ThumbnailVariant(
        variant_id="variant_b_wide_sanctuary",
        name="Expansive Majestic Sanctuary Vista",
        description="Monumental scale landscape with solitary warm glowing cabin.",
        prompt=(
            f"Masterpiece 4K YouTube thumbnail landscape photograph of majestic {name}. "
            "Sweeping monumental mountain peaks and misty clouds, an enchanting solitary wooden chalet nestled in the landscape with warm yellow lights glowing from windows. "
            "Striking complementary color contrast (deep indigo twilight sky vs warm golden window glow), award-winning NatGeo cinematography, 8k, zero text."
        ),
    )

    # Variant C: Intimate Hearth & Macro Detail
    var_c = ThumbnailVariant(
        variant_id="variant_c_hearth_detail",
        name="Warm Hearth & Macro Comfort Detail",
        description="Glowing orange embers, knitted blanket, warm fireplace, soft blurred landscape.",
        prompt=(
            f"Masterpiece 4K YouTube thumbnail photograph focusing on a warm glowing stone fireplace with crackling orange embers. "
            f"A chunky knit wool blanket draped over an armchair, large bay window in background showing soft blurred misty {name} outside. "
            "Intimate, peaceful, ultimate cozy feeling, deep depth of field, 8k resolution, zero text."
        ),
    )

    return ThumbnailABPackage(
        archetype_key=clean_key,
        variants=[var_a, var_b, var_c],
    )
