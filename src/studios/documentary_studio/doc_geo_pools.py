"""Geographic pools, archetypes, and templates for Nations & Civilizations documentary studio."""

from __future__ import annotations

from src.studios.documentary_studio.doc_archetype_templates import (
    ARCHETYPE_TEMPLATES,
    ARCHETYPE_GENRE_MAP,
)

CONTINENT_COUNTRIES_MAP: dict[str, list[str]] = {
    "europe_nations": [
        "Poland", "Czech Republic", "Austria", "Italy", "France", "Spain",
        "Portugal", "Germany", "Greece", "Scotland", "Switzerland", "Norway",
        "Netherlands", "Ireland", "Croatia", "Hungary", "Romania", "Sweden",
        "Denmark", "Belgium", "Finland", "Slovenia", "Estonia", "Slovakia",
    ],
    "asia_nations": [
        "Japan", "India", "Vietnam", "South Korea", "Thailand", "Jordan",
        "Indonesia", "China", "Nepal", "Malaysia", "Oman", "Turkey",
        "Cambodia", "Sri Lanka", "Philippines", "Taiwan", "Uzbekistan",
        "Singapore", "Bhutan", "Laos",
    ],
    "americas_nations": [
        "Peru", "Canada", "Mexico", "Brazil", "Chile", "Colombia",
        "Argentina", "Costa Rica", "United States", "Guatemala", "Ecuador",
        "Bolivia", "Panama", "Uruguay",
    ],
    "africa_nations": [
        "Egypt", "Morocco", "Kenya", "South Africa", "Tanzania", "Namibia",
        "Ethiopia", "Zimbabwe", "Botswana", "Madagascar", "Ghana", "Tunisia",
        "Rwanda", "Uganda",
    ],
    "oceania_nations": [
        "New Zealand", "Australia", "Fiji", "French Polynesia", "Samoa",
        "Papua New Guinea", "Cook Islands", "Vanuatu",
    ],
    "nordic_polar_nations": [
        "Iceland", "Norway", "Greenland", "Svalbard", "Finland",
        "Faroe Islands", "Sweden",
    ],
}

for _k, _v in [
    ("europe_countries", "europe_nations"),
    ("asia_countries", "asia_nations"),
    ("americas_countries", "americas_nations"),
    ("africa_countries", "africa_nations"),
    ("oceania_countries", "oceania_nations"),
    ("nordic_arctic_countries", "nordic_polar_nations"),
]:
    CONTINENT_COUNTRIES_MAP[_k] = CONTINENT_COUNTRIES_MAP[_v]

CONTINENT_CITIES_MAP: dict[str, list[str]] = {
    "europe_nations": [
        "Rome", "Paris", "Vienna", "Prague", "Barcelona", "Florence", "Amsterdam", "Edinburgh", "Krakow", "Seville",
        "Athens", "Munich", "Dubrovnik", "Budapest", "Lisbon", "Venice", "Warsaw", "Salzburg", "Porto", "Bruges", "Copenhagen", "Dublin", "Stockholm", "Madrid", "Berlin",
    ],
    "asia_nations": [
        "Kyoto", "Tokyo", "Varanasi", "Bangkok", "Istanbul", "Seoul", "Singapore", "Chiang Mai", "Jaipur", "Hanoi", "Petra", "Taipei",
        "Luang Prabang", "Samarkand", "Shanghai", "Mumbai", "Ubud", "Kuala Lumpur", "Kathmandu", "Bukhara", "Isfahan", "Beijing", "Ho Chi Minh City",
    ],
    "americas_nations": [
        "Cusco", "Buenos Aires", "Quebec City", "Mexico City", "Rio de Janeiro", "Vancouver", "Cartagena", "San Francisco", "Oaxaca", "Montreal",
        "Santiago", "Boston", "Antigua Guatemala", "New Orleans", "Havana", "Salvador da Bahia", "Medellin", "Toronto",
    ],
    "africa_nations": [
        "Cairo", "Marrakech", "Cape Town", "Zanzibar Stone Town", "Luxor", "Nairobi", "Fez", "Alexandria", "Johannesburg", "Addis Ababa",
        "Essaouira", "Victoria Falls Town", "Kigali", "Windhoek", "Aswan", "Tunis",
    ],
    "oceania_nations": [
        "Sydney", "Melbourne", "Queenstown", "Auckland", "Cairns", "Hobart", "Rotorua", "Suva", "Papeete", "Wellington", "Adelaide", "Christchurch",
    ],
    "nordic_polar_nations": [
        "Reykjavik", "Bergen", "Tromso", "Oslo", "Stockholm", "Helsinki", "Rovaniemi", "Torshavn", "Longyearbyen", "Akureyri", "Nuuk", "Trondheim",
    ],
}

# Backward compatibility aliases for cities
CONTINENT_CITIES_MAP["europe_cities"] = CONTINENT_CITIES_MAP["europe_nations"]
CONTINENT_CITIES_MAP["asia_cities"] = CONTINENT_CITIES_MAP["asia_nations"]
CONTINENT_CITIES_MAP["americas_cities"] = CONTINENT_CITIES_MAP["americas_nations"]
CONTINENT_CITIES_MAP["africa_cities"] = CONTINENT_CITIES_MAP["africa_nations"]
CONTINENT_CITIES_MAP["oceania_cities"] = CONTINENT_CITIES_MAP["oceania_nations"]
CONTINENT_CITIES_MAP["nordic_polar_cities"] = CONTINENT_CITIES_MAP["nordic_polar_nations"]

__all__ = [
    "CONTINENT_COUNTRIES_MAP",
    "CONTINENT_CITIES_MAP",
    "ARCHETYPE_TEMPLATES",
    "ARCHETYPE_GENRE_MAP",
]
