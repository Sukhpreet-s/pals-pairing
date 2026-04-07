### Extraction data from free-form text

Later: 
- Do feature extraction from whole dataset using llm

#### hard constraints
- timezone 
- platform 
- voice chat compatibility
- communication preferences
- availability 
- age boundary preferences
- co-op vs PvP
- 1-on-1 vs group preference
- personality cues

[!Note] Some of these constraints will also be extracted from title and tags.

#### Match/overlap features
- shared games
- shared genres
- same platform
- timezone proximity
- same communication preferences
- both long-term / both casual

#### Complementarity features
- shy + welcoming
- anxious + patient
- socially passive + socially initiating
- broad game flexibility + niche preferences
- low skill + “new players welcome”

#### Friction / constraint features
- severe timezone gap
- no cross-platform route
- competitive vs anti-competitive
- 1-on-1 preference vs discomfort with 1-on-1
- mic required vs no mic
- fast-paced shooter preference vs cozy-only preference
- age preference mismatch
- emotional intensity mismatch



#### Games extraction and stance extraction

Two step process:
1. Identify entity names (games, genres)
2. Label stance for each game and genre