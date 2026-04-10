# Gamer Compatibility System — Technical Report

## 1. Problem Description

#### 1.1 Overview

This project addresses the problem of matching gamers based on rich, free‑form introduction posts rather than simple checklists or single‑dimension tags. The source data comes from the GamerPals Discord community, where users introduce themselves in open‑ended messages that mention games, genres, playstyle, social expectations, and personality traits.

The core goal is to build a system that:
- extracts structured preference data from free‑form intros
- computes a compatibility score between pairs of users
- exposes domain‑level scores (games, genres, playstyle, social, personality) that can later be used for explanations and UI

#### 1.2 Why This Problem is Interesting

There are various different aspects that make gamers compatible or incompatible with others. Some of them are hard rules while other soft rules still contributing to the compatibility. These rules can be:
- List of liked and disliked games/genres 
- Playstyle alignment
- Social expectations
- Personality fit
- Flexibility and tolerance

For example:
- two competitive players may work
- a chill + competitive player may not work
- a shy player + welcoming player may work 

The format of this community allows users to introduce themselves using free-form text which allows users to express these preferences.

With availability of this data, I wanted to explore the idea and potential solutions.

#### 1.3 Potential Impact

A robust compatibility system could:
- improve new user experiences
- improve new user retention
- enable automated friend/group formation
- be extended to other domains:
    - team formation
    - co-op partner recommendations

Once fully working, this would help multiple people in gaming communities to improve their experience in finding others to enjoy playing games.
## 2. Previous Work

#### 2.1 In gaming communities

The previous approaches to improve new user experience in gaming communities are based on users to provide their games preference only. This is usually done by allowing users to select list of games from the available games.  

#### 2.2 In other industries

There are lots of recommendation systems in other industries like movies (netflix), work placements, dating which also uses hybrid systems. These include user-item and user-user recommendation systems.

## 3. Solutions Explored

#### 3.1 Initial Approach: Pure Similarity System

For starting, I made an attempt to use sentence similarity models like `BERT`/`SBERT` to:
1. convert entire intro posts into a single vector embedding, 
2. then compute similarity score using cosine similarity between vectors.

Issues encountered with this approach:
1. Each intro post contains highly dense information. Even a single sentence contain data for different aspects. This made it difficult to analyse the results
2. Existing models are not domain specific and require labelled pair of intros. Labelling these posts is another challenge which can be explored more.

**Below is an example of computing similarity score for parts of 3 different posts which mention about their preference towards a game:**
```python
specific_games = [
	"I tried CS 2 and I didn't like it",
	"I am looking for other CS 2 players",
	"need other Couter Strike 2 gamers"
]
```
Output:
```python
tensor([[1.0000, 0.5440, 0.3579],
        [0.5440, 1.0000, 0.6345],
        [0.3579, 0.6345, 1.0000]])
```

**What the matrix represents:**
Each row is a comparison of the post at row's index positions (1st row = 1st post) with all the other posts (2nd column = 2nd post)

**Note about this data:**
- It works well for basic matching (similar to bag of words model)
- Lacks awareness about abbreviated game names: 1st and 2nd get score of `0.54` when 1st and 3rd get score of `0.35`. These should have similar score
- Missed context about not liking the game mentioned by 1st user led to having a unexpected high score of `0.5` for 1st and 2nd post.
- Unnecessary words like "I", "am" can contribute to the score.

### 3.2 Final Solution: Extraction + Structured Scoring

The final design is a two‑stage hybrid system:

1. **Extraction pipeline (LLM‑based)**
    - Takes free‑form intro posts as input.
    - Uses a local LLM (Ollama with `qwen2.5:3b`) and five specialized prompts to extract structured JSON for games, genres, playstyle, social preferences, and personality.
    - Normalizes and flattens the JSON responses into a single CSV per user, where each column corresponds to a field in the `UserProfile` schema.
    
