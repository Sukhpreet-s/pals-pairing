import requests

from ..config import OLLAMA_URL, MODEL


def extract_profile_with_prompt(prompt: str, model: str = MODEL, ollama_url: str = OLLAMA_URL) -> str:
    """Call Ollama LLM API to extract profile information."""
    response = requests.post(
        ollama_url,
        json={"model": model, "prompt": prompt, "stream": False},
    )
    response.raise_for_status()
    payload = response.json()
    return payload["response"]
