from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import random

# 🔥 Base strengths
TEAM_BASE_STRENGTH = {
    "MI": 350,
    "CSK": 360,
    "RCB": 340,
    "KKR": 345,
    "RR": 330,
    "GT": 355,
    "SRH": 335,
    "DC": 340,
    "PBKS": 330,
    "LSG": 345
}

app = FastAPI()

# ✅ Load data
df_players = pd.read_csv("data/raw/player_stats.csv")

# ✅ Input model
class MatchInput(BaseModel):
    team1: str
    team2: str
    team1_players: Optional[List[str]] = None
    team2_players: Optional[List[str]] = None


# ✅ Helper function
def calculate_team_strength(team, selected_players):

    team_df = df_players[df_players["team"] == team]

    if selected_players:
        selected_players = [p for p in selected_players if p is not None]

        if selected_players:
            team_df = team_df[team_df["player_name"].isin(selected_players)]

    if team_df.empty:
        return 0

    total_strength = 0

    for _, row in team_df.iterrows():

        role = row["role"]

        batting = row["batting_avg"] if not pd.isna(row["batting_avg"]) else 0
        strike = row["batting_sr"] if not pd.isna(row["batting_sr"]) else 0
        wickets = row["wickets"] if not pd.isna(row["wickets"]) else 0
        economy = row["economy"] if not pd.isna(row["economy"]) else 0

        # 🔥 ROLE BASED LOGIC
        if role == "Bat":
            strength = (batting * 0.5) + (strike * 0.5)

        elif role == "Bowl":
            strength = (wickets * 0.7) - (economy * 0.3)

        else:  # All-rounder
            strength = (
                batting * 0.3 +
                strike * 0.3 +
                wickets * 0.3 -
                economy * 0.1
            )

        total_strength += strength

    return total_strength / len(team_df)

# ✅ API route
@app.post("/predict-match")
def predict_match(data: MatchInput):

    base_team1 = TEAM_BASE_STRENGTH.get(data.team1, 300)
    base_team2 = TEAM_BASE_STRENGTH.get(data.team2, 300)

    # 🔥 FULL TEAM + SELECTED PLAYER MIX (IMPORTANT FIX)
    full1 = calculate_team_strength(data.team1, None)
    sel1 = calculate_team_strength(data.team1, data.team1_players)

    full2 = calculate_team_strength(data.team2, None)
    sel2 = calculate_team_strength(data.team2, data.team2_players)

    team1_strength = base_team1 + (0.7 * full1) + (0.3 * sel1)
    team2_strength = base_team2 + (0.7 * full2) + (0.3 * sel2)

    total = team1_strength + team2_strength

    if total == 0:
        return {"error": "No data available"}

    team1_prob = team1_strength / total
    team2_prob = team2_strength / total

    # 🎲 Probabilistic winner
    winner = data.team1 if random.random() < team1_prob else data.team2

    return {
        "team1": data.team1,
        "team2": data.team2,
        "winner": winner,
        "team1_prob": team1_prob,
        "team2_prob": team2_prob,
        "team1_strength": team1_strength,
        "team2_strength": team2_strength
    }