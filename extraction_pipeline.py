import csv
import json
import re
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"
PROMPT_TYPES = ["games", "genres", "playstyle", "social", "personality"]
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

PROFILE_FIELDNAMES = [
    "post_id",
    "games_currently_plays",
    "games_likes",
    "games_dislikes",
    "games_used_to_play",
    "games_open_to_try",
    "games_wants_to_play",
    "genres_likes",
    "genres_dislikes",
    "genres_avoids",
    "genres_open_to_try",
    "genres_unknown",
    "genres_metadata",
    "playstyle_cooperative",
    "playstyle_competitive",
    "playstyle_casual_chill",
    "social_wants_long_term",
    "social_wants_group",
    "social_open_to_chat",
    "personality_chill",
    "personality_energy_level",
    "personality_introverted",
]


def load_prompt(prompt_type: str) -> str:
    filename = PROMPTS_DIR / f"{prompt_type}_only_prompt.txt"
    with open(filename, "r", encoding="utf-8") as file:
        return file.read().strip()


def extract_profile_with_prompt(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
    )
    response.raise_for_status()
    payload = response.json()
    return payload["response"]


def clean_json_output(raw_output: str) -> str:
    cleaned = re.sub(r"```json\s*", "", raw_output)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    return cleaned


def flatten_games(games_json: dict) -> dict[str, str]:
    stances = [
        "currently_plays",
        "likes",
        "dislikes",
        "used_to_play",
        "open_to_try",
        "wants_to_play",
    ]
    result = {f"games_{stance}": "" for stance in stances}
    stance_groups = {stance: [] for stance in stances}

    for game in games_json.get("games", []):
        name = game.get("name", "").strip()
        stance = game.get("stance", "").strip()
        if name and stance in stance_groups:
            stance_groups[stance].append(name)
        elif name and stance:
            print(f"Warning: Unexpected stance '{stance}' for game '{name}'")

    for stance in stances:
        unique_games = list(dict.fromkeys(stance_groups[stance]))
        result[f"games_{stance}"] = "|".join(unique_games)
    return result


def flatten_genres(genres_json: dict) -> dict[str, str]:
    stances = ["likes", "dislikes", "avoids", "open_to_try", "unknown"]
    result = {f"genres_{stance}": "" for stance in stances}
    result["genres_metadata"] = "[]"
    genres = genres_json.get("genres", [])
    result["genres_metadata"] = json.dumps(genres)
    stance_groups = {stance: [] for stance in stances}

    for genre in genres:
        name = genre.get("name", "").strip()
        stance = genre.get("stance", "").strip()
        if name and stance in stance_groups:
            stance_groups[stance].append(name)
        elif name and stance:
            print(f"Warning: Unexpected stance '{stance}' for genre '{name}'")

    for stance in stances:
        unique_genres = list(dict.fromkeys(stance_groups[stance]))
        result[f"genres_{stance}"] = "|".join(unique_genres)
    return result


def flatten_playstyle(playstyle_json: dict) -> dict[str, str]:
    fields = ["cooperative", "competitive", "casual_chill"]
    result: dict[str, str] = {}
    for field in fields:
        value = playstyle_json.get(field)
        if value is None:
            result[f"playstyle_{field}"] = "null"
        elif isinstance(value, bool):
            result[f"playstyle_{field}"] = str(value).lower()
        else:
            result[f"playstyle_{field}"] = str(value)
    return result


def flatten_social(social_json: dict) -> dict[str, str]:
    fields = ["wants_long_term", "wants_group", "open_to_chat"]
    result: dict[str, str] = {}
    for field in fields:
        value = social_json.get(field)
        if value is None:
            result[f"social_{field}"] = "null"
        elif isinstance(value, bool):
            result[f"social_{field}"] = str(value).lower()
        else:
            result[f"social_{field}"] = str(value)
    return result


def flatten_personality(personality_json: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    chill = personality_json.get("chill")
    if chill is None:
        result["personality_chill"] = "null"
    elif isinstance(chill, bool):
        result["personality_chill"] = str(chill).lower()
    else:
        result["personality_chill"] = str(chill)

    energy = personality_json.get("energy_level")
    result["personality_energy_level"] = str(energy) if energy is not None else "null"

    introverted = personality_json.get("introverted")
    if introverted is None:
        result["personality_introverted"] = "null"
    elif isinstance(introverted, bool):
        result["personality_introverted"] = str(introverted).lower()
    else:
        result["personality_introverted"] = str(introverted)
    return result


def default_values_for_prompt(prompt_type: str) -> dict[str, str]:
    if prompt_type == "games":
        return {
            f"games_{stance}": ""
            for stance in [
                "currently_plays",
                "likes",
                "dislikes",
                "used_to_play",
                "open_to_try",
                "wants_to_play",
            ]
        }
    if prompt_type == "genres":
        values = {
            f"genres_{stance}": ""
            for stance in ["likes", "dislikes", "avoids", "open_to_try", "unknown"]
        }
        values["genres_metadata"] = "[]"
        return values
    if prompt_type == "playstyle":
        return {
            f"playstyle_{field}": "null"
            for field in ["cooperative", "competitive", "casual_chill"]
        }
    if prompt_type == "social":
        return {
            f"social_{field}": "null"
            for field in ["wants_long_term", "wants_group", "open_to_chat"]
        }
    if prompt_type == "personality":
        return {
            "personality_chill": "null",
            "personality_energy_level": "null",
            "personality_introverted": "null",
        }
    return {}


def flatten_by_prompt_type(prompt_type: str, parsed: dict) -> dict[str, str]:
    if prompt_type == "games":
        return flatten_games(parsed)
    if prompt_type == "genres":
        return flatten_genres(parsed)
    if prompt_type == "playstyle":
        return flatten_playstyle(parsed)
    if prompt_type == "social":
        return flatten_social(parsed)
    if prompt_type == "personality":
        return flatten_personality(parsed)
    return {}


def process_record(post_id: str, intro_text: str) -> dict[str, str]:
    row: dict[str, str] = {"post_id": post_id}
    for prompt_type in PROMPT_TYPES:
        try:
            prompt_template = load_prompt(prompt_type)
            full_prompt = prompt_template.replace("{USER_TEXT}", intro_text)
            print(f"  Processing {prompt_type}...")

            raw_response = extract_profile_with_prompt(full_prompt)
            cleaned = clean_json_output(raw_response)
            parsed = json.loads(cleaned)
            row.update(flatten_by_prompt_type(prompt_type, parsed))

        except json.JSONDecodeError as error:
            print(f"  ERROR: JSON parse error for {prompt_type}: {error}")
            row.update(default_values_for_prompt(prompt_type))

        except Exception as error:
            print(f"  ERROR: Unexpected error for {prompt_type}: {error}")
            row.update(default_values_for_prompt(prompt_type))

    return row


def load_source_records(input_file: str, limit: int) -> list[dict[str, str]]:
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
    with open(output_file, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=PROFILE_FIELDNAMES, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def extract_profiles_pipeline(
    input_file: str = "prompt_data.csv",
    output_file: str = "profile_extraction_output.csv",
    limit: int = 3,
) -> list[dict[str, str]]:
    print("=== Multi-Prompt Profile Extraction Pipeline ===")
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