2. **Scoring pipeline (deterministic)**
    - Loads the extracted CSV rows and normalizes them into typed `UserProfile` objects (sets and booleans) using `normalize_user_profile`.
    - Computes per‑domain scores via explicit scoring functions (games, genres, playstyle, social, personality) and aggregates them into a single overall compatibility score using configurable weights.

This design keeps the LLM responsibilities limited to extraction and leaves the scoring logic transparent and individually tuneable per domain.

## 4. Current Implementation
#### 4.1 Data Model

The core data structure for a user is the `UserProfile` TypedDict in `models.py`, which contains:
- Game preferences: sets of strings for `games_currently_plays`, `games_likes`, `games_dislikes`, `games_used_to_play`, `games_open_to_try`, `games_wants_to_play`.
- Genre preferences: sets of strings for `genres_likes`, `genres_dislikes`, `genres_avoids`, `genres_open_to_try`, `genres_unknown`, plus a `genres_metadata` list of dicts to retain the original genre JSON.
- Playstyle preferences: optional booleans for `playstyle_cooperative`, `playstyle_competitive`, `playstyle_casual_chill`.
- Social expectations: optional booleans for `social_wants_long_term`, `social_wants_group`, `social_open_to_chat`.
- Personality: optional booleans and categorical values for `personality_chill`, `personality_energy_level`, and `personality_introverted`.

Two additional TypedDicts represent scoring outputs: `PairOverlapResult` for pairwise overlap between two users and `AggregateOverlapResult` for higher‑level aggregations.

#### 4.2 Multi-Prompt Extraction Pipeline

The extraction step is implemented in `extraction_pipeline.py` and operates in three phases: reading source posts, sending prompts to the LLM, and flattening responses to CSV.

1. **Source loading**: `load_source_records` reads the input CSV (e.g., `prompt_data.csv`) and pulls the `id` and intro text for each row, up to a configurable limit.[^2]
2. **Prompting**: for each intro and each prompt type (`games`, `genres`, `playstyle`, `social`, `personality`), `process_record` loads the corresponding prompt template from the `prompts` directory, fills `{USER_TEXT}`, and calls the Ollama HTTP endpoint (`/api/generate`) with the `qwen2.5:3b` model.[^6][^2]
3. **JSON cleaning and flattening**:
   - `clean_json_output` strips code fences and extracts the JSON object from the LLM output using regular expressions.[^2]
   - Dedicated `flatten_*` functions (e.g., `flatten_games`, `flatten_genres`, `flatten_playstyle`, `flatten_social`, `flatten_personality`) convert each JSON structure into columns in the CSV.
   - The pipeline writes the final rows to `profile_extraction_output.csv` with a fixed set of headers defined in `PROFILE_FIELDNAMES`.[^2]

The prompt templates, such as `games_only_prompt.txt`, strictly define the allowed JSON schema and instruct the model not to hallucinate extra content or infer games not mentioned explicitly.[^6]

### 4.3 Normalization Layer

The normalization logic in `normalizers.py` converts raw CSV strings into the structured `UserProfile` format for downstream scoring.

Key functions:
- `normalize_pipe_list`: converts `"a|b|c"` into a lower‑cased set `{"a", "b", "c"}`, handling empty or null inputs gracefully.
- `normalize_bool`: accepts booleans or strings like "true", "false", "null" and returns a `bool | None`.
- `normalize_energy_level`: maps arbitrary string variants to standardized energy levels via `ENERGY_MAP` (e.g., low, medium, high, or None).
- `normalize_genres_metadata`: parses the JSON string in the `genres_metadata` column into a list of dictionaries, or returns an empty list on parse errors.

`normalize_user_profile` is the main entrypoint that takes a mapping (e.g., a CSV row) and returns a `UserProfile` with all fields properly typed.

Utility helpers like `sorted_list` in `utils.py` make it easier to present set contents deterministically when needed.

### 4.4 Scoring Logic

