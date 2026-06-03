# System Architecture — Sports Analytics & Prediction System

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │  HTTP
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              FRONTEND  (Streamlit — app.py)                     │
│  - Team & player selection UI                                   │
│  - Win probability display                                      │
│  - Player impact charts (Plotly)                                │
│  - Prediction history table                                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │  REST API call (POST /predict-match)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND API  (FastAPI — api/main.py)               │
│  - Validates input (Pydantic)                                   │
│  - Calculates role-based player strength                        │
│  - Returns winner, probabilities, team strengths                │
└─────────────────────────┬───────────────────────────────────────┘
                          │  reads
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA LAYER  (SQLite — data/db/ipl.db)              │
│  - matches (1,146 rows)                                         │
│  - player_stats (2,285 rows)                                    │
│  - venues (64 rows)                                             │
│  - head_to_head (603 rows)                                      │
│  - season_stats (156 rows)                                      │
│  - predictions (user predictions history)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ML Pipeline Architecture

```
RAW DATA (IPL.csv 2008-2025)
        │
        ▼
┌───────────────────┐
│  DATA INGESTION   │  src/data/create_dataset.py
│  - Extract matches│  src/data/ingest.py
│  - Extract players│  src/data/preprocess.py
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ FEATURE ENGINEER  │  src/features/engineer.py
│ - Win rates       │  src/features/team_strength.py
│ - Recent form     │  src/features/venue_features.py
│ - H2H records     │
│ - Venue features  │
│ - Player strength │
└────────┬──────────┘
         │  features.csv (1,146 rows × 31 features)
         ▼
┌───────────────────┐
│  MODEL TRAINING   │  src/models/trainer.py
│  - Random Forest  │  src/models/random_forest_model.py
│  - XGBoost        │  src/models/xgboost_model.py
│  - LightGBM       │  src/models/lightgbm_model.py
│  - Neural Network │  src/models/neural_network_model.py
│  - Extra Trees    │  src/models/extra_trees_model.py
│  - Ensemble       │  src/models/ensemble_model.py
└────────┬──────────┘
         │  saved to outputs/models/*.pkl
         ▼
┌───────────────────┐
│  PREDICTION 2026  │  src/prediction/predict_2026.py
│  - Simulate all   │
│    matchups       │
│  - Bayesian update│
│  - Rank teams     │
└────────┬──────────┘
         │
         ▼
   outputs/results/
   prediction_2026.json
   model_results.json
   *.png charts
```

---

## Module Responsibilities

| Module | Responsibility | Key Files |
|--------|---------------|-----------|
| `src/data/` | Data ingestion, cleaning, DB setup | `create_dataset.py`, `db_setup.py`, `ingest.py`, `preprocess.py` |
| `src/features/` | Feature engineering from raw data | `engineer.py`, `team_strength.py`, `venue_features.py` |
| `src/models/` | ML model definitions, training, evaluation | `trainer.py`, `base_model.py`, `ensemble_model.py` |
| `src/prediction/` | 2026 tournament simulation and ranking | `predict_2026.py`, `visualize.py` |
| `api/` | REST API for real-time match prediction | `main.py` |
| `tests/` | Unit tests for all modules | `test_features.py`, `test_models.py` |

---

## Data Flow

```
1. Input:   Historical match data (2008–2025)
2. Process: Feature engineering (30+ features per match)
3. Train:   5 ML models + stacking ensemble
4. Tune:    Optuna hyperparameter optimization (60 trials each)
5. Predict: Simulate all 2026 matchups
6. Output:  Win probabilities + ranked predictions
```

---

## API Contract

### POST /predict-match

**Request:**
```json
{
  "team1": "MI",
  "team2": "CSK",
  "team1_players": ["Rohit Sharma", "Jasprit Bumrah"],
  "team2_players": ["MS Dhoni", "Ravindra Jadeja"]
}
```

**Response:**
```json
{
  "team1": "MI",
  "team2": "CSK",
  "winner": "MI",
  "team1_prob": 0.523,
  "team2_prob": 0.477,
  "team1_strength": 396.1,
  "team2_strength": 362.4
}
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| SQLite over CSV for data storage | Enables proper querying, indexing, relationships |
| Stacking Ensemble over single model | Combines strengths of 5 models, more robust |
| Bayesian smoothing on win rates | Prevents small-sample bias for new teams |
| Walk-forward CV for Optuna | Respects temporal order, prevents data leakage |
| Absolute file paths in production | Prevents path errors across different OS/deployment environments |
| Role-based player strength formula | Domain knowledge: batsmen and bowlers contribute differently |
