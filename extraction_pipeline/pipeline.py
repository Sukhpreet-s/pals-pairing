"""Main extraction pipeline orchestration."""

import json
import logging

from .config import PROFILE_FIELDNAMES, PROMPT_TYPES, MODEL
from .api import extract_profile_with_prompt
from .parsers import (
    clean_json_output,
    parse_json,
    flatten_by_prompt_type,
    default_values_for_prompt,
)
from .prompts import load_prompt
from .io import load_source_records, write_profile_rows

logger = logging.getLogger(__name__)


def extract_profiles_pipeline(
    input_file: str = "prompt_data.csv",
    output_file: str = "profile_extraction_output.csv",
    limit: int = 3,
) -> list[dict[str, str]]:
    """
    Extract player profiles from introduction texts using multi-prompt analysis.

    Processes each record through 5 prompt types (games, genres, playstyle, social,
    personality) and writes results to CSV.

    @param input_file - Path to input CSV with post IDs and introduction content
    @param output_file - Path to write extracted profiles CSV
    @param limit - Maximum number of records to process
    @returns List of extracted profile rows with all profile fields
    """
    print(f"Processing first {limit} intro posts through 5 prompt types")
    print(f"Model: {MODEL}\n")

    print(f"Loading first {limit} records from {input_file}...")
    records = load_source_records(input_file, limit)
    print(f"Loaded {len(records)} records\n")

    all_rows: list[dict[str, str]] = []
    for index, record in enumerate(records, 1):
        print(f"=== Processing record {index}/{len(records)} (ID: {record['id']}) ===")
        all_rows.append(process_record(record["id"], record["intro"]))
        print(f"Completed record {index}/{len(records)}\n")

    print(f"Writing results to {output_file}...")
    write_profile_rows(all_rows, output_file)
    print(f"\n✓ Success! Wrote {len(all_rows)} rows to {output_file}")
    print(f"  Columns: {len(PROFILE_FIELDNAMES)}")
    print("\n=== Extraction pipeline complete ===")
    return all_rows


def process_record(post_id: str, intro_text: str) -> dict[str, str]:
    """
    Process a single post through all prompt types to extract player profile.

    Handles errors gracefully by using default values if extraction fails for any
    prompt type.

    @param post_id - Unique identifier for the post
    @param intro_text - User introduction text to extract profile from
    @returns Profile row with post_id and all extracted profile fields
    """
    row: dict[str, str] = {"post_id": post_id}
    for prompt_type in PROMPT_TYPES:
        try:
            logger.debug("Extracting profile", extra={"prompt_type": prompt_type})

            prompt_template = load_prompt(prompt_type)
            logger.debug("Loaded prompt template", extra={"length": len(prompt_template)})

            full_prompt = prompt_template.replace("{USER_TEXT}", intro_text)
            logger.debug("Generated full prompt", extra={"length": len(full_prompt)})
            
            logger.info(f"Processing {prompt_type} for post {post_id}")

            raw_response = extract_profile_with_prompt(full_prompt)
            logger.debug("Raw response", extra={"length": len(raw_response)})

            cleaned = clean_json_output(raw_response)
            logger.debug("Cleaned JSON", extra={"length": len(cleaned), "content": cleaned[:200]})

            parsed = parse_json(cleaned)
            logger.debug(
                "JSON parsed",
                extra={"keys": list(parsed.keys())[:10]}
            )

            flattened = flatten_by_prompt_type(prompt_type, parsed)
            logger.debug(
                "Flattened result",
                extra={"fields": list(flattened.keys())}
            )

            row.update(flattened)

        except json.JSONDecodeError as error:
            logger.error(
                f"JSON parse error for {prompt_type} on post {post_id}: {error}",
                exc_info=True,
            )
            row.update(default_values_for_prompt(prompt_type))

        except Exception as error:
            logger.error(
                f"Unexpected error for {prompt_type} on post {post_id}: {error}",
                exc_info=True,
            )
            row.update(default_values_for_prompt(prompt_type))

    return row