The scoring logic lives under the `overlap_system` package (referenced in `main.py` and `pipeline.py`) and is driven by configuration weights from `config.py`.

At the domain aggregation level, the overall overlap score is computed as:
$$
\begin{align}  
\text{overall\_overlap} &= 0.40 \times \text{games} \\  
&\quad + 0.20 \times \text{genres} \\  
&\quad + 0.15 \times \text{playstyle} \\  
&\quad + 0.15 \times \text{social} \\  
&\quad + 0.10 \times \text{personality}  
\end{align}
$$
with these weights stored in `DOMAIN_WEIGHTS`.

Each domain has its own scoring function (e.g., `score_games`, `score_genres`, `score_playstyle`, `score_social`, `score_personality`) that operates on two `UserProfile`s:
- **Games**: builds sets of `positive_games` (`currently_plays` $\cup$ `likes`), `soft_games` (`open_to_try` $\cup$ `wants_to_play`), `historical_games` (`used_to_play`), and `negative_games` (`dislikes`). It then computes overlap features such as shared strong games, soft overlaps, shared historical games, and conflicts, and aggregates them into a score using `GAME_WEIGHTS`.
- **Genres**: uses a similar approach but with genre sets and separate weights for liked overlap, soft overlap, and negative conflicts (dislikes and avoids) stored in `GENRE_WEIGHTS`.
- **Playstyle, social, and personality**: treat each boolean or categorical field as a signal, applying weights in `PLAYSTYLE_WEIGHTS`, `SOCIAL_WEIGHTS`, and `PERSONALITY_WEIGHTS` to reward aligned preferences and penalize mismatches where appropriate.

The `score_pair` function in `overlap_system/pipeline.py` is the main scoring entrypoint: it normalizes two rows into `UserProfile`s and passes them into the aggregate `score_overlap` function.

### 4.5 End‑to‑End Pipelines and CLI

`main.py` provides a simple command‑line interface to run the extraction and scoring pipelines:

- `run_extraction_pipeline`: calls `extract_profiles_pipeline` with an input file, output file, and limit, orchestrating multi‑prompt extraction for the first N intro posts.
- `run_scoring_pipeline`: loads the extracted profiles and calls `score_profiles_pipeline`, which computes all pairwise overlaps between users and writes them into `pair_overlap_output.csv`.

`build_parser` defines two subcommands:

- `extract`: `python main.py extract --input-file prompt_data.csv --output-file profile_extraction_output.csv --limit 3`
- `score`: `python main.py score --input-file profile_extraction_output.csv --output-file pair_overlap_output.csv`

This separation makes it easy to run extraction once (which is LLM‑heavy) and then iterate on scoring logic or weights without re‑calling the LLM.

## 5. Code and Data Explanation

### 5.1 Input Data

The pipeline expects an input CSV containing at least an `id` column and an `introduction content` column (as used in `load_source_records`). Each row corresponds to a single Discord intro post from the GamerPals community, which typically contains several sentences about games played, preferred genres, playstyle, social habits, and personality.

During experimentation, a subset of posts (for example, the first three) is used to keep extraction runtime manageable while still producing multiple pairs for scoring.

### 5.2 Extracted Profiles

The extraction pipeline outputs a CSV `profile_extraction_output.csv` with the following fields (among others):

- `post_id`: original user/post identifier.
- Game columns: `games_currently_plays`, `games_likes`, `games_dislikes`, `games_used_to_play`, `games_open_to_try`, `games_wants_to_play`.
- Genre columns: `genres_likes`, `genres_dislikes`, `genres_avoids`, `genres_open_to_try`, `genres_unknown`, `genres_metadata`.
- Playstyle columns: `playstyle_cooperative`, `playstyle_competitive`, `playstyle_casual_chill`.
- Social columns: `social_wants_long_term`, `social_wants_group`, `social_open_to_chat`.
- Personality columns: `personality_chill`, `personality_energy_level`, `personality_introverted`.

