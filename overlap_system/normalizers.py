import json
from typing import Any, Mapping

from .models import UserProfile

ENERGY_MAP = {
    "low": "low",
    "calm": "low",
    "quiet": "low",
    "reserved": "low",
    "medium": "medium",
    "mid": "medium",
    "balanced": "medium",
    "high": "high",
    "energetic": "high",
    "loud": "high",
}


def normalize_pipe_list(value: str | None) -> set[str]:
    if value is None:
        return set()
    raw = str(value).strip()
    if not raw:
        return set()
    return {item.strip().lower() for item in raw.split("|") if item.strip()}


def normalize_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value

    lowered = str(value).strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    if lowered in {"null", "none", "", "unknown", "na", "n/a"}:
        return None
    return None


def normalize_energy_level(value: str | None) -> str | None:
    if value is None:
        return None
    lowered = str(value).strip().lower()
    if lowered in {"", "null", "none", "unknown", "na", "n/a"}:
        return None
    return ENERGY_MAP.get(lowered)


def normalize_genres_metadata(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if value is None:
        return []
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    return []


def normalize_user_profile(row: Mapping[str, Any]) -> UserProfile:
    return UserProfile(
        games_currently_plays=normalize_pipe_list(row.get("games_currently_plays")),
        games_likes=normalize_pipe_list(row.get("games_likes")),
        games_dislikes=normalize_pipe_list(row.get("games_dislikes")),
        games_used_to_play=normalize_pipe_list(row.get("games_used_to_play")),
        games_open_to_try=normalize_pipe_list(row.get("games_open_to_try")),
        games_wants_to_play=normalize_pipe_list(row.get("games_wants_to_play")),
        genres_likes=normalize_pipe_list(row.get("genres_likes")),
        genres_dislikes=normalize_pipe_list(row.get("genres_dislikes")),
        genres_avoids=normalize_pipe_list(row.get("genres_avoids")),
        genres_open_to_try=normalize_pipe_list(row.get("genres_open_to_try")),
        genres_unknown=normalize_pipe_list(row.get("genres_unknown")),
        genres_metadata=normalize_genres_metadata(row.get("genres_metadata")),
        playstyle_cooperative=normalize_bool(row.get("playstyle_cooperative")),
        playstyle_competitive=normalize_bool(row.get("playstyle_competitive")),
        playstyle_casual_chill=normalize_bool(row.get("playstyle_casual_chill")),
        social_wants_long_term=normalize_bool(row.get("social_wants_long_term")),
        social_wants_group=normalize_bool(row.get("social_wants_group")),
        social_open_to_chat=normalize_bool(row.get("social_open_to_chat")),
        personality_chill=normalize_bool(row.get("personality_chill")),
        personality_energy_level=normalize_energy_level(row.get("personality_energy_level")),
        personality_introverted=normalize_bool(row.get("personality_introverted")),
    )
