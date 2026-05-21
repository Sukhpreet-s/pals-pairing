from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL = "qwen2.5:3b"
# MODEL = "hf.co/QuantFactory/Qwen2.5-7B-Instruct-GGUF:Q4_K_M"
MODEL = "hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:UD-Q4_K_XL"
# MODEL = "hf.co/Qwen/Qwen3-8B-GGUF:Q4_K_M"
PROMPT_TYPES = ["games"]
								#"genres", "playstyle", "social", "personality"]
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Input CSV column names
SOURCE_CSV_ID_COLUMN = "id"
SOURCE_CSV_INTRO_COLUMN = "introduction content"

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
