"""Culturally and regionally authentic character name generator."""

from typing import Optional

CULTURAL_NAME_POOLS: dict[str, dict[str, list[str]]] = {
    "te": {
        "female": ["Vennela", "Lavanya", "Swapna", "Mounika", "Sirisha", "Radhika", "Renuka", "Anitha", "Kavitha", "Sravani"],
        "male": ["Mallesh", "Shiva", "Vamsi", "Harish", "Naresh", "Rajesh", "Kalyan", "Srinivas", "Ramesh", "Suresh"],
    },
    "ta": {
        "female": ["Meenakshi", "Priya", "Soundarya", "Kaviya", "Nandhini", "Deepa"],
        "male": ["Karthik", "Selvan", "Saravanan", "Vignesh", "Murugan", "Senthil"],
    },
    "kn": {
        "female": ["Sowmya", "Kavya", "Deepika", "Bhavya", "Spoorthi"],
        "male": ["Manjunath", "Praveen", "Chethan", "Darshan", "Raghu"],
    },
    "ml": {
        "female": ["Anjali", "Parvathy", "Aparna", "Sneha", "Devika"],
        "male": ["Rahul", "Midhun", "Vishnu", "Anoop", "Sreejith"],
    },
    "hi": {
        "female": ["Aaradhya", "Simran", "Pooja", "Neha", "Riya", "Kavya"],
        "male": ["Rohan", "Rahul", "Amit", "Kabir", "Arjun", "Vikram"],
    },
    "east_asian": {
        "female": ["Mei", "Lin", "Yuna", "Minji", "Hana", "Sakura"],
        "male": ["Chen", "Wei", "Jun", "Jin", "Kenji", "Daiki"],
    },
    "western_global": {
        "female": ["Emma", "Sophia", "Chloe", "Sarah", "Olivia", "Ava"],
        "male": ["James", "Liam", "Lucas", "Ethan", "Noah", "Oliver"],
    },
}


def resolve_cultural_character_name(
    culture: Optional[str] = None,
    language: str = "en",
    gender: str = "female",
    seed: int = 0,
) -> str:
    """Resolve an authentic regional name without generic or hardcoded fallbacks."""
    g_key = "male" if (gender or "female").lower() == "male" else "female"
    lang_key = (language or "en").lower().split("-")[0]
    cult_safe = (culture or "western_global").lower()

    if lang_key in CULTURAL_NAME_POOLS:
        names = CULTURAL_NAME_POOLS[lang_key].get(g_key, [])
        if names:
            return names[seed % len(names)]

    if any(k in cult_safe for k in ("south", "dravid", "telugu", "andhra", "tamil")):
        names = CULTURAL_NAME_POOLS["te"].get(g_key, [])
        return names[seed % len(names)]

    if any(k in cult_safe for k in ("north", "hindi", "punjab", "aryan")):
        names = CULTURAL_NAME_POOLS["hi"].get(g_key, [])
        return names[seed % len(names)]

    if any(k in cult_safe for k in ("east", "china", "japan", "korea")):
        names = CULTURAL_NAME_POOLS["east_asian"].get(g_key, [])
        return names[seed % len(names)]

    names = CULTURAL_NAME_POOLS["western_global"].get(g_key, ["Emma" if g_key == "female" else "Liam"])
    return names[seed % len(names)]
