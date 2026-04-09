from ..config import PERSONALITY_WEIGHTS
from ..models import PairOverlapResult, UserProfile
from ..utils import clamp, field_known_confidence

ENERGY_ORDER = {"low": 0, "medium": 1, "high": 2}


def _chill_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.5
    if left and right:
        return 1.0
    if not left and not right:
        return 0.5
    return 0.25


def _energy_alignment(left: str | None, right: str | None) -> tuple[float, int | None]:
    if left is None or right is None:
        return 0.5, None

    left_value = ENERGY_ORDER[left]
    right_value = ENERGY_ORDER[right]
    distance = abs(left_value - right_value)
    if distance == 0:
        return 1.0, distance
    if distance == 1:
        return 0.5, distance
    return 0.0, distance


def _introversion_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.5
    if left and right:
        return 1.0
    if not left and not right:
        return 0.5
    return 0.25


def score_personality(a: UserProfile, b: UserProfile) -> PairOverlapResult:
    chill_alignment = _chill_alignment(a["personality_chill"], b["personality_chill"])
    energy_alignment, energy_distance = _energy_alignment(
        a["personality_energy_level"], b["personality_energy_level"]
    )
    introversion_alignment = _introversion_alignment(
        a["personality_introverted"], b["personality_introverted"]
    )

    score = (
        PERSONALITY_WEIGHTS["chill"] * chill_alignment
        + PERSONALITY_WEIGHTS["energy_level"] * energy_alignment
        + PERSONALITY_WEIGHTS["introverted"] * introversion_alignment
    )
    score = clamp(score, 0.0, 1.0)
    confidence = field_known_confidence(
        [
            a["personality_chill"] if b["personality_chill"] is not None else None,
            a["personality_energy_level"]
            if b["personality_energy_level"] is not None
            else None,
            a["personality_introverted"]
            if b["personality_introverted"] is not None
            else None,
        ]
    )

    return PairOverlapResult(
        raw_features={
            "chill_alignment": chill_alignment,
            "energy_alignment": energy_alignment,
            "energy_distance": energy_distance,
            "introversion_alignment": introversion_alignment,
            "personality_values": {
                "a": {
                    "chill": a["personality_chill"],
                    "energy_level": a["personality_energy_level"],
                    "introverted": a["personality_introverted"],
                },
                "b": {
                    "chill": b["personality_chill"],
                    "energy_level": b["personality_energy_level"],
                    "introverted": b["personality_introverted"],
                },
            },
        },
        score=score,
        confidence=confidence,
    )
