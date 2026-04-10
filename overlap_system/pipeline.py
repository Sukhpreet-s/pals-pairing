from itertools import combinations
from typing import Any, Mapping
import csv
import json

from .normalizers import normalize_user_profile
from .scorers.aggregate import score_overlap


def score_profiles_pipeline(input_file, output_file):
    extracted_rows = load_extracted_profile_rows(input_file=input_file)

    if len(extracted_rows) < 2:
        print(f"Not enough extracted rows in {input_file} to score pairs.")
        return

    overlap_rows = score_all_pairs(extracted_rows, id_field="post_id")
    write_pair_overlap_output(overlap_rows, output_file=output_file)
    print(f"Wrote {len(overlap_rows)} pair overlap rows to {output_file}")


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


def score_pair(row_a: Mapping[str, Any], row_b: Mapping[str, Any]) -> dict[str, Any]:
    user_a = normalize_user_profile(row_a)
    user_b = normalize_user_profile(row_b)
    return score_overlap(user_a, user_b)


def load_extracted_profile_rows(
    input_file: str = "profile_extraction_output.csv",
) -> list[dict[str, str]]:
    with open(input_file, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [dict(row) for row in reader]


def write_pair_overlap_output(
    overlap_rows: list[dict], output_file: str = "pair_overlap_output.csv"
) -> None:
    fieldnames = [
        "user_a_id",
        "user_b_id",
        "overall_overlap_score",
        "games_score",
        "genres_score",
        "playstyle_score",
        "social_score",
        "personality_score",
        "raw_features_json",
    ]

    with open(output_file, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in overlap_rows:
            writer.writerow(
                {
                    "user_a_id": row["user_a_id"],
                    "user_b_id": row["user_b_id"],
                    "overall_overlap_score": row["overall_overlap_score"],
                    "games_score": row["domain_scores"]["games"],
                    "genres_score": row["domain_scores"]["genres"],
                    "playstyle_score": row["domain_scores"]["playstyle"],
                    "social_score": row["domain_scores"]["social"],
                    "personality_score": row["domain_scores"]["personality"],
                    "raw_features_json": json.dumps(row["raw_features"], sort_keys=True),
                }
            )
