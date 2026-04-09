from itertools import combinations
from typing import Any, Mapping

from .normalizers import normalize_user_profile
from .scorers.aggregate import score_overlap


def score_pair(row_a: Mapping[str, Any], row_b: Mapping[str, Any]) -> dict[str, Any]:
    user_a = normalize_user_profile(row_a)
    user_b = normalize_user_profile(row_b)
    return score_overlap(user_a, user_b)


def score_all_pairs(
    rows: list[Mapping[str, Any]], id_field: str = "post_id"
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for left, right in combinations(rows, 2):
        overlap = score_pair(left, right)
        results.append(
            {
                "user_a_id": str(left.get(id_field, left.get("id", ""))),
                "user_b_id": str(right.get(id_field, right.get("id", ""))),
                **overlap,
            }
        )
    return results
