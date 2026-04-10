import json


def flatten_genres(genres_json: dict) -> dict[str, str]:
    """Flatten genres data from JSON to CSV row format."""
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


def default_values_genres() -> dict[str, str]:
    """Return default values for genres when extraction fails."""
    values = {
        f"genres_{stance}": ""
        for stance in ["likes", "dislikes", "avoids", "open_to_try", "unknown"]
    }
    values["genres_metadata"] = "[]"
    return values
