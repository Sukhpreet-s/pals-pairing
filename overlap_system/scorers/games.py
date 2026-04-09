from ..config import GAME_WEIGHTS
from ..models import PairOverlapResult, UserProfile
from ..utils import clamp, set_presence_confidence, sorted_list


def score_games(a: UserProfile, b: UserProfile) -> PairOverlapResult:
    positive_a = a["games_currently_plays"] | a["games_likes"]
    positive_b = b["games_currently_plays"] | b["games_likes"]
    soft_a = a["games_open_to_try"] | a["games_wants_to_play"]
    soft_b = b["games_open_to_try"] | b["games_wants_to_play"]
    historical_a = a["games_used_to_play"]
    historical_b = b["games_used_to_play"]
    negative_a = a["games_dislikes"]
    negative_b = b["games_dislikes"]

    shared_strong = positive_a & positive_b
    shared_soft = (positive_a & soft_b) | (positive_b & soft_a)
    shared_historical = historical_a & historical_b
    conflicts = (positive_a & negative_b) | (positive_b & negative_a)

    raw_score = (
        len(shared_strong) * GAME_WEIGHTS["strong_overlap"]
        + len(shared_soft) * GAME_WEIGHTS["soft_overlap"]
        + len(shared_historical) * GAME_WEIGHTS["historical_overlap"]
    )
    score = clamp(raw_score / GAME_WEIGHTS["normalizer"], 0.0, 1.0)
    confidence = set_presence_confidence(
        [
            (a["games_currently_plays"], b["games_currently_plays"]),
            (a["games_likes"], b["games_likes"]),
            (a["games_dislikes"], b["games_dislikes"]),
            (a["games_used_to_play"], b["games_used_to_play"]),
            (a["games_open_to_try"], b["games_open_to_try"]),
            (a["games_wants_to_play"], b["games_wants_to_play"]),
        ]
    )

    return PairOverlapResult(
        raw_features={
            "shared_strong_games": sorted_list(shared_strong),
            "shared_soft_games": sorted_list(shared_soft),
            "shared_historical_games": sorted_list(shared_historical),
            "game_conflicts": sorted_list(conflicts),
            "game_total_overlap_count": len(shared_strong)
            + len(shared_soft)
            + len(shared_historical),
            "game_total_conflict_count": len(conflicts),
        },
        score=score,
        confidence=confidence,
    )
