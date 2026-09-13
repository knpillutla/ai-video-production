"""Costume, Jewelry, and Traditional Attire LoRA Intelligence Catalog."""

from typing import Any

COSTUME_INTELLIGENCE_CATALOG: dict[str, dict[str, Any]] = {
    "indian_traditional_saree": {
        "display_name": "Kanchipuram Silk Saree & Temple Jewelry",
        "target_gender": "female",
        "recommended_lora": {
            "path": "loras/kanchipuram_silk_saree_v2.safetensors",
            "scale": 0.85,
            "trigger": "kanchipuram silk saree, gold zari brocade",
        },
        "jewelry_lora": {
            "path": "loras/temple_jewelry_gold_v1.safetensors",
            "scale": 0.80,
            "trigger": "antique gold temple jewelry, jhumkas, neck choker",
        },
        "prompt_enhancer": (
            "wearing an opulent handwoven Kanchipuram silk saree with intricate pure gold zari brocade, "
            "contrasting temple borders, layered antique gold temple jewelry, jhumkas, waist belt, jasmine garland in braided hair"
        ),
    },
    "indian_traditional_dhoti": {
        "display_name": "Traditional Silk Dhoti-Pancha & Angavastram",
        "target_gender": "male",
        "recommended_lora": {
            "path": "loras/indian_mens_dhoti_v1.safetensors",
            "scale": 0.85,
            "trigger": "silk dhoti pancha, gold zari border",
        },
        "prompt_enhancer": (
            "wearing an authentic off-white raw silk dhoti-pancha with thick gold zari border, "
            "matching silk angavastram draped over shoulder, traditional gold chain, neat sandalwood tilak on forehead"
        ),
    },
    "indian_royal_sherwani": {
        "display_name": "Royal Embroidered Sherwani & Turban",
        "target_gender": "male",
        "recommended_lora": {
            "path": "loras/royal_sherwani_zardozi_v1.safetensors",
            "scale": 0.90,
            "trigger": "embroidered zardozi royal sherwani, velvet stole",
        },
        "prompt_enhancer": (
            "wearing a regal ivory and gold zardozi hand-embroidered sherwani, rich velvet shawl with gold fringe, "
            "jeweled kalgi brooch on silk turban (pagdi), heritage pearl necklace"
        ),
    },
    "telugu_mass_festive": {
        "display_name": "Telugu Mass Song & Jathara Folk Attire",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/telugu_mass_festive_v1.safetensors",
            "scale": 0.85,
            "trigger": "telugu mass dance attire, mirror-work festive lehenga, rustic patterned shirt, zari lungi",
        },
        "jewelry_lora": {
            "path": "loras/indian_oxidized_silver_jewelry_v1.safetensors",
            "scale": 0.80,
            "trigger": "oxidized silver necklace, ethnic glass bangles, maang tikka",
        },
        "jewelry_anchor": "oxidized silver ethnic necklace, sparkling glass bangles, waist belt",
        "prompt_enhancer": (
            "wearing high-energy Telugu cinema mass folk dance attire, vibrant multi-colored mirror-work flared lehenga choli "
            "with intricate embroidery and sleeveless choli for female, or rustic patterned festival shirt with rolled-up sleeves, "
            "man-bun, sweat glisten, and zari-border lungi for male, dancing in an electric village jathara festival atmosphere"
        ),
    },
    "telugu_rain_folk_saree": {
        "display_name": "Telugu Village Monsoon Rain Folk Saree & Dhoti",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/telugu_rain_folk_v1.safetensors",
            "scale": 0.85,
            "trigger": "wet cotton saree tucked at waist, dark green blouse, wet hair strands, rain droplets",
        },
        "jewelry_lora": {
            "path": "loras/indian_silver_bell_jhumkas_v1.safetensors",
            "scale": 0.80,
            "trigger": "traditional silver bell jhumkas, red and green glass bangles, small black bindi",
        },
        "jewelry_anchor": "traditional silver bell jhumkas, glass bangles on forearms, small black bindi",
        "prompt_enhancer": (
            "wearing authentic Telugu village monsoon rain folk dance attire: dark forest-green short-sleeve choli blouse, "
            "rustic cream and gold striped handloom cotton saree tucked high at the waist (kattu) for dancing in water, "
            "clinging damp cotton fabric, glistening rain droplets rolling down warm dusky skin, wet dark hair framing face, "
            "traditional silver bell jhumkas, bare feet in damp fertile soil"
        ),
    },
    "western_modern": {
        "display_name": "Modern Smart Casual",
        "target_gender": "unisex",
        "prompt_enhancer": "wearing stylish contemporary fitted attire, clean tailoring, modern aesthetic",
    },
    "italian_tarantella_folk": {
        "display_name": "Traditional Italian Tarantella Folk Costume",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/italian_tarantella_costume_v1.safetensors",
            "scale": 0.85,
            "trigger": "traditional italian folk dress, laced bodice, embroidered apron, tambourine",
        },
        "prompt_enhancer": (
            "wearing authentic Southern Italian folk attire, flared pleated skirt with colorful ribbons, "
            "crisp white lace peasant blouse, laced black velvet bodice (corpetto), embroidered floral apron, carrying a festive tambourine"
        ),
    },
    "mexican_jalisco_charro": {
        "display_name": "Mexican Ballet Folklórico Jalisco Dress & Charro Suit",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/mexican_folklore_jalisco_v1.safetensors",
            "scale": 0.85,
            "trigger": "jalisco ribbon dress, embroidered charro suit, wide sombrero",
        },
        "prompt_enhancer": (
            "wearing authentic Mexican Ballet Folklórico Jalisco attire, grand tiered circular skirt with vivid rainbow satin ribbons, "
            "high-collar ruffled lace blouse, braided hair adorned with matching ribbons and silver earrings"
        ),
    },
    "american_western_country": {
        "display_name": "American Western Country & Line Dance Attire",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/american_western_country_v1.safetensors",
            "scale": 0.85,
            "trigger": "cowboy boots, denim jeans, western snap shirt, stetson cowboy hat",
        },
        "prompt_enhancer": (
            "wearing authentic American Western country dance attire, tailored pearl-snap western shirt, dark denim jeans, "
            "tooled leather belt with large engraved silver buckle, handcrafted leather cowboy boots, Stetson felt cowboy hat"
        ),
    },
    "chinese_hanfu_water_sleeves": {
        "display_name": "Traditional Chinese Hanfu & Water Sleeves (Shuixiu)",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/chinese_classical_hanfu_dance_v1.safetensors",
            "scale": 0.85,
            "trigger": "flowing water sleeves shuixiu, celestial hanfu silk robes, long silk ribbons",
        },
        "prompt_enhancer": (
            "wearing ethereal celestial Chinese Hanfu silk robes, dramatic flowing white silk water sleeves (shuixiu) extending past hands, "
            "delicate jade hairpins, floating celestial silk ribbons, exquisite lotus embroidery"
        ),
    },
    "ancient_egyptian_exotic": {
        "display_name": "Ancient Egyptian Royal Linen & Gold Hieroglyphic Attire",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/ancient_egyptian_royal_v1.safetensors",
            "scale": 0.85,
            "trigger": "ancient egyptian royal linen dress, gold hieroglyphic embroidery, kohl eyeliner, gold diadem",
        },
        "jewelry_lora": {
            "path": "loras/ancient_egyptian_gold_jewelry_v1.safetensors",
            "scale": 0.80,
            "trigger": "gold wesekh broad collar, turquoise lapis lazuli necklace, gold arm cuffs, snake armband",
        },
        "jewelry_anchor": "gold diadem headdress, broad wesekh gold collar necklace, engraved gold arm cuffs",
        "prompt_enhancer": (
            "wearing authentic ancient Egyptian royal attire, pleated fine linen dress with gilded gold "
            "hieroglyphic embroidery and gold trim, gold diadem headdress across long wavy dark hair, dramatic dark kohl smokey eyeliner, "
            "broad gold wesekh collar adorned with lapis lazuli and turquoise, standing in an ancient candlelit sandstone temple tomb"
        ),
    },
    "american_hiphop_streetwear": {
        "display_name": "American Hip-Hop & Urban Streetwear",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/american_hiphop_streetwear_v1.safetensors",
            "scale": 0.85,
            "trigger": "oversized designer hoodie, layered cuban link chains, distressed cargo pants, retro high-top sneakers",
        },
        "jewelry_lora": {
            "path": "loras/cuban_link_gold_chains_v1.safetensors",
            "scale": 0.80,
            "trigger": "heavy gold cuban link necklace, iced out watch, diamond stud earrings",
        },
        "jewelry_anchor": "heavy layered 18K gold Cuban link chains, diamond stud earrings, iced-out luxury watch",
        "prompt_enhancer": (
            "wearing luxury American hip-hop streetwear, oversized graphic designer hoodie, heavy layered 18K gold Cuban link chains, "
            "distressed tactical cargo pants, limited edition high-top retro basketball sneakers, diamond studs, fitted cap"
        ),
    },
    "american_rock_leather": {
        "display_name": "American Rock & Alternative Leather Attire",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/american_rock_leather_v1.safetensors",
            "scale": 0.85,
            "trigger": "black leather motorcycle jacket, band t-shirt, ripped skinny jeans, combat boots",
        },
        "prompt_enhancer": (
            "wearing vintage American rock music attire, distressed black leather motorcycle jacket with silver zippers and studs, "
            "graphic rock band t-shirt, ripped black denim jeans, studded leather belt, scuffed leather combat boots"
        ),
    },
    "american_pop_glam": {
        "display_name": "American Pop Star Futuristic Stage Glamour",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/american_popstar_glam_v1.safetensors",
            "scale": 0.85,
            "trigger": "metallic stage outfit, glitter sequins, avant-garde pop star styling",
        },
        "prompt_enhancer": (
            "wearing high-fashion American pop star stage costume, iridescent holographic metallic cropped jacket, "
            "sequined silver accents, futuristic reflective sunglasses, sleek tailored joggers, platform designer sneakers"
        ),
    },
    "american_rnb_velvet": {
        "display_name": "American R&B & Neo-Soul Luxury Velvet",
        "target_gender": "unisex",
        "recommended_lora": {
            "path": "loras/american_rnb_velvet_v1.safetensors",
            "scale": 0.85,
            "trigger": "tailored velvet blazer, silk button-down shirt, gold dress watch",
        },
        "prompt_enhancer": (
            "wearing smooth American R&B music video attire, tailored burgundy velvet blazer with satin lapels, "
            "black silk open-collar shirt, tailored slim dress trousers, polished Italian dress shoes, minimalist gold pendant"
        ),
    },
}


