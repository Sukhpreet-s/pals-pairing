def flatten_playstyle(playstyle_json: dict) -> dict[str, str]:
    """Flatten playstyle data from JSON to CSV row format."""
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


def default_values_playstyle() -> dict[str, str]:
    """Return default values for playstyle when extraction fails."""
    return {
        f"playstyle_{field}": "null"
        for field in ["cooperative", "competitive", "casual_chill"]
    }
