"""Unified interface for profile flattening."""
from extraction_pipeline.parsers.flatteners.games import (
    flatten_games,
    default_values_games,
)
from extraction_pipeline.parsers.flatteners.genres import (
    flatten_genres,
    default_values_genres,
)
from extraction_pipeline.parsers.flatteners.playstyle import (
    flatten_playstyle,
    default_values_playstyle,
)
from extraction_pipeline.parsers.flatteners.social import (
    flatten_social,
    default_values_social,
)
from extraction_pipeline.parsers.flatteners.personality import (
    flatten_personality,
    default_values_personality,
)


def flatten_by_prompt_type(prompt_type: str, parsed: dict) -> dict[str, str]:
    """Flatten parsed profile data based on prompt type."""
    if prompt_type == "games":
        return flatten_games(parsed)
    if prompt_type == "genres":
        return flatten_genres(parsed)
    if prompt_type == "playstyle":
        return flatten_playstyle(parsed)
    if prompt_type == "social":
        return flatten_social(parsed)
    if prompt_type == "personality":
        return flatten_personality(parsed)
    return {}


def default_values_for_prompt(prompt_type: str) -> dict[str, str]:
    """Get default values for a prompt type when extraction fails."""
    if prompt_type == "games":
        return default_values_games()
    if prompt_type == "genres":
        return default_values_genres()
    if prompt_type == "playstyle":
        return default_values_playstyle()
    if prompt_type == "social":
        return default_values_social()
    if prompt_type == "personality":
        return default_values_personality()
    return {}
