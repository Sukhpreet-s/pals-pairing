# CSV column names
PROFILE_ID_FIELD = "post_id"
PROFILE_ID_FALLBACK_FIELD = "id"

DOMAIN_WEIGHTS = {
    "games": 0.40,
    "genres": 0.20,
    "playstyle": 0.15,
    "social": 0.15,
    "personality": 0.10,
}

GAME_WEIGHTS = {
    "strong_overlap": 1.00,
    "soft_overlap": 0.50,
    "historical_overlap": 0.25,
    "conflict": -1.00,
    "normalizer": 4.0,
}

GENRE_WEIGHTS = {
    "liked_overlap": 0.80,
    "soft_overlap": 0.40,
    "dislike_conflict": -0.80,
    "avoid_conflict": -1.00,
    "normalizer": 4.0,
}

PLAYSTYLE_WEIGHTS = {
    "cooperative": 0.40,
    "competitive": 0.30,
    "casual_chill": 0.30,
}

SOCIAL_WEIGHTS = {
    "wants_long_term": 0.45,
    "wants_group": 0.25,
    "open_to_chat": 0.30,
}

PERSONALITY_WEIGHTS = {
    "chill": 0.45,
    "energy_level": 0.35,
    "introverted": 0.20,
}
