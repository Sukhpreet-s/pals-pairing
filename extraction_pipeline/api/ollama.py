import requests

from ..config import OLLAMA_URL, MODEL


def extract_profile_with_prompt(prompt: str) -> str:
    """Call Ollama LLM API to extract profile information."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
    )
    response.raise_for_status()
    payload = response.json()
    return payload["response"]
