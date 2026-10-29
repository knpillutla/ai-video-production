"""Helper utilities for Documentary and Science Studio Dispatch."""
from __future__ import annotations

from typing import Optional, Tuple
from src.studios.documentary_studio.doc_templates import DocGenre

DOC_GENRE_MAP = {
    "places": DocGenre.PLACES, "doc_places": DocGenre.PLACES,
    "beaches": DocGenre.BEACHES, "doc_beaches": DocGenre.BEACHES,
    "mountains": DocGenre.MOUNTAINS, "doc_mountains": DocGenre.MOUNTAINS,
    "nature": DocGenre.NATURE, "doc_nature": DocGenre.NATURE,
    "ocean": DocGenre.OCEAN, "doc_ocean": DocGenre.OCEAN,
    "desert": DocGenre.DESERT, "doc_desert": DocGenre.DESERT,
    "wildlife": DocGenre.WILDLIFE, "doc_wildlife": DocGenre.WILDLIFE,
    "art": DocGenre.ART, "doc_art": DocGenre.ART,
    "ancient_structures": DocGenre.ANCIENT_STRUCTURES,
    "doc_architecture": DocGenre.ANCIENT_STRUCTURES,
    "architecture_design_tour": DocGenre.ANCIENT_STRUCTURES,
    "ancient_civilizations_history": DocGenre.ANCIENT_STRUCTURES,
    "heritage_history_tour": DocGenre.ANCIENT_STRUCTURES,
    "open_topic_documentary": DocGenre.PLACES,
    "blue_chip_doc": DocGenre.PLACES,
    "itinerary_map_tour": DocGenre.PLACES,
    "grand_tour": DocGenre.PLACES,
    "top_attractions_tour": DocGenre.PLACES,
    "local_neighborhood_tour": DocGenre.PLACES,
    "culinary_food_tour": DocGenre.PLACES,
    "travel_itinerary_tour": DocGenre.PLACES,
    "science": DocGenre.SCIENCE, "science_discovery": DocGenre.SCIENCE,
    "doc_science": DocGenre.SCIENCE, "human_evolution": DocGenre.SCIENCE,
    "science_evolution": DocGenre.SCIENCE, "science_earth": DocGenre.SCIENCE,
    "science_medicine": DocGenre.SCIENCE, "science_space": DocGenre.SCIENCE,
    "science_physics": DocGenre.SCIENCE, "science_tech": DocGenre.SCIENCE,
    "doc/nations": DocGenre.PLACES, "doc_nations": DocGenre.PLACES,
    "nations": DocGenre.PLACES, "europe_nations": DocGenre.PLACES,
    "asia_nations": DocGenre.PLACES, "africa_nations": DocGenre.PLACES,
    "americas_nations": DocGenre.PLACES, "oceania_nations": DocGenre.PLACES,
    "nordic_polar_nations": DocGenre.PLACES,
    "doc/civilizations": DocGenre.ANCIENT_STRUCTURES, "doc_civilizations": DocGenre.ANCIENT_STRUCTURES,
    "civilizations": DocGenre.ANCIENT_STRUCTURES, "civilization": DocGenre.ANCIENT_STRUCTURES,
    "indus_vedic": DocGenre.ANCIENT_STRUCTURES, "celtic_world": DocGenre.ANCIENT_STRUCTURES,
    "viking_norse": DocGenre.ANCIENT_STRUCTURES, "greco_roman": DocGenre.ANCIENT_STRUCTURES,
    "silk_road": DocGenre.ANCIENT_STRUCTURES, "islamic_golden_age": DocGenre.ANCIENT_STRUCTURES,
    "mesoamerican_andean": DocGenre.ANCIENT_STRUCTURES, "east_asian_dynasties": DocGenre.ANCIENT_STRUCTURES,
    "mesopotamian_persian": DocGenre.ANCIENT_STRUCTURES, "byzantine_empire": DocGenre.ANCIENT_STRUCTURES,
    "civilizational_origins": DocGenre.ANCIENT_STRUCTURES, "maritime_expansion_voyages": DocGenre.ANCIENT_STRUCTURES,
}

