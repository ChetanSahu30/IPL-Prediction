import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Paths (absolute so they work both locally and on Render) ────────────────
SQLITE_DB_PATH = os.path.join(BASE_DIR, "data", "db", "ipl.db")
PLAYER_STATS_PATH = os.path.join(BASE_DIR, "data", "raw", "player_stats.csv")

def save_prediction_to_db(team1, team2, winner, team1_prob, team2_prob):
    """Save prediction to database"""
    try:
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create prediction table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team1 TEXT,
                team2 TEXT,
                predicted_winner TEXT,
                team1_probability REAL,
                team2_probability REAL,
                timestamp TEXT
            )
        """)
        
        # Insert prediction
        cur.execute("""
            INSERT INTO predictions (team1, team2, predicted_winner, team1_probability, team2_probability, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (team1, team2, winner, team1_prob, team2_prob, timestamp))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def get_prediction_history():
    """Get all past predictions from database"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        history_df = pd.read_sql("""
            SELECT team1 as 'Team 1', 
                   team2 as 'Team 2', 
                   predicted_winner as 'Winner', 
                   ROUND(team1_probability*100, 1) as 'Team1 %',
                   ROUND(team2_probability*100, 1) as 'Team2 %',
                   timestamp as 'Time'
            FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT 50
        """, conn)
        conn.close()
        return history_df if not history_df.empty else None
    except Exception as e:
        return None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

st.set_page_config(page_title="Sports Analytics & Prediction System", layout="wide")

st.markdown("""
<style>

body {
    min-height: 100vh;
    margin: 0;
    padding: 0;
    background: radial-gradient(circle at top left, rgba(214,45,109,0.18), transparent 20%),
                radial-gradient(circle at top right, rgba(0,198,255,0.15), transparent 18%),
                radial-gradient(circle at bottom left, rgba(68, 192, 255, 0.10), transparent 22%),
                #05070f;
    font-family: 'Poppins', sans-serif;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(90deg,#ff6a00,#ee0979);
    color: white;
    border-radius: 12px;
    padding: 14px 26px;
    font-weight: bold;
    letter-spacing: 0.02em;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 35px rgba(255,105,180,0.25);
}

/* Card */
.card {
    background: rgba(255,255,255,0.06);
    padding: 28px;
    border-radius: 24px;
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.08);
    transition: transform 0.35s ease, box-shadow 0.35s ease;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 30px 80px rgba(0,0,0,0.25);
}

.hero-banner {
    margin: 0 -40px 30px -40px;
    padding: 42px 48px;
    border-radius: 30px;
    background: linear-gradient(180deg, rgba(20,24,37,0.95), rgba(12,15,25,0.88));
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 32px 90px rgba(0,0,0,0.35);
}
.hero-content {
    max-width: 980px;
    margin: 0 auto;
}
.hero-banner h1 {
    margin: 0;
    font-size: clamp(2.8rem, 4vw, 4.2rem);
    letter-spacing: 0.04em;
    color: #ff2d6d;
    line-height: 1.05;
    text-shadow: 0 24px 40px rgba(255,45,109,0.18);
}
.hero-banner p {
    margin: 20px 0 0;
    font-size: 1.05rem;
    color: #d5d8e4;
    max-width: 720px;
    line-height: 1.8;
}
.hero-badges {
    margin-top: 28px;
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    border-radius: 999px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    color: #e8edf8;
    font-size: 0.95rem;
}
.feature-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 18px;
    margin-top: 26px;
}
.feature-card {
    flex: 1;
    min-width: 220px;
    max-width: 280px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 18px 20px;
    box-shadow: 0 18px 40px rgba(0,0,0,0.18);
    color: #f3f6ff;
}
.feature-card strong {
    display: block;
    margin-top: 12px;
    font-size: 1.15rem;
    color: #ffffff;
}
.section-card {
    background: rgba(12, 18, 33, 0.85);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 24px 70px rgba(0,0,0,0.20);
}
.section-card h2 {
    margin-top: 0;
    margin-bottom: 18px;
    color: #ffffff;
}
.team-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.team-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 40px rgba(0,0,0,0.22);
}
.team-label {
    margin-top: 16px;
    font-weight: 700;
    letter-spacing: 0.03em;
}
.vs-box {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    color: #ffffff;
    font-weight: 700;
}

/* Progress */
.stProgress > div > div {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
}

