from ..config import PLAYSTYLE_WEIGHTS
from ..models import PairOverlapResult, UserProfile
from ..utils import clamp, field_known_confidence


def _cooperative_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.0
    if left and right:
        return 1.0
    if not left and not right:
        return 0.0
    return -1.0


def _competitive_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.0
    if left == right:
        return 1.0
    return -1.0


def _casual_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.0
    if left and right:
        return 1.0
    if not left and not right:
        return 0.0
    return -0.5


def score_playstyle(a: UserProfile, b: UserProfile) -> PairOverlapResult:
    cooperative_alignment = _cooperative_alignment(
        a["playstyle_cooperative"], b["playstyle_cooperative"]
    )
    competitive_alignment = _competitive_alignment(
        a["playstyle_competitive"], b["playstyle_competitive"]
    )
    casual_alignment = _casual_alignment(
        a["playstyle_casual_chill"], b["playstyle_casual_chill"]
    )

    weighted_alignment = (
        PLAYSTYLE_WEIGHTS["cooperative"] * cooperative_alignment
        + PLAYSTYLE_WEIGHTS["competitive"] * competitive_alignment
        + PLAYSTYLE_WEIGHTS["casual_chill"] * casual_alignment
    )
    score = clamp((weighted_alignment + 1.0) / 2.0, 0.0, 1.0)
    confidence = field_known_confidence(
        [
            a["playstyle_cooperative"] if b["playstyle_cooperative"] is not None else None,
            a["playstyle_competitive"] if b["playstyle_competitive"] is not None else None,
            a["playstyle_casual_chill"]
            if b["playstyle_casual_chill"] is not None
            else None,
        ]
    )

    return PairOverlapResult(
        raw_features={
            "cooperative_alignment": cooperative_alignment,
            "competitive_alignment": competitive_alignment,
            "casual_chill_alignment": casual_alignment,
            "playstyle_values": {
                "a": {
                    "cooperative": a["playstyle_cooperative"],
                    "competitive": a["playstyle_competitive"],
                    "casual_chill": a["playstyle_casual_chill"],
                },
                "b": {
                    "cooperative": b["playstyle_cooperative"],
                    "competitive": b["playstyle_competitive"],
                    "casual_chill": b["playstyle_casual_chill"],
                },
            },
        },
        score=score,
        confidence=confidence,
    )
