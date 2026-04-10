def flatten_social(social_json: dict) -> dict[str, str]:
    """Flatten social data from JSON to CSV row format."""
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


def default_values_social() -> dict[str, str]:
    """Return default values for social when extraction fails."""
    return {
        f"social_{field}": "null"
        for field in ["wants_long_term", "wants_group", "open_to_chat"]
    }
