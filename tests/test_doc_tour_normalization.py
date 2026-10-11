import asyncio
from src.studios.documentary_studio.doc_storyboard import DocGenre
from src.studios.documentary_studio.doc_tour_normalizer import normalize_tour_scenes
from src.studios.ambient_world.relax_models import RelaxScreenplay, RelaxSceneDirective

mock_raw_scenes = [
    {
        "scene_index": 1,
        "visual_prompt": "Cinematography of the Palace of Westminster and Big Ben",
        "narration_text": "Begin exploring Westminster Abbey",
    },
    {
        "scene_index": 2,
        "visual_prompt": "St Paul's Cathedral rising behind Millennium Bridge",
        "narration_text": "Stroll along the Thames to St Paul's Cathedral",
    },
    {
        "scene_index": 3,
        "visual_prompt": "Historic Borough Market with green iron trusses",
        "narration_text": "Pause at Borough Market for gourmet cuisine",
    },
    {
        "scene_index": 4,
        "visual_prompt": "Tower of London fortress beside Tower Bridge",
        "narration_text": "Uncover secrets within Tower of London",
    },
    {
        "scene_index": 5,
        "visual_prompt": "Sunset view overlooking London skyline",
        "narration_text": "Conclude your circuit by six o'clock",
    }
]

norm_scenes, summary = normalize_tour_scenes(mock_raw_scenes, "London 1 Day Tour")
print("Normalized scenes count:", len(norm_scenes))
for sc in norm_scenes:
    print(f"Stop {sc['scene_index']}: {sc['origin_name']} | Coords: {sc['origin_coords']} | Time: {sc['start_time']} - {sc['end_time']} ({sc['visit_duration']})")
print("Summary attractions:", summary[0]["attractions"])

# Test RelaxScreenplay serialization
relax_scenes = [
    RelaxSceneDirective(
        scene_index=s["scene_index"],
        visual_prompt=s["visual_prompt"],
        motion_prompt="slow push",
        narration_text=s["narration_text"],
        day_number=s["day_number"],
        start_time=s["start_time"],
        end_time=s["end_time"],
        visit_duration=s["visit_duration"],
        transit_duration=s["transit_duration"],
        origin_name=s["origin_name"],
        origin_coords=s["origin_coords"],
    )
    for s in norm_scenes
]
sp = RelaxScreenplay(
    title="London Tour",
    scenes=relax_scenes,
    itinerary_summary=summary,
)
dump = sp.model_dump()
print("Serialized origin_name in scene 1:", dump["scenes"][0]["origin_name"])
print("Serialized origin_coords in scene 1:", dump["scenes"][0]["origin_coords"])
print("Serialized start_time in scene 1:", dump["scenes"][0]["start_time"])
print("Serialized itinerary_summary day 1 attractions:", dump["itinerary_summary"][0]["attractions"])
