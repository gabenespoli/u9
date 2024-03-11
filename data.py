import re

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

STANDINGS_URL = "https://alliancehockey.com/Rounds/27668/Recreational_League_2023-2024_TCHL_U9_Regular_Season/"
GAMES_URLS = [
    "https://alliancehockey.com/Groups/1617/Schedule/?Month=1&Year=2024",
    "https://alliancehockey.com/Groups/1617/Schedule/?Month=2&Year=2024",
    "https://alliancehockey.com/Groups/1617/Schedule/?Month=3&Year=2024",
]

DTYPES_STANDINGS = {
    "GP": int,
    "W": int,
    "L": int,
    "T": int,
    "Pts": int,
    "W %": float,
    "GF": int,
    "GA": int,
    "Diff": int,
}


@st.cache_data()
def get_standings(url=STANDINGS_URL):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    standings = soup.find_all("table", attrs={"class": "standings"})[0]
    data = []
    for row in standings.find_all("tr"):
        row_data = []
        for cell in row.find_all("th"):
            row_data.append(cell.text)
        for cell in row.find_all("td"):
            row_data.append(cell.text)
        data.append(row_data)
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.astype(DTYPES_STANDINGS)
    df["GAA"] = (df["GA"] / df["GP"]).round(2)
    return df.set_index("Team")


@st.cache_data()
def get_games(urls=GAMES_URLS):
    data = list()
    for url in urls:
        print(">", end="")
        year = url.split("Year=")[1]
        month = url.split("Month=")[1].split("&")[0]
        month = "0" + month if len(month) == 1 else month
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        games = soup.find_all(
            "div", attrs={"class": ["event-list-item", "hover-function"]}
        )
        for game in games:
            print(".", end="")
            row = dict()
            day_of_month = game.find_all("div", attrs={"class": "day_of_month"})[0].text
            time = game.find_all("div", attrs={"class": "time-primary"})[0].text

            row["date"] = f"{year}-{month}-{day_of_month.split(' ')[1]}"
            row["time"] = re.sub(day_of_month, "", time)
            row["location"] = game.find_all("div", attrs={"class": "location"})[0].text

            score = game.find_all("div", attrs={"class": "game_score"})[0].text
            row["home_team"] = game.find_all("div", attrs={"class": "subject-owner"})[
                0
            ].text
            row["home_score"] = score.split("-")[0] if score != "" else None
            away_team = game.find_all("div", attrs={"class": "subject-text"})[
                0
            ].text.replace("@ ", "")
            row["away_team"] = re.sub("U9.*", "", away_team)
            row["away_score"] = score.split("-")[1] if score != "" else None

            data.append(row)

    return pd.DataFrame(data)


# def get_game_details(urls=GAMES_URLS):
#     for url in urls:
#         soup = BeautifulSoup(requests.get(url).text, "html.parser")
#         events = soup.find_all(
#             "div", attrs={"class": ["event-list-item", "hover-function"]}
#         )
#         for event in events:
#             href = event.find_all(
#                 "a", attrs={"class": ["flex-child-shrink", "text-center"]}
#             )[0]["href"]
#             link = "https://alliancehockey.com" + href
#             game = BeautifulSoup(requests.get(link).text, "html.parser")
