import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

def clean_json_output(raw: str) -> str:
    raw = raw.strip()

    # Remove ```json ... ``` fences
    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # Keep only text between first { and last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end+1]

    return raw.strip()

def normalize_profile(data: dict) -> dict:
    profile = {
        "timezone": data.get("timezone"),
        "platforms": data.get("platforms", []) or [],
        "games": data.get("games", []) or [],
        "tags": data.get("tags", []) or [],
        "playstyle": {
            "cooperative": False,
            "competitive": False
        },
        "social": {
            "wants_long_term": False
        },
        "personality": {
            "chill": False
        },
        "communication": {
            "mic_ok": False
        }
    }

    # Handle playstyle
    ps = data.get("playstyle")
    if isinstance(ps, dict):
        profile["playstyle"]["cooperative"] = bool(ps.get("cooperative", False))
        profile["playstyle"]["competitive"] = bool(ps.get("competitive", False))
    elif isinstance(ps, str):
        ps_lower = ps.lower()
        profile["playstyle"]["cooperative"] = "coop" in ps_lower or "cooperative" in ps_lower
        profile["playstyle"]["competitive"] = "competitive" in ps_lower or "pvp" in ps_lower

    # Handle social
    social = data.get("social")
    if isinstance(social, dict):
        profile["social"]["wants_long_term"] = bool(social.get("wants_long_term", False))
    elif isinstance(social, str):
        profile["social"]["wants_long_term"] = "long" in social.lower()
    elif isinstance(social, bool):
        profile["social"]["wants_long_term"] = social

    # Handle personality
    personality = data.get("personality")
    if isinstance(personality, dict):
        profile["personality"]["chill"] = bool(personality.get("chill", False))
    elif isinstance(personality, str):
        profile["personality"]["chill"] = "chill" in personality.lower()

    # Handle communication
    comm = data.get("communication")
    if isinstance(comm, dict):
        profile["communication"]["mic_ok"] = bool(comm.get("mic_ok", False))
    elif isinstance(comm, str):
        profile["communication"]["mic_ok"] = "mic" in comm.lower()

    return profile



def extract_profile(text):
    prompt = get_prompt(text)

    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False}
    )
    print("Prompt:", prompt)

    raw = response.json()["response"]
    print("Raw response:", raw)
    
    cleaned = clean_json_output(raw)

    try:
        parsed = json.loads(cleaned)
        return normalize_profile(parsed)
    except Exception as e:
        print("Parse error:", raw)
        print("Cleaned:", cleaned)
        print("Exception:", e)
        return normalize_profile({})

def get_prompt(text):
    prompt = f"""
Extract structured data from this gaming intro.

Return ONLY valid JSON.
Do not use markdown.
Do not wrap the JSON in backticks.

Required schema:
{{
  "timezone": "string or null",
  "platforms": ["string"],
  "games": ["string"],
  "tags": ["string"],
  "playstyle": {{
    "cooperative": true,
    "competitive": false
  }},
  "social": {{
    "wants_long_term": false
  }},
  "personality": {{
    "chill": false
  }},
  "communication": {{
    "mic_ok": false
  }}
}}

If unknown, use null, false, or [].

Intro:
\"\"\"{text}\"\"\"
"""

    return prompt

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

def run_pair(text1, text2):
    p1 = extract_profile(text1)
    p2 = extract_profile(text2)

    features = compute_features(p1, p2)
    score = compute_score(features)

    print("\n--- RESULT ---")
    print("Score:", score)
    print("Features:", features)


# 🔥 TEST DATA (replace later)
text1 = "I like chill co-op games like BG3 and Minecraft. EST timezone."
text2 = "Looking for long term friends, mostly play Helldivers and BG3. EST."

run_pair(text1, text2)