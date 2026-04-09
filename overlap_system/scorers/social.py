from ..config import SOCIAL_WEIGHTS
from ..models import PairOverlapResult, UserProfile
from ..utils import clamp


def _long_term_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.0
    if left and right:
        return 1.0
    if not left and not right:
        return 0.3
    return -1.0


def _group_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.0
    if left and right:
        return 1.0
    if not left and not right:
        return 0.0
    return -0.5


def _chat_alignment(left: bool | None, right: bool | None) -> float:
    if left is None or right is None:
        return 0.0
    if left and right:
        return 1.0
    if not left and not right:
        return 0.0
    return -0.5


def score_social(a: UserProfile, b: UserProfile) -> PairOverlapResult:
    long_term_alignment = _long_term_alignment(
        a["social_wants_long_term"], b["social_wants_long_term"]
    )
    group_alignment = _group_alignment(a["social_wants_group"], b["social_wants_group"])
    chat_alignment = _chat_alignment(a["social_open_to_chat"], b["social_open_to_chat"])

    weighted_alignment = (
        SOCIAL_WEIGHTS["wants_long_term"] * long_term_alignment
        + SOCIAL_WEIGHTS["wants_group"] * group_alignment
        + SOCIAL_WEIGHTS["open_to_chat"] * chat_alignment
    )
    score = clamp((weighted_alignment + 1.0) / 2.0, 0.0, 1.0)

    return PairOverlapResult(
        raw_features={
            "long_term_alignment": long_term_alignment,
            "group_alignment": group_alignment,
            "open_to_chat_alignment": chat_alignment,
            "social_values": {
                "a": {
                    "wants_long_term": a["social_wants_long_term"],
                    "wants_group": a["social_wants_group"],
                    "open_to_chat": a["social_open_to_chat"],
                },
                "b": {
                    "wants_long_term": b["social_wants_long_term"],
                    "wants_group": b["social_wants_group"],
                    "open_to_chat": b["social_open_to_chat"],
                },
            },
        },
        score=score,
    )
