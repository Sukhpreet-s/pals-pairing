def flatten_games(games_json: dict) -> dict[str, str]:
    """Flatten games data from JSON to CSV row format."""
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


def default_values_games() -> dict[str, str]:
    """Return default values for games when extraction fails."""
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
