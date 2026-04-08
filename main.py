import requests
import json
import re
import csv

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

def load_prompt(prompt_type: str) -> str:
    """
    Load prompt template from file.
    
    Args:
        prompt_type: Type of prompt (e.g., 'games', 'genre', 'personality')
    
    Returns:
        Prompt template string with {USER_TEXT} placeholder
    
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    filename = f"{prompt_type}_only_prompt.txt"
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().strip()

def flatten_games(games_json):
    """
    Flatten games array into stance-grouped dict.
    
    Args:
        games_json: dict with "games" array, each game has "name" and "stance"
    
    Returns:
        dict with 6 keys (one per stance), values are pipe-delimited game names
    """
    stances = ["currently_plays", "likes", "dislikes", "used_to_play", "open_to_try", "wants_to_play"]
    result = {f"games_{stance}": "" for stance in stances}
    
    games = games_json.get("games", [])
    
    # Group games by stance
    stance_groups = {stance: [] for stance in stances}
    
    for game in games:
        name = game.get("name", "").strip()
        stance = game.get("stance", "").strip()
        
        if name and stance in stance_groups:
            stance_groups[stance].append(name)
        elif name and stance:
            # Unexpected stance - log but skip
            print(f"Warning: Unexpected stance '{stance}' for game '{name}'")
    
    # Deduplicate and join with pipes
    for stance in stances:
        unique_games = list(dict.fromkeys(stance_groups[stance]))  # Preserve order while deduping
        result[f"games_{stance}"] = "|".join(unique_games)
    
    return result

def flatten_genres(genres_json):
    """
    Flatten genres array into stance-grouped dict + metadata.
    
    Args:
        genres_json: dict with "genres" array, each has "name", "stance", "source", "inferred_from_games"
    
    Returns:
        dict with 6 keys (5 stance columns + metadata JSON string)
    """
    stances = ["likes", "dislikes", "avoids", "open_to_try", "unknown"]
    result = {f"genres_{stance}": "" for stance in stances}
    result["genres_metadata"] = "[]"
    
    genres = genres_json.get("genres", [])
    
    # Store full metadata as JSON
    result["genres_metadata"] = json.dumps(genres)
    
    # Group genre names by stance
    stance_groups = {stance: [] for stance in stances}
    
    for genre in genres:
        name = genre.get("name", "").strip()
        stance = genre.get("stance", "").strip()
        
        if name and stance in stance_groups:
            stance_groups[stance].append(name)
        elif name and stance:
            print(f"Warning: Unexpected stance '{stance}' for genre '{name}'")
    
    # Deduplicate and join with pipes
    for stance in stances:
        unique_genres = list(dict.fromkeys(stance_groups[stance]))
        result[f"genres_{stance}"] = "|".join(unique_genres)
    
    return result

def flatten_playstyle(playstyle_json):
    """
    Flatten playstyle object to flat dict.
    
    Args:
        playstyle_json: dict with "cooperative", "competitive", "casual_chill" (true/false/null)
    
    Returns:
        dict with 3 keys, values as strings
    """
    fields = ["cooperative", "competitive", "casual_chill"]
    result = {}
    
    for field in fields:
        value = playstyle_json.get(field)
        # Convert to string: true -> "true", false -> "false", null/missing -> "null"
        if value is None:
            result[f"playstyle_{field}"] = "null"
        elif isinstance(value, bool):
            result[f"playstyle_{field}"] = str(value).lower()
        else:
            result[f"playstyle_{field}"] = str(value)
    
    return result

def flatten_social(social_json):
    """
    Flatten social object to flat dict.
    
    Args:
        social_json: dict with "wants_long_term", "wants_group", "open_to_chat" (true/false/null)
    
    Returns:
        dict with 3 keys, values as strings
    """
    fields = ["wants_long_term", "wants_group", "open_to_chat"]
    result = {}
    
    for field in fields:
        value = social_json.get(field)
        if value is None:
            result[f"social_{field}"] = "null"
        elif isinstance(value, bool):
            result[f"social_{field}"] = str(value).lower()
        else:
            result[f"social_{field}"] = str(value)
    
    return result

def flatten_personality(personality_json):
    """
    Flatten personality object to flat dict.
    
    Args:
        personality_json: dict with "chill" (bool), "energy_level" (str), "introverted" (bool)
    
    Returns:
        dict with 3 keys, values as strings
    """
    result = {}
    
    # Handle chill (bool or null)
    chill = personality_json.get("chill")
    if chill is None:
        result["personality_chill"] = "null"
    elif isinstance(chill, bool):
        result["personality_chill"] = str(chill).lower()
    else:
        result["personality_chill"] = str(chill)
    
    # Handle energy_level (string or null)
    energy = personality_json.get("energy_level")
    result["personality_energy_level"] = str(energy) if energy is not None else "null"
    
    # Handle introverted (bool or null)
    introverted = personality_json.get("introverted")
    if introverted is None:
        result["personality_introverted"] = "null"
    elif isinstance(introverted, bool):
        result["personality_introverted"] = str(introverted).lower()
    else:
        result["personality_introverted"] = str(introverted)
    
    return result

def clean_json_output(raw_output: str) -> str:
    """
    Clean LLM output to extract valid JSON.
    Removes markdown code fences and extra text.
    """
    # Remove markdown code fences
    cleaned = re.sub(r'```json\s*', '', raw_output)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = cleaned.strip()
    
    # Try to extract JSON object if there's extra text
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    
    return cleaned

def process_record(post_id: str, intro_text: str) -> dict:
    """
    Process a single record through all 5 prompts and flatten results.
    
    Args:
        post_id: ID from CSV
        intro_text: Introduction content
    
    Returns:
        dict with all 22 columns ready for CSV
    """
    prompt_types = ["games", "genres", "playstyle", "social", "personality"]
    row = {"post_id": post_id}
    
    for prompt_type in prompt_types:
        try:
            # Build prompt
            prompt_template = load_prompt(prompt_type)
            full_prompt = prompt_template.replace("{USER_TEXT}", intro_text)
            
            # Call LLM
            print(f"  Processing {prompt_type}...")
            raw_response = extract_profile_with_prompt(full_prompt)
            
            # Clean and parse JSON
            cleaned = clean_json_output(raw_response)
            parsed = json.loads(cleaned)
            
            # Flatten based on type
            if prompt_type == "games":
                flattened = flatten_games(parsed)
            elif prompt_type == "genres":
                flattened = flatten_genres(parsed)
            elif prompt_type == "playstyle":
                flattened = flatten_playstyle(parsed)
            elif prompt_type == "social":
                flattened = flatten_social(parsed)
            elif prompt_type == "personality":
                flattened = flatten_personality(parsed)
            else:
                flattened = {}
            
            # Merge into row
            row.update(flattened)
            
        except json.JSONDecodeError as e:
            print(f"  ERROR: JSON parse error for {prompt_type}: {e}")
            print(f"  Raw response: {raw_response[:200] if 'raw_response' in locals() else 'N/A'}")
            # Add empty defaults for this prompt type
            if prompt_type == "games":
                row.update({f"games_{s}": "" for s in ["currently_plays", "likes", "dislikes", "used_to_play", "open_to_try", "wants_to_play"]})
            elif prompt_type == "genres":
                row.update({f"genres_{s}": "" for s in ["likes", "dislikes", "avoids", "open_to_try", "unknown"]})
                row["genres_metadata"] = "[]"
            elif prompt_type == "playstyle":
                row.update({f"playstyle_{f}": "null" for f in ["cooperative", "competitive", "casual_chill"]})
            elif prompt_type == "social":
                row.update({f"social_{f}": "null" for f in ["wants_long_term", "wants_group", "open_to_chat"]})
            elif prompt_type == "personality":
                row.update({"personality_chill": "null", "personality_energy_level": "null", "personality_introverted": "null"})
                
        except Exception as e:
            print(f"  ERROR: Unexpected error for {prompt_type}: {e}")
            # Add empty defaults (same as above)
            if prompt_type == "games":
                row.update({f"games_{s}": "" for s in ["currently_plays", "likes", "dislikes", "used_to_play", "open_to_try", "wants_to_play"]})
            elif prompt_type == "genres":
                row.update({f"genres_{s}": "" for s in ["likes", "dislikes", "avoids", "open_to_try", "unknown"]})
                row["genres_metadata"] = "[]"
            elif prompt_type == "playstyle":
                row.update({f"playstyle_{f}": "null" for f in ["cooperative", "competitive", "casual_chill"]})
            elif prompt_type == "social":
                row.update({f"social_{f}": "null" for f in ["wants_long_term", "wants_group", "open_to_chat"]})
            elif prompt_type == "personality":
                row.update({"personality_chill": "null", "personality_energy_level": "null", "personality_introverted": "null"})
    
    return row

def extract_profile_with_prompt(prompt: str):
    """
    Send prompt to LLM and parse response.
    """
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False}
    )
    
    raw = response.json()["response"]
    return raw
    # cleaned = clean_json_output(raw)
    
    # try:
    #     parsed = json.loads(cleaned)
    #     return normalize_profile(parsed)
    # except Exception as e:
    #     print(f"Parse error: {e}")
    #     print(f"Raw: {raw[:200]}")
    #     print(f"Cleaned: {cleaned[:200]}")
    #     return normalize_profile({})

def compute_features(p1, p2):
    return {
        "shared_games": len(set(p1.get("games", [])) & set(p2.get("games", []))),
        "same_timezone": p1.get("timezone") == p2.get("timezone") and p1.get("timezone") is not None,
        "platform_overlap": bool(set(p1.get("platforms", [])) & set(p2.get("platforms", []))),
        "both_long_term": bool(p1.get("social", {}).get("wants_long_term")) and bool(p2.get("social", {}).get("wants_long_term")),
        "both_coop": bool(p1.get("playstyle", {}).get("cooperative")) and bool(p2.get("playstyle", {}).get("cooperative")),
        "competitive_mismatch": bool(p1.get("playstyle", {}).get("competitive")) != bool(p2.get("playstyle", {}).get("competitive")),
        "chill_match": bool(p1.get("personality", {}).get("chill")) and bool(p2.get("personality", {}).get("chill")),
        "mic_match": bool(p1.get("communication", {}).get("mic_ok")) == bool(p2.get("communication", {}).get("mic_ok"))
    }

def compute_score(f):
    score = 0

    score += min(f["shared_games"], 3) * 1.5

    if f["both_coop"]:
        score += 1.5

    if f["both_long_term"]:
        score += 1.5

    if f["chill_match"]:
        score += 1.0

    if f["same_timezone"]:
        score += 1.5
    else:
        score -= 1.0

    if not f["platform_overlap"]:
        score -= 2.0

    if f["competitive_mismatch"]:
        score -= 1.5

    if f["mic_match"]:
        score += 0.5

    return max(0, min(10, score))

def extract_profiles_pipeline():
    """
    Main pipeline: Extract profiles from first 3 intro posts and save to CSV.
    
    HARD LIMIT: Processes exactly 3 records only.
    """
    print("=== Multi-Prompt Profile Extraction Pipeline ===")
    print("Processing first 3 intro posts through 5 prompt types")
    print("Model: qwen2.5:3b\n")
    
    # Define CSV column order
    fieldnames = [
        "post_id",
        # Games (6 columns)
        "games_currently_plays", "games_likes", "games_dislikes", 
        "games_used_to_play", "games_open_to_try", "games_wants_to_play",
        # Genres (6 columns)
        "genres_likes", "genres_dislikes", "genres_avoids", 
        "genres_open_to_try", "genres_unknown", "genres_metadata",
        # Playstyle (3 columns)
        "playstyle_cooperative", "playstyle_competitive", "playstyle_casual_chill",
        # Social (3 columns)
        "social_wants_long_term", "social_wants_group", "social_open_to_chat",
        # Personality (3 columns)
        "personality_chill", "personality_energy_level", "personality_introverted"
    ]
    
    # Load records - HARD LIMIT: 3 only
    print("Loading first 3 records from prompt_data.csv...")
    records = []
    with open("prompt_data.csv", 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 3:  # HARD LIMIT
                break
            records.append({
                "id": row["id"],
                "intro": row["introduction content"]
            })
    
    print(f"Loaded {len(records)} records\n")
    
    # Process each record
    all_rows = []
    for i, record in enumerate(records, 1):
        print(f"=== Processing record {i}/3 (ID: {record['id']}) ===")
        row = process_record(record['id'], record['intro'])
        all_rows.append(row)
        print(f"Completed record {i}/3\n")
    
    # Write to CSV
    output_file = "profile_extraction_output.csv"
    print(f"Writing results to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\n✓ Success! Wrote {len(all_rows)} rows to {output_file}")
    print(f"  Columns: {len(fieldnames)}")
    print(f"  File: {output_file}")
    print("\n=== Pipeline complete ===")


if __name__ == "__main__":
    # Run the extraction pipeline
    extract_profiles_pipeline()