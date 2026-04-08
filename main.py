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

def load_csv_data(filename: str, n: int = 10, column: str = "introduction content") -> list:
    """
    Load first N records from CSV and extract specified column.
    
    Args:
        filename: CSV file path
        n: Number of records to load (default: 10)
        column: Column name to extract (default: "introduction content")
    
    Returns:
        List of strings from the specified column
    
    Notes:
        - Handles UTF-8 with BOM
        - Skips header row automatically
    """
    results = []
    
    with open(filename, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            if i >= n:
                break
            
            if column in row:
                results.append(row[column])
            else:
                raise KeyError(f"Column '{column}' not found in CSV. Available: {list(row.keys())}")
    
    return results

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

def get_prompt(prompt_type: str, user_text: str) -> str:
    """
    Create final prompt by loading template and inserting user text.
    
    Args:
        prompt_type: Type of prompt to load (e.g., 'games', 'genre', 'personality')
                    Use 'default' for old hardcoded prompt
        user_text: User introduction text to analyze
    
    Returns:
        Complete prompt ready for LLM

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """

    # Load from file
    template = load_prompt(prompt_type)
    return template.replace("{USER_TEXT}", user_text)

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

def main():
    """
    Main pipeline: Load CSV data and process with LLM.
    """
    print("=== Starting main pipeline ===\n")
    
    # Load CSV data
    try:
        intro_texts = load_csv_data("prompt_data.csv", n=1, column="introduction content")
        print(f"✓ Loaded {len(intro_texts)} introductions from CSV\n")
    except Exception as e:
        print(f"✗ Error loading CSV: {e}")
        return
    
    # Process each introduction
    for i, text in enumerate(intro_texts, start=1):
        print(f"\n--- Processing intro {i}/{len(intro_texts)} ---")
        print(f"Text preview: {text[:100]}...")
        
        # Create prompt using 'games' type
        try:
            prompt = get_prompt("games", text)
            print(f"✓ Prompt created (length: {len(prompt)} chars)")
        except Exception as e:
            print(f"✗ Error creating prompt: {e}")
            continue
        
        # Send to LLM
        try:
            profile = extract_profile_with_prompt(prompt)
            print(f"✓ Extracted profile: {profile}")
            # print("LLM extraction process is commented for now")
        except Exception as e:
            print(f"✗ Error extracting profile: {e}")
            continue
    
    print("\n=== Pipeline complete ===")


if __name__ == "__main__":
    main()