Raw values are strings (e.g., pipe‑separated lists or textual booleans) which are then normalized into structured `UserProfile` objects.

### 5.3 Scored Pairwise Output

The scoring pipeline writes a `pair_overlap_output.csv` that contains one row per user pair, with columns:

- `user_a_id`, `user_b_id`: identifiers for the two matched users.
- `overall_overlap_score`: final compatibility score after domain aggregation.
- `games_score`, `genres_score`, `playstyle_score`, `social_score`, `personality_score`: per‑domain scores.
- `raw_features_json`: a JSON dump of intermediate features, useful for debugging and explaining why two users scored the way they did.

This format makes it straightforward to build downstream applications: for example, a web UI could show a compatibility score, a breakdown by domain, and a human‑readable explanation derived from the `raw_features_json` fields.

## 6. Results and Observations

### 6.1 Qualitative Evaluation of Extraction

On the sampled intro posts, the multi‑prompt extraction generally succeeds at:

- Identifying explicitly mentioned games and assigning them to the correct stance (currently plays, likes, dislikes, etc.) as constrained by `games_only_prompt.txt`.
- Capturing genre information and preserving the full genre JSON in `genres_metadata`, enabling future fine‑grained analysis.
- Translating textual descriptions of playstyle and social expectations into boolean flags (e.g., `cooperative`, `open_to_chat`).

When JSON parsing errors occur (e.g., due to unexpected LLM output), the pipeline falls back to default values for the corresponding prompt type so that downstream scoring remains robust and does not crash.

### 6.2 Qualitative Evaluation of Scoring

Even with a small dataset, the scoring pipeline produces outputs that align with intuition:

- Pairs that share several strongly liked or currently played games receive high `games_score` values, especially when there are no conflicts in disliked games.
- Pairs that align in social expectations (e.g., both want long‑term groups and are open to chat) and personality (e.g., both chill, similar energy levels) see their overall overlap score boosted by the `social` and `personality` domain weights.
- Pairs with conflicting signals (e.g., one user strongly dislikes a game that the other loves) receive negative contributions in the corresponding domain, decreasing their overall compatibility.

Because the domain weights are configurable, it is possible to experiment with different emphasis.

### 6.3 Limitations

Several limitations remain:

- Normalization of game and genre names: the scoring algorithm is not able to detect if a game name is an alias name.
- LLM extraction quality: the system relies on a single local LLM; different models or prompts might extract slightly different structures, and there is no human‑labelled ground truth for automatic scoring. 

Addressing these limitations would involve doing more analysis on the free-form data using different techniques like feature engineering, implementing hard check pipelines using a game database like IGDB, designing a labelling protocol for human compatibility judgments, and possibly training or fine‑tuning models on domain‑specific text. However, the current implementation already demonstrates that a multi‑prompt LLM extraction pipeline combined with a transparent, configurable scoring layer is a practical way to operationalize gamer compatibility.

## 7. Conclusion and Future Work

This project implemented a hybrid gamer compatibility system that:

- extracts structured preference data from free‑form GamerPals intro posts using five specialized LLM prompts
- normalizes the extracted data into a typed `UserProfile` schema
- computes per‑domain and overall compatibility scores via explicit, weighted scoring functions.

Compared to pure embedding‑based similarity, the system provides more interpretable scores and a clear path to explanations, because each domain (games, genres, playstyle, social, personality) is scored separately with transparent rules. The solution is also extensible: new fields or domains can be added to the `UserProfile`, extraction prompts, and scoring configuration without changing the overall architecture.

Future work focuses on:

- Setting up a hard check pipeline using IGDB games database to normalize the game and genre names extracted by LLM.
- Analysing the free-form text in depth to improve the features that affect the scoring the most. 
- Integrating this with the Discord bot and allowing users to provide a feedback on a successful or unsuccessful pairing using this algorithm.
- Using existing friends network to extract labelled set of positive pair and use that labelled pair to implement a machine learning model like a decision tree.