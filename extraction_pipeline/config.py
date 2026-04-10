from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"
PROMPT_TYPES = ["games", "genres", "playstyle", "social", "personality"]
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

PROFILE_FIELDNAMES = [
    "post_id",
    "games_currently_plays",
    "games_likes",
    "games_dislikes",
    "games_used_to_play",
    "games_open_to_try",
    "games_wants_to_play",
    "genres_likes",
    "genres_dislikes",
    "genres_avoids",
    "genres_open_to_try",
    "genres_unknown",
    "genres_metadata",
    "playstyle_cooperative",
    "playstyle_competitive",
    "playstyle_casual_chill",
    "social_wants_long_term",
    "social_wants_group",
    "social_open_to_chat",
    "personality_chill",
    "personality_energy_level",
    "personality_introverted",
]