def lookup_costume_stack(costume_style: str | None = None, gender: str = "female") -> dict[str, Any]:
    """Retrieve costume prompt anchors, fabrics, and recommended LoRAs."""
    c_key = (costume_style or "western_modern").lower().replace("-", "_")
    if "hip_hop" in c_key or "rap" in c_key or "trap" in c_key or "streetwear" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["american_hiphop_streetwear"]
    if "rock" in c_key or "metal" in c_key or "punk" in c_key or "grunge" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["american_rock_leather"]
    if "pop" in c_key or "glam" in c_key or "electronic" in c_key or "edm" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["american_pop_glam"]
    if "rnb" in c_key or "r&b" in c_key or "soul" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["american_rnb_velvet"]
    if "ital" in c_key or "tarantella" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["italian_tarantella_folk"]
    if "mexic" in c_key or "jalisco" in c_key or "charro" in c_key or "folklore" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["mexican_jalisco_charro"]
    if "americ" in c_key or "western" in c_key or "cowboy" in c_key or "country" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["american_western_country"]
    if "chin" in c_key or "hanfu" in c_key or "water_sleeve" in c_key or "shuixiu" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["chinese_hanfu_water_sleeves"]
    if "egypt" in c_key or "pharaoh" in c_key or "hieroglyph" in c_key or "cleopatra" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["ancient_egyptian_exotic"]
    if "royal" in c_key or "sherwani" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["indian_royal_sherwani"]
    if "dhoti" in c_key or "pancha" in c_key or ("trad" in c_key and gender.lower() == "male"):
        return COSTUME_INTELLIGENCE_CATALOG["indian_traditional_dhoti"]
    if "rain" in c_key or "monsoon" in c_key or "vanammo" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["telugu_rain_folk_saree"]
    if "mass" in c_key or "jathara" in c_key or "teenmaar" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["telugu_mass_festive"]
    if "saree" in c_key or "traditional" in c_key:
        return COSTUME_INTELLIGENCE_CATALOG["indian_traditional_saree"]
    return COSTUME_INTELLIGENCE_CATALOG["western_modern"]


__all__ = ["COSTUME_INTELLIGENCE_CATALOG", "lookup_costume_stack"]
