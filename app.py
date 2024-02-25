from data import *

import streamlit as st

st.set_page_config(layout="wide")

PAGES = {
    "Dados por partida": get_general_data,
    "Dados por time": get_team_data_filtered,
    "Dados por champion": get_champion_data,
    "Dados por jogador": get_player_data,
    "Ranking dos champions": get_champion_ranking,
    "Winrate": get_win_rate,
}


st.sidebar.header("Navegação")
selection = st.sidebar.radio("Selecione uma página", list(PAGES.keys()))

page = PAGES[selection]
page.app()
