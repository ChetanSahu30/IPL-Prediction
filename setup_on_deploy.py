"""
Run this on deployment to ensure data files exist.
Since data files are .gitignored, this checks if they exist,
and if not, creates minimal dummy data for the app to work.
"""
import os
import pandas as pd
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_DIR = os.path.join(BASE_DIR, "data", "db")

# Create directories
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Check if player_stats.csv exists
player_stats_path = os.path.join(RAW_DIR, "player_stats.csv")

if not os.path.exists(player_stats_path):
    print("⚠️ player_stats.csv not found. Creating dummy data...")
    
    # Create minimal dummy player stats
    teams = ["MI", "CSK", "RCB", "KKR", "RR", "GT", "SRH", "DC", "PBKS", "LSG"]
    players = []
    
    for team in teams:
        for i in range(5):
            players.append({
                "season": 2025,
                "player_name": f"{team}_Player_{i+1}",
                "team": team,
                "role": ["Bat", "Bowl", "All"][i % 3],
                "batting_avg": 25.0 + (i * 5),
                "batting_sr": 120.0 + (i * 10),
                "runs_scored": 200 + (i * 50),
                "wickets": 10 + i,
                "bowling_avg": 30.0 - i,
                "economy": 8.0 - (i * 0.5)
            })
    
    df = pd.DataFrame(players)
    df.to_csv(player_stats_path, index=False)
    print(f"✅ Created {player_stats_path}")
else:
    print(f"✅ {player_stats_path} already exists")

print("✅ Setup complete!")
