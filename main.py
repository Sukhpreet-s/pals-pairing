import argparse
import csv
import json

from extraction_pipeline import extract_profiles_pipeline
from overlap_system.pipeline import score_all_pairs


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


def load_extracted_profile_rows(
    input_file: str = "profile_extraction_output.csv",
) -> list[dict[str, str]]:
    with open(input_file, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [dict(row) for row in reader]


def run_extraction_pipeline(
    input_file: str = "prompt_data.csv",
    output_file: str = "profile_extraction_output.csv",
    limit: int = 3,
) -> None:
    extract_profiles_pipeline(input_file=input_file, output_file=output_file, limit=limit)


def run_scoring_pipeline(
    input_file: str = "profile_extraction_output.csv",
    output_file: str = "pair_overlap_output.csv",
) -> None:
    extracted_rows = load_extracted_profile_rows(input_file=input_file)

    if len(extracted_rows) < 2:
        print(f"Not enough extracted rows in {input_file} to score pairs.")
        return

    overlap_rows = score_all_pairs(extracted_rows, id_field="post_id")
    write_pair_overlap_output(overlap_rows, output_file=output_file)
    print(f"Wrote {len(overlap_rows)} pair overlap rows to {output_file}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run extraction or pair-overlap scoring pipelines."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser(
        "extract",
        help="Run extraction pipeline and write profile_extraction_output.csv",
    )
    extract_parser.add_argument(
        "--input-file",
        default="prompt_data.csv",
        help="Source CSV used for profile extraction",
    )
    extract_parser.add_argument(
        "--output-file",
        default="profile_extraction_output.csv",
        help="Destination CSV for extracted profiles",
    )
    extract_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum number of input rows to process",
    )

    score_parser = subparsers.add_parser(
        "score",
        help="Run scoring pipeline and write pair_overlap_output.csv",
    )
    score_parser.add_argument(
        "--input-file",
        default="profile_extraction_output.csv",
        help="Extracted profiles CSV to score",
    )
    score_parser.add_argument(
        "--output-file",
        default="pair_overlap_output.csv",
        help="Destination CSV for pair overlap scores",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "extract":
        run_extraction_pipeline(
            input_file=args.input_file,
            output_file=args.output_file,
            limit=args.limit,
        )
    elif args.command == "score":
        run_scoring_pipeline(input_file=args.input_file, output_file=args.output_file)


if __name__ == "__main__":
    main()