/* Animated gradient title */
.title {
        background: linear-gradient(90deg,#ff6a00,#ee0979,#8e2de2,#00c6ff);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 8s linear infinite;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Floating team logos */
.team-logo {
    border-radius: 12px;
    transition: transform 0.6s ease, box-shadow 0.6s ease;
    animation: floaty 4s ease-in-out infinite;
}
.team-logo:hover { transform: translateY(-8px) scale(1.05); box-shadow: 0 10px 25px rgba(0,0,0,0.4); }
@keyframes floaty {
    0% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
    100% { transform: translateY(0); }
}

/* Card entrance */
.card { opacity: 0; transform: translateY(8px); animation: cardIn 0.6s forwards; }
@keyframes cardIn { to { opacity: 1; transform: translateY(0); } }

/* Animated predict button */
div.stButton > button {
    background: linear-gradient(90deg,#ff6a00,#ee0979);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
    transition: 0.3s;
}
div.stButton > button:active { transform: translateY(2px); }

.hero-banner {
  margin: 0 -40px 30px -40px;
  padding: 40px 40px 30px 40px;
  border-radius: 30px;
  background: rgba(20, 24, 37, 0.78);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 30px 90px rgba(0,0,0,0.35);
  backdrop-filter: blur(18px);
}
.hero-content {
  max-width: 900px;
  margin: 0 auto;
}
.hero-banner h1 {
  margin: 0;
  font-size: 3.2rem;
  letter-spacing: 0.04em;
  color: #ff2d6d;
  text-shadow: 0 15px 40px rgba(255,45,109,0.18);
}
.hero-banner p {
  margin: 16px 0 0;
  font-size: 1.05rem;
  color: #d5d8e4;
  max-width: 780px;
  line-height: 1.8;
}

.section-card {
  background: rgba(12, 18, 33, 0.75);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 22px;
  padding: 18px 20px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.20);
}

.section-card h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #ffffff;
}

.team-logo {
  border-radius: 50%;
  transition: transform 0.6s ease, box-shadow 0.6s ease;
  animation: floaty 4s ease-in-out infinite;
}

</style>
""", unsafe_allow_html=True)

# 📊 Load data (absolute path so it works on Render too)
df_players = pd.read_csv(PLAYER_STATS_PATH)

# 🔥 Player Impact Function
def get_player_impact(team, selected_players):
    team_df = df_players[df_players["team"] == team].copy()

    if selected_players:
        team_df = team_df[team_df["player_name"].isin(selected_players)]

    if team_df.empty:
        return pd.DataFrame()

    team_df["impact"] = (
        team_df["batting_avg"].fillna(0) * 0.3 +
        team_df["batting_sr"].fillna(0) * 0.3 +
        team_df["wickets"].fillna(0) * 0.25 -
        team_df["economy"].fillna(0) * 0.15
    )

    return team_df[["player_name", "impact"]].sort_values(by="impact", ascending=False)

# 📊 Player list
TEAM_PLAYERS = {}
for team in df_players["team"].unique():
    TEAM_PLAYERS[team] = df_players[df_players["team"] == team]["player_name"].unique().tolist()

# 🎨 Team Colors
TEAM_COLORS = {
    "MI": "#004BA0",
    "CSK": "#FFFF00",
    "RCB": "#DA1818",
    "KKR": "#3A225D",
    "RR": "#FF1493",
    "GT": "#1C1C1C",
    "SRH": "#FF822A",
    "DC": "#0078BC",
    "PBKS": "#ED1B24",
    "LSG": "#00AEEF"
}

# Use the backend FastAPI predict endpoint instead of loading a local model file.
# The Streamlit frontend will call this URL when the Predict button is pressed.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict-match")

# Hero section
st.markdown(
    """
    <div class='hero-banner'>
      <div class='hero-content'>
        <h1>Sports Analytics & Prediction System</h1>
        <p>Advanced match forecasting with player impact analysis, live probability insights, and team strength prediction.</p>
        <div class='hero-badges'>
          <div class='hero-badge'>📊 Historical data driven</div>
          <div class='hero-badge'>⚡ Real-time prediction</div>
          <div class='hero-badge'>🔥 Player impact insights</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='feature-row'>
      <div class='feature-card'>
        <span>📊 Predictive analytics</span>
        <strong>Instant match forecasts</strong>
      </div>
      <div class='feature-card'>
        <span>⚡ Smart player insights</span>
        <strong>Team strength analysis</strong>
      </div>
      <div class='feature-card'>
        <span>🔍 Clear probability</span>
        <strong>Easy decision support</strong>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 📐 Layout
left, main, right = st.columns([1, 3, 1])

# 🧠 LEFT
with left:
    st.markdown("## 💡 Tips")
    st.info("Pick impactful players")
    st.info("All-rounders = game changers ⚡")
    st.info("More players → better prediction")

# 📊 RIGHT
with right:
    st.markdown("## 📊 Model Info")
    st.success("Uses batting + bowling stats")
    st.success("Role-based prediction")
    st.success("Probabilistic outcomes 🎲")

# 🎯 MAIN
with main:

    teams = list(TEAM_COLORS.keys())

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("Team 1", teams)

    with col2:
        team2 = st.selectbox("Team 2", teams)

    # VS
    st.markdown('<div class="card">', unsafe_allow_html=True)

    colA, colB, colC = st.columns([1,0.3,1])

    with colA:
        team1_logo = os.path.join(ASSETS_DIR, f"{team1}.png")
        st.image(team1_logo, width=130)
        st.markdown(
            f"<div style='text-align:center;color:{TEAM_COLORS[team1]};font-weight:700;margin-top:8px'>{team1}</div>",
            unsafe_allow_html=True,
        )

    with colB:
        st.markdown("<div class='vs-box'>VS</div>", unsafe_allow_html=True)

    with colC:
        team2_logo = os.path.join(ASSETS_DIR, f"{team2}.png")
        st.image(team2_logo, width=130)
        st.markdown(
            f"<div style='text-align:center;color:{TEAM_COLORS[team2]};font-weight:700;margin-top:8px'>{team2}</div>",
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)
    # Players
    st.markdown("### 👤 Select Players")

    p1, p2 = st.columns(2)

    with p1:
        team1_players = st.multiselect(team1, TEAM_PLAYERS.get(team1, []))

    with p2:
        team2_players = st.multiselect(team2, TEAM_PLAYERS.get(team2, []))

    st.markdown("<br>", unsafe_allow_html=True)

    # Button
    if st.button("🚀 Predict Winner"):

        if team1 == team2:
            st.error("⚠️ Select different teams!")
        else:
            try:
                response = requests.post(API_URL, json={
                    "team1": team1,
                    "team2": team2,
                    "team1_players": team1_players,
                    "team2_players": team2_players
                })

                if response.status_code != 200:
                    st.error("API Error")
                else:
                    result = response.json()
                    
                    # 💾 SAVE TO DATABASE
                    save_prediction_to_db(
                        team1=team1,
                        team2=team2,
                        winner=result["winner"],
                        team1_prob=result["team1_prob"],
                        team2_prob=result["team2_prob"]
                    )

                    winner_color = TEAM_COLORS[result["winner"]]

                    # Winner Card
                    st.markdown(f"""
                    <div class="card" style="
                      background: linear-gradient(135deg, {winner_color}, black);
                      text-align:center;
                      font-size:30px;
                      color:white;
                      font-weight:bold;">
                      🏆 {result['winner']} DOMINATING!
                    </div>
                    """, unsafe_allow_html=True)

                    st.image("https://media.giphy.com/media/l0HlQ7LRalQqdWfao/giphy.gif")

                    if result["team1_prob"] > 0.6 or result["team2_prob"] > 0.6:
                        st.balloons()

                    st.info("⚠️ Prediction is probabilistic")

                    # Probability
                    st.markdown("### 📊 Win Probability")

                    st.progress(result["team1_prob"])
                    st.write(f"{team1}: {result['team1_prob']*100:.1f}%")

                    st.progress(result["team2_prob"])
                    st.write(f"{team2}: {result['team2_prob']*100:.1f}%")

                    # Strength
                    st.markdown("### ⚡ Team Strength")

                    c1, c2 = st.columns(2)
                    c1.metric(team1, f"{result['team1_strength']:.1f}")
                    c2.metric(team2, f"{result['team2_strength']:.1f}")

                    # Insight
                    st.markdown("### 🔍 AI Insight")

                    if result["team1_prob"] > result["team2_prob"]:
                        st.success(f"{team1} stronger")
                    else:
                        st.success(f"{team2} stronger")

                    # 🔥 PLAYER IMPACT GRAPH (FINAL CLEAN FIX)
                    st.markdown("### 🔥 Player Impact Analysis")

                    impact1 = get_player_impact(team1, team1_players)
                    impact2 = get_player_impact(team2, team2_players)

                    g1, g2 = st.columns(2)

                    # TEAM 1
                    with g1:
                      st.markdown(f"#### {team1}")

                      if not impact1.empty:
                        fig1 = px.bar(
                          impact1,
                          x="player_name",
                          y="impact",
                          title=f"{team1} Player Impact",
                          color="impact"
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                      else:
                        st.warning("No data for Team 1")

                    # TEAM 2
                    with g2:
                      st.markdown(f"#### {team2}")

                      if not impact2.empty:
                        fig2 = px.bar(
                          impact2,
                          x="player_name",
                          y="impact",
                          title=f"{team2} Player Impact",
                          color="impact"
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                      else:
                        st.warning("No data for Team 2") 
                      g1, g2 = st.columns(2)

                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 📜 SHOW PREDICTION HISTORY FROM DATABASE
# ============================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("## 📜 Prediction History")

history = get_prediction_history()
if history is not None and not history.empty:
    st.dataframe(history, use_container_width=True)
else:
    st.info("No predictions yet. Click 'Predict Winner' above to start!")
