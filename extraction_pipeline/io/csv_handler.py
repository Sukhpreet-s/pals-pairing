import csv

from extraction_pipeline.config import PROFILE_FIELDNAMES


def load_source_records(input_file: str, limit: int) -> list[dict[str, str]]:
    """Load source records from CSV file with post ID and introduction text."""
    records: list[dict[str, str]] = []
    with open(input_file, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader):
            if index >= limit:
                break
            records.append(
                {
                    "id": row["id"],
                    "intro": row["introduction content"],
                }
            )
    return records


def write_profile_rows(rows: list[dict[str, str]], output_file: str) -> None:
    """Write extracted profile rows to CSV file."""
    with open(output_file, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=PROFILE_FIELDNAMES, quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        writer.writerows(rows)
