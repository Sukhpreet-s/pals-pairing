# Copilot Instructions for pals-pairing

## Project Overview

**pals-pairing** is a gamer compatibility system that matches gamers based on their preferences extracted from free-form Discord introduction posts. It combines LLM-based extraction with transparent, configurable scoring logic.

The system consists of two main pipelines:
1. **Extraction Pipeline**: Uses a local LLM (Ollama with configurable model) and five specialized prompts to extract structured JSON from intro posts, flattening results to CSV.
2. **Scoring Pipeline**: Loads extracted profiles, normalizes them into `UserProfile` objects, and computes pairwise compatibility scores across five domains (games, genres, playstyle, social, personality).

## Running the Project

### Setup
```bash
pip install -r requirements.txt
```

No additional build or compilation steps are required—the project is pure Python.

### Running Pipelines

**Extract profiles** (requires Ollama running locally on port 11434):
```bash
python3 main.py extract --input-file prompt_data.csv --output-file profile_extraction_output.csv --limit 3
```
- `--limit`: Maximum number of records to process (default: 3)

**Score extracted profiles**:
```bash
python3 main.py score --input-file profile_extraction_output.csv --output-file pair_overlap_output.csv
```

### Testing & Linting

No existing test suite or linting tools are configured. Code follows implicit conventions (see below).

## High-Level Architecture

### Data Flow

```
input CSV (id, introduction content)
    ↓
[Extraction Pipeline]
  ├─ Load intro posts
  ├─ Send to Ollama (5 specialized prompts)
  ├─ Clean JSON responses (strip code fences, handle errors)
  ├─ Flatten into CSV columns
    ↓
    profile_extraction_output.csv
    ↓
[Scoring Pipeline]
  ├─ Load & normalize profiles → UserProfile objects
  ├─ Compute pairwise domain scores (games, genres, playstyle, social, personality)
  ├─ Aggregate domain scores into final compatibility score
    ↓
    pair_overlap_output.csv
```

### Key Modules

**extraction_pipeline/**
- `pipeline.py`: Orchestrates multi-prompt extraction for each record.
- `api/ollama.py`: HTTP client to local Ollama `/api/generate` endpoint.
- `parsers/`: JSON cleaning, parsing, and flattening per prompt type.
- `io/`: CSV I/O helpers (`load_source_records`, `write_profile_rows`).
- `config.py`: Model selection, prompt types, CSV field names.
- `prompts.py`: Loads `.txt` prompt templates from `prompts/` directory.

**overlap_system/**
- `models.py`: `UserProfile` and result TypedDicts.
- `normalizers.py`: CSV → Python type conversion (`normalize_pipe_list`, `normalize_bool`, `normalize_user_profile`).
- `scorers/`: Domain-specific scoring functions (games, genres, playstyle, social, personality).
  - Each takes two `UserProfile`s and returns a float score.
  - `aggregate.py`: combines domain scores using `DOMAIN_WEIGHTS`.
- `pipeline.py`: Loads CSV, normalizes, computes all pairwise overlaps.
- `config.py`: Tunable weights for domains and sub-domains.

**prompts/** directory
- Five `.txt` templates: `games_only_prompt.txt`, `genres_only_prompt.txt`, `playstyle_only_prompt.txt`, `social_only_prompt.txt`, `personality_only_prompt.txt`.
- Each defines a strict JSON schema; the LLM is instructed not to infer or hallucinate.

### Configuration & Scoring Weights

All weights are in `config.py` files under each module:

**Domain Weights** (`overlap_system/config.py` → `DOMAIN_WEIGHTS`):
```python
games: 0.40, genres: 0.20, playstyle: 0.15, social: 0.15, personality: 0.10
```

**Per-Domain Weights** (e.g., `overlap_system/config.py` → `GAME_WEIGHTS`):
- Games: `strong_overlap` (1.0), `soft_overlap` (0.5), `historical_overlap` (0.25), `conflict` (-1.0).
- Genres: `liked_overlap` (0.8), `soft_overlap` (0.4), `dislike_conflict` (-0.8), `avoid_conflict` (-1.0).
- Playstyle, social, personality: weight individual boolean/categorical flags.

All weights are configurable and can be tuned for different prioritization strategies.

## Code Conventions

### Data Structures

- **UserProfile** (TypedDict): Core data model with 22 typed fields.
  - Game/genre fields: `set[str]` (pipe-separated in CSV, normalized to sets).
  - Playstyle/social/personality: `bool | None` (tri-state: true, false, or unknown).
  - Special: `genres_metadata` preserves original JSON for future analysis.

- **Result types**: `PairOverlapResult` and `AggregateOverlapResult` hold scores and `raw_features` dicts for debugging/explanation.

### CSV & Normalization

- CSV pipe-list format: `"game1|game2|game3"` → normalized to `{"game1", "game2", "game3"}` (lowercase).
- Boolean format: `"true"`, `"false"`, `"null"` strings → `True | False | None`.
- Energy level normalization: arbitrary strings → `"low" | "medium" | "high" | None` via `ENERGY_MAP`.
- Graceful degradation: JSON parsing errors fall back to empty sets/None values; pipelines never crash.

### Extraction & Parsing

- **Prompt templates**: Stored as `.txt` files in `prompts/`; loaded dynamically.
- **JSON cleaning**: Strips Markdown code fences (`\`\`\`json ... \`\`\``) using regex before parsing.
- **Per-prompt flattening**: Each `flatten_*` function knows the schema for its prompt type and converts JSON → CSV columns.
- **Error handling**: If a prompt returns unparseable JSON, `default_values_for_prompt` returns safe defaults so scoring continues.

### Scoring Pattern

Each domain scorer follows the same pattern:
1. Extract relevant fields from two `UserProfile`s.
2. Compute overlap, soft overlap, and conflict signals.
3. Multiply by weights from `config.py`.
4. Aggregate into a single float score (typically 0.0–1.0, can be negative with conflicts).
5. Include intermediate features in `raw_features_json` for debugging.

## Important Notes

- **Ollama Integration**: Extraction requires a local Ollama server on `localhost:11434`. Model is configurable in `extraction_pipeline/config.py` (currently `Qwen3-4B-Instruct`).
- **No Training**: The scoring logic is deterministic and rule-based—no ML training, only LLM extraction.
- **Transparency**: All scoring is explicit and weights are configurable, enabling experimentation and debugging.
- **Game Name Normalization**: Currently relies on exact string matching; no alias detection. Future work includes IGDB database integration for canonicalization.

## Future Extensibility

New domains or fields can be added by:
1. Extending `UserProfile` in `overlap_system/models.py`.
2. Adding a new prompt in `prompts/`.
3. Creating a new scorer in `overlap_system/scorers/`.
4. Adding weights in `overlap_system/config.py` (both domain and per-field).
5. Updating `extraction_pipeline/config.py` `PROFILE_FIELDNAMES` and prompt types.
