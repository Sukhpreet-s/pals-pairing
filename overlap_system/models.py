from typing import Any, TypedDict


class UserProfile(TypedDict):
    games_currently_plays: set[str]
    games_likes: set[str]
    games_dislikes: set[str]
    games_used_to_play: set[str]
    games_open_to_try: set[str]
    games_wants_to_play: set[str]
    genres_likes: set[str]
    genres_dislikes: set[str]
    genres_avoids: set[str]
    genres_open_to_try: set[str]
    genres_unknown: set[str]
    genres_metadata: list[dict[str, Any]]
    playstyle_cooperative: bool | None
    playstyle_competitive: bool | None
    playstyle_casual_chill: bool | None
    social_wants_long_term: bool | None
    social_wants_group: bool | None
    social_open_to_chat: bool | None
    personality_chill: bool | None
    personality_energy_level: str | None
    personality_introverted: bool | None


class PairOverlapResult(TypedDict):
    raw_features: dict[str, Any]
    score: float
    confidence: float


class AggregateOverlapResult(TypedDict):
    overall_overlap_score: float
    domain_scores: dict[str, float]
    domain_confidence: dict[str, float]
    raw_features: dict[str, Any]
