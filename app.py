import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.markdown("""
<style>

body {
    background-color: #0e1117;
    font-family: 'Poppins', sans-serif;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(90deg,#ff6a00,#ee0979);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
    transition: 0.3s;
}
div.stButton > button:hover {
    transform: scale(1.08);
    box-shadow: 0px 0px 15px rgba(255,105,180,0.6);
}

/* Card */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-5px);
}

/* Title */
.title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg,#ff6a00,#ee0979);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Progress */
.stProgress > div > div {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
}

</style>
""", unsafe_allow_html=True)

# 📊 Load data
df_players = pd.read_csv("data/raw/player_stats.csv")

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

# 🎨 Config
st.set_page_config(page_title="IPL Predictor", layout="wide")

API_URL = "http://127.0.0.1:8000/predict-match"

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

    st.markdown('<div class="title">🏏 IPL AI Predictor</div>', unsafe_allow_html=True)
    teams = list(TEAM_COLORS.keys())

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("Team 1", teams)

    with col2:
        team2 = st.selectbox("Team 2", teams)

    # VS
    st.markdown('<div class="card">', unsafe_allow_html=True)

    colA, colB, colC = st.columns([1,0.5,1])

    with colA:
      st.image(f"assets/{team1}.png", width=120)
      st.markdown(f"<h4 style='text-align:center;color:{TEAM_COLORS[team1]}'>{team1}</h4>", unsafe_allow_html=True)

    with colB:
      st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)

    with colC:
      st.image(f"assets/{team2}.png", width=120)
      st.markdown(f"<h4 style='text-align:center;color:{TEAM_COLORS[team2]}'>{team2}</h4>", unsafe_allow_html=True)

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

                    
            except Exception as e:
                st.error(f"Error: {e}")