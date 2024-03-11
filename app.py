import streamlit as st

st.set_page_config(page_title="U9", layout="wide")

import data  # noqa: E402

standings = data.get_standings()
games = data.get_games()

# highlighted_teams = st.sidebar.multiselect(
#     "Highlight teams",
#     standings.index.drop_duplicates().sort_values(),
# )

teams = st.sidebar.multiselect(
    "Filter teams",
    standings.index.drop_duplicates().sort_values(),
)
if teams != []:
    games = games[(games["home_team"].isin(teams)) | (games["away_team"].isin(teams))]

dates = st.sidebar.multiselect("Filter dates", games["date"].unique())
if dates != []:
    games = games[games["date"].isin(dates)]


# if highlighted_teams != []:

#     def highlight_teams(team):
#         return "background-color: lightseagreen;" if team in highlighted_teams else None

#     standings = standings.style.map(highlight_teams, subset=["Team"])
#     games = games.style.map(highlight_teams, subset=["home_team", "away_team"])


st.subheader("Standings")
st.dataframe(standings)

st.subheader("Games")
st.write(games)
