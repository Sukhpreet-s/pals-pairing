def flatten_personality(personality_json: dict) -> dict[str, str]:
    """Flatten personality data from JSON to CSV row format."""
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


def default_values_personality() -> dict[str, str]:
    """Return default values for personality when extraction fails."""
    return {
        "personality_chill": "null",
        "personality_energy_level": "null",
        "personality_introverted": "null",
    }
