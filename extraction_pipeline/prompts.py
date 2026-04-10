from extraction_pipeline.config import PROMPTS_DIR


def load_prompt(prompt_type: str) -> str:
    """Load prompt template from prompts directory."""
    filename = PROMPTS_DIR / f"{prompt_type}_only_prompt.txt"
    with open(filename, "r", encoding="utf-8") as file:
        return file.read().strip()
