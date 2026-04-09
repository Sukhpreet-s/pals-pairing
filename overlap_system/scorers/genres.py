from ..config import GENRE_WEIGHTS
from ..models import PairOverlapResult, UserProfile
from ..utils import clamp, set_presence_confidence, sorted_list


def score_genres(a: UserProfile, b: UserProfile) -> PairOverlapResult:
    likes_a = a["genres_likes"]
    likes_b = b["genres_likes"]
    open_a = a["genres_open_to_try"]
    open_b = b["genres_open_to_try"]
    dislikes_a = a["genres_dislikes"]
    dislikes_b = b["genres_dislikes"]
    avoids_a = a["genres_avoids"]
    avoids_b = b["genres_avoids"]

    shared_liked = likes_a & likes_b
    shared_soft = (likes_a & open_b) | (likes_b & open_a)
    conflicts_dislike = (likes_a & dislikes_b) | (likes_b & dislikes_a)
    conflicts_avoid = (likes_a & avoids_b) | (likes_b & avoids_a)

    raw_score = (
        len(shared_liked) * GENRE_WEIGHTS["liked_overlap"]
        + len(shared_soft) * GENRE_WEIGHTS["soft_overlap"]
        + len(conflicts_dislike) * GENRE_WEIGHTS["dislike_conflict"]
        + len(conflicts_avoid) * GENRE_WEIGHTS["avoid_conflict"]
    )
    score = clamp(raw_score / GENRE_WEIGHTS["normalizer"], 0.0, 1.0)
    confidence = set_presence_confidence(
        [
            (a["genres_likes"], b["genres_likes"]),
            (a["genres_dislikes"], b["genres_dislikes"]),
            (a["genres_avoids"], b["genres_avoids"]),
            (a["genres_open_to_try"], b["genres_open_to_try"]),
        ]
    )

    return PairOverlapResult(
        raw_features={
            "shared_liked_genres": sorted_list(shared_liked),
            "shared_soft_genres": sorted_list(shared_soft),
            "genre_conflicts_dislike": sorted_list(conflicts_dislike),
            "genre_conflicts_avoid": sorted_list(conflicts_avoid),
        },
        score=score,
        confidence=confidence,
    )
