import json
import re


def clean_json_output(raw_output: str) -> str:
    """Clean raw LLM output to extract valid JSON."""
    cleaned = re.sub(r"```json\s*", "", raw_output)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    return cleaned


def parse_json(json_str: str) -> dict:
    """Parse JSON string and return parsed dictionary."""
    return json.loads(json_str)