DEFAULT_DOC_THEMES = {
    "indus_vedic": "Indus Valley Civilization: Harappa, Mohenjo-daro & Ancient Urban Planning",
    "celtic_world": "The Celtic World: Ancient Gaels, Druids & Atlantic Citadels",
    "viking_norse": "Viking Seafarers: Longships, Norse Sagas & Atlantic Voyages",
    "greco_roman": "Classical Antiquity: Mediterranean Empires, Philosophy & Forum Geometry",
    "silk_road": "The Silk Road: Caravans, Oasis Metropolises & Trans-Eurasian Commerce",
    "ancient_civilizations_history": "Ancient Civilizations: Lost Metropolises & Monumental World History",
    "giza_megalithic_pyramids": "Ancient Giza: Megalithic Engineering & The Great Pyramids",
    "scotland_highlands_isles": "Scottish Highlands: Ancient Castles & Mist-Veiled Isles",
    "swiss_alps_valleys": "Swiss Alps: Majestic Glaciers & Granite Titans",
    "iceland_volcanic_coasts": "Iceland: Land of Fire & Glacial Ice",
    "pacific_northwest_redwoods": "Olympic Rainforest & Ancient Redwood Giants",
    "serengeti_savannah_predators": "Serengeti: Untamed Predators & The Great Migration",
    "whitehaven_barrier_reef": "Great Barrier Reef & Whitehaven Beach",
    "amalfi_cliffside_mediterranean": "Amalfi Coast: Azure Cliffs",
    "sahara_dunes_canyons": "Sahara: Monumental Star Dunes",
    "open_topic_documentary": "Wonders of the World: Architectural & Natural Marvels",
    "deep_space_webb": "Cosmic Dawn: James Webb Deep Field",
    "black_holes_gravity": "Event Horizon: Black Hole Singularities",
    "solar_system_moons": "Subsurface Oceans: Europa & Enceladus",
    "exoplanets_alien_worlds": "Exoplanets & Habitable Goldilocks Zone",
    "deep_ocean_abyss": "The Hadal Zone: Mariana Trench",
    "plate_tectonics_volcano": "Mantle Plumes & Supervolcano Calderas",
    "paleontology_fossil_epochs": "Deep Time & The Cambrian Explosion",
    "extreme_meteorology": "Atmospheric Supercells & Jet Streams",
    "neuroscience_brain_connectome": "The Human Connectome: Synaptic Mind",
    "cellular_microbiology": "Nanomachines of Life: Mitosis",
    "genetics_crispr_dna": "The Genetic Code: CRISPR Precision",
    "immunology_body_defense": "The Immune Fortress: T-Cell Defense",
    "quantum_superposition": "Quantum Superposition, Entanglement & Wave-Particle Duality",
    "particle_accelerator_cern": "Inside CERN: Hadron Collider Collisions & The Higgs Boson",
    "atomic_lattice_microscopy": "Imaging the Atom: Scanning Tunneling Microscopy & Lattices",
    "thermodynamics_entropy": "The Arrow of Time: Entropy, Heat Death & Absolute Zero",
    "fusion_energy_tokamak": "Harnessing Star Power: Tokamak Magnetic Confinement Fusion",
    "quantum_computing": "Quantum Supremacy: Dilution Cryostats & Superconducting Qubits",
    "deep_space_propulsion": "Interstellar Propulsion: Ion Thrusters & Relativistic Sails",
    "megastructures_future": "Megastructures: Orbital Rings, Dyson Swarms & Future Engineering",
    "hominin_origins_rift_valley": "Rift Valley Hominins: Australopithecus & Dawn of Bipedalism",
    "ice_age_neanderthals": "Ice Age Neanderthals & Denisovans: Mammoth Hunters",
    "mastery_of_fire_stone_tools": "The Fire Revolution: Acheulean Flint Knapping",
    "cognitive_revolution_cave_art": "The Cognitive Dawn: Lascaux Ochre Murals",
}

GENRE_FALLBACKS = {
    DocGenre.ANCIENT_STRUCTURES: "Ancient Civilizations: Lost Metropolises & World History Architecture",
    DocGenre.WILDLIFE: "Untamed Majesty: Predators of the Serengeti",
    DocGenre.OCEAN: "Abyssal Realms: Secrets of the Deep Coral Sea",
    DocGenre.NATURE: "Ancient Canopies: Whispers of the Temperate Rainforest",
    DocGenre.MOUNTAINS: "Granite Sanctuaries: Titans of the Swiss Alps",
    DocGenre.ART: "The Master's Touch: Secrets of Renaissance Frescoes",
    DocGenre.BEACHES: "Untamed Shorelines: Coastal Wonders of the World",
    DocGenre.DESERT: "Silent Dunes: Mysteries of the Living Sands",
    DocGenre.PLACES: "Earth's Geographic Sanctuaries: Wonders of the World",
    DocGenre.SCIENCE: "Cosmic Frontiers: The Architecture of Reality & Deep Space",
}


def resolve_doc_dispatch_params(
    sub_lower: str,
    arch_lower: str,
    is_science: bool,
    primary_archetype: Optional[str] = None,
    sub_genre: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
) -> Tuple[DocGenre, str, str]:
    """Resolve documentary genre enum, effective archetype name, and theme seed."""
    from src.studios.documentary_studio.doc_geo_rotation import (
        is_geo_continent_subgenre,
        resolve_autonomous_geo_theme,
        ARCHETYPE_TEMPLATES,
    )

    eff_sub = (sub_genre or sub_lower or "").strip().lower()
    eff_arch = (primary_archetype or arch_lower or "").strip().lower()

    if (
        is_geo_continent_subgenre(eff_sub)
        or eff_arch in ARCHETYPE_TEMPLATES
        or "nations" in eff_sub
        or "nations" in eff_arch
    ):
        return resolve_autonomous_geo_theme(
            sub_genre=eff_sub,
            archetype=eff_arch,
            user_id=user_id,
            channel_id=channel_id,
            custom_prompt=custom_prompt,
        )

    eff_doc_genre = DOC_GENRE_MAP.get(
        sub_lower,
        DOC_GENRE_MAP.get(arch_lower, DocGenre.SCIENCE if is_science else DocGenre.PLACES)
    )
    eff_archetype_name = (
        primary_archetype or sub_genre or arch_lower or sub_lower or
        ("deep_space_webb" if is_science else "open_topic_documentary")
    )
    theme_seed = (
        custom_prompt or
        DEFAULT_DOC_THEMES.get(eff_archetype_name.lower()) or
        GENRE_FALLBACKS.get(eff_doc_genre, "Cosmic Frontiers: Deep Space & Science")
    )
    return eff_doc_genre, eff_archetype_name, theme_seed
