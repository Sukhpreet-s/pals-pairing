import argparse

from extraction_pipeline import extract_profiles_pipeline
from overlap_system import score_profiles_pipeline


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
    return score_profiles_pipeline(input_file, output_file)


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
