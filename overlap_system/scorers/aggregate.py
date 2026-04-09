from ..config import DOMAIN_WEIGHTS
from ..models import AggregateOverlapResult, UserProfile
from ..utils import clamp
from .games import score_games
from .genres import score_genres
from .personality import score_personality
from .playstyle import score_playstyle
from .social import score_social


def score_overlap(a: UserProfile, b: UserProfile) -> AggregateOverlapResult:
    games = score_games(a, b)
    genres = score_genres(a, b)
    playstyle = score_playstyle(a, b)
    social = score_social(a, b)
    personality = score_personality(a, b)

    domain_scores = {
        "games": games["score"],
        "genres": genres["score"],
        "playstyle": playstyle["score"],
        "social": social["score"],
        "personality": personality["score"],
    }
    domain_confidence = {
        "games": games["confidence"],
        "genres": genres["confidence"],
        "playstyle": playstyle["confidence"],
        "social": social["confidence"],
        "personality": personality["confidence"],
    }

    overall_score = (
        DOMAIN_WEIGHTS["games"] * domain_scores["games"]
        + DOMAIN_WEIGHTS["genres"] * domain_scores["genres"]
        + DOMAIN_WEIGHTS["playstyle"] * domain_scores["playstyle"]
        + DOMAIN_WEIGHTS["social"] * domain_scores["social"]
        + DOMAIN_WEIGHTS["personality"] * domain_scores["personality"]
    )

    raw_features = {
        "games": games["raw_features"],
        "genres": genres["raw_features"],
        "playstyle": playstyle["raw_features"],
        "social": social["raw_features"],
        "personality": personality["raw_features"],
    }

    return AggregateOverlapResult(
        overall_overlap_score=clamp(overall_score, 0.0, 1.0),
        domain_scores=domain_scores,
        domain_confidence=domain_confidence,
        raw_features=raw_features,
    )
