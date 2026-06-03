# Sports Analytics & Prediction System

A full-stack machine learning system for predicting sports match outcomes and tournament winners using historical performance data, feature engineering, and ensemble learning.

> Applied to cricket tournament data (2008–2025), covering 1,146 matches across 17 seasons.

---

## Live Demo

| Service | URL |
|---------|-----|
| Frontend (Streamlit) | https://ipl-prediction-1-hwmo.onrender.com |
| Backend API (FastAPI) | https://ipl-prediction-yahb.onrender.com |

---

## Features

- **Match Prediction** — predict winner and win probability for any two teams
- **Player Impact Analysis** — role-based strength scoring for selected players
- **Tournament Simulation** — simulate all round-robin matchups for season ranking
- **Prediction History** — all predictions stored and displayed from SQLite database
- **Interactive UI** — team logos, probability bars, player impact charts

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Plotly |
| Backend API | FastAPI, Uvicorn, Pydantic |
| ML Models | Scikit-learn, XGBoost, LightGBM |
| Hyperparameter Tuning | Optuna |
| Model Explainability | SHAP |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Deployment | Render |
| Version Control | Git + GitHub |

---

## ML Models

| Model | Test Accuracy | AUC-ROC |
|-------|--------------|---------|
| Random Forest | 67.1% | 0.699 |
| XGBoost | 65.3% | 0.711 |
| LightGBM | 66.0% | 0.713 |
| Neural Network | 60.4% | 0.614 |
| Extra Trees | 65.1% | 0.708 |
| **Stacking Ensemble** | **64.9%** | **0.705** |

---

## Project Structure

```
sports-analytics/
├── config.py                  # Central configuration (paths, constants, model params)
├── main.py                    # CLI pipeline runner (setup/train/predict/visualize)
├── app.py                     # Streamlit frontend
├── Procfile                   # Render deployment config
├── requirements.txt           # Python dependencies
├── ARCHITECTURE.md            # System design documentation
│
├── api/
│   └── main.py                # FastAPI backend — /predict-match endpoint
│
├── src/
│   ├── data/
│   │   ├── create_dataset.py  # Extract matches and player stats from raw data
│   │   ├── db_setup.py        # SQLite schema creation
│   │   ├── ingest.py          # Load CSVs into database
│   │   └── preprocess.py      # Clean and normalize match data
│   │
│   ├── features/
│   │   ├── engineer.py        # 30+ feature calculations per match
│   │   ├── team_strength.py   # Batting/bowling strength from player stats
│   │   └── venue_features.py  # Venue-level pitch and toss features
│   │
│   ├── models/
│   │   ├── base_model.py      # Abstract base class for all models
│   │   ├── trainer.py         # Training orchestrator
│   │   ├── ensemble_model.py  # Stacking ensemble
│   │   ├── tune.py            # Optuna hyperparameter optimization
│   │   └── shap_explainer.py  # Feature importance via SHAP
│   │
│   └── prediction/
│       ├── predict_2026.py    # Tournament simulation + Bayesian ranking
│       └── visualize.py       # Chart generation
│
├── tests/
│   ├── test_features.py       # Unit tests for feature engineering
│   ├── test_models.py         # Unit tests for ML model interfaces
│   ├── test_data.py           # Unit tests for data pipeline
│   └── test_prediction.py     # Unit tests for prediction logic
│
├── data/
│   ├── raw/                   # matches.csv, player_stats.csv, teams.json
│   ├── processed/             # features.csv, matches_processed.csv
│   └── db/                    # ipl.db (SQLite)
│
├── outputs/
│   ├── models/                # Trained model .pkl files
│   └── results/               # Predictions JSON, charts PNG
│
└── assets/                    # Team logo images
```

---

## Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/ChetanSahu30/IPL-Prediction.git
cd IPL-Prediction
pip install -r requirements.txt
```

---

## Running the Project

### Option 1: Full ML Pipeline

```bash
# Step by step
python main.py --mode setup       # ingest data, build features
python main.py --mode train       # train all 5 models + ensemble
python main.py --mode predict     # generate 2026 predictions
python main.py --mode visualize   # generate charts

# Or all at once
python main.py --mode all
```

### Option 2: Web Application (2 terminals)

**Terminal 1 — Backend API:**
```bash
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
python -m streamlit run app.py
```

Open: `http://localhost:8501`

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for full system design, data flow diagrams, and API contract.

---

## Feature Engineering

30+ features engineered per match with **no data leakage** (only past data used for each match):

- Win rates (all-time, last 3 seasons) with Bayesian smoothing
- Recent form (last 5 matches)
- Head-to-head records (last 3 seasons)
- Venue-specific win rates
- Home ground advantage
- Toss impact per venue
- Team batting/bowling strength from player statistics
- Difference features for all pairwise metrics

---

## Prediction Methodology (2026)

Final ranking combines ML output with domain priors via Bayesian weighting:

```
Final Score = 35% Squad Strength
            + 30% Recent Form (2023–2025)
            + 30% ML Ensemble Output
            +  5% Playoff Appearance Rate
```

---

## API Reference

### POST /predict-match

Predicts match outcome given two teams and optional player selections.

**Request body:**
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
  "winner": "MI",
  "team1_prob": 0.523,
  "team2_prob": 0.477,
  "team1_strength": 396.1,
  "team2_strength": 362.4
}
```

---

## Database Schema

| Table | Rows | Description |
|-------|------|-------------|
| matches | 1,146 | Historical match results |
| player_stats | 2,285 | Per-season player statistics |
| venues | 64 | Stadium information |
| head_to_head | 603 | Team vs team records |
| season_stats | 156 | Per-season team standings |
| teams | 15 | Franchise information |
| predictions | dynamic | User prediction history |

---

## Author

Chetan Sahu
