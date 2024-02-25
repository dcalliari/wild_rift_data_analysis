from data.imports import st
from data.utils import GameData

gd = GameData()


# Site
def app():

    df = gd.process_game_data()

    # CALCULANDO OURO POR TEMPO DE JOGO
    df["Gold5"] = df["totalGolds0"].sub(
        df.groupby(["ID", "positionPlayed"])["totalGolds0"].transform("mean")
    )
    df["Gold10"] = df["totalGolds1"].sub(
        df.groupby(["ID", "positionPlayed"])["totalGolds1"].transform("mean")
    )
    df["Gold15"] = df["totalGolds2"].sub(
        df.groupby(["ID", "positionPlayed"])["totalGolds2"].transform("mean")
    )

    # CALCULANDO OURO POR ID E POSIÇÃO
    df["AGold5"] = df["totalGolds0"].sub(
        df.groupby(["ID", "positionPlayed"])["totalGolds0"].transform("sum")
    )
    df["AGold10"] = df["totalGolds1"].sub(
        df.groupby(["ID", "positionPlayed"])["totalGolds1"].transform("sum")
    )
    df["AGold15"] = df["totalGolds2"].sub(
        df.groupby(["ID", "positionPlayed"])["totalGolds2"].transform("sum")
    )

    # CALCULANDO DIFF GOLD
    df["diffGold5"] = df["totalGolds0"] + df["AGold5"]
    df["diffGold10"] = df["totalGolds1"] + df["AGold10"]
    df["diffGold15"] = df["totalGolds2"] + df["AGold15"]

    # CALCULANDO SE A DIFERENÇA É POSITIVA OU NEGATIVA
    df["%WR gold5"] = df["diffGold5"].apply(lambda x: 1 if x > 0 else 0)
    df["%WR gold10"] = df["diffGold10"].apply(lambda x: 1 if x > 0 else 0)
    df["%WR gold15"] = df["diffGold15"].apply(lambda x: 1 if x > 0 else 0)

    # RENOMEANDO COLUNAS GRANDES
    df = df.rename(
        columns={
            "totalDamageDealtToChampions": "damageDealt",
            "killParticipationRate": "KPR",
        }
    )

    # CALCULANDO DANO POR GOLD
    df["DDPG"] = df["damageDealt"] / df["totalGolds3"]

    # agrupar ouro por player: id do jogo e lado jogado
    df["totalGold%"] = (
        df["totalGolds3"] / df.groupby(["ID", "side"])["totalGolds3"].transform("sum")
    ) * 100

    # agrupar dano por player: id do jogo e lado jogado
    df["damageDealt%"] = (
        df["damageDealt"] / df.groupby(["ID", "side"])["damageDealt"].transform("sum")
    ) * 100

    # -------------------------------------------------
    # ------------------FILTRANDO DADOS----------------
    # -------------------------------------------------
    # filtro_data - https://www.samproell.io/posts/datascience/adhoc-data-filters-streamlit/
    # https://discuss.streamlit.io/t/filtering-data-with-pandas/20724/2

    st.sidebar.header("Filtro:")
    battleType = st.sidebar.multiselect(
        "Tipo de jogo:", options=df["battleType"].unique(), default="Scrim"
    )
    options = list(df["team"].unique())
    options.append("outros")
    team = st.sidebar.multiselect("Time:", options, default="LBR")
    side = st.sidebar.multiselect("Lado do mapa:", options=df["side"].unique())

    col1, col2 = st.columns([1, 1])
    with col1:
        positionPlayed = df["positionPlayed"].unique()
        positionPlayed = st.multiselect("", positionPlayed, positionPlayed[:5])
    with col2:
        opt = st.selectbox(
            "", ("Visualização sem personagem", "Visualização por personagem")
        )
        if opt == "Visualização sem personagem":
            view_champion = 0
        else:
            view_champion = 1

    ### SEMANA ###
    options = ["Sim, por semana", "Sim, por data", "Não"]
    default_ix = options.index("Não")
    data_visivel = st.sidebar.selectbox("Visualizar data?", options, index=default_ix)

    if data_visivel == "Sim, por semana":
        filtro_data = "semana"
    elif data_visivel == "Sim, por data":
        filtro_data = "data"

    if data_visivel != "Não":
        data_lista = list(df[filtro_data].unique())
        data = st.sidebar.select_slider(
            filtro_data, df[filtro_data], value=[min(data_lista), max(data_lista)]
        )

        sem_min = data_lista.index(gd.minimo_valor(data))
        sem_max = data_lista.index(gd.maximo_valor(data))

        lista_data = []

        for i in range(sem_min, sem_max + 1):
            lista_data.append(data_lista[i])

        df = df[df[filtro_data].isin(lista_data)]

    # VERICICANDO ELEMENTOS DENTRO DA LISTA
    numero_time = gd.tamanho_lista(team)
    numero_tipo = gd.tamanho_lista(battleType)
    numero_lado = gd.tamanho_lista(side)

    # DEFININDO DADOS DA LBR VS INIMIGO
    if numero_time == 2 and "LBR" in team:
        st.text("2 times escolhidos, os campos serão calculados entre eles")
        primeiro_time = team[0]
        segundo_time = team[1]
        if primeiro_time == "LBR":
            df = df.loc[df["confronto"].str.contains(segundo_time)]
        else:
            df = df.loc[df["confronto"].str.contains(primeiro_time)]

    # -------------------------------------------------
    # --------------SELECIONANDO FILTRO----------------
    # -------------------------------------------------
    lista = []
    if view_champion == 1:
        lista.append("champion")
    if data_visivel != "Não":
        lista.append(filtro_data)
    if numero_time > 0:
        lista.append("team")
    if numero_tipo > 0:
        lista.append("battleType")
    if numero_lado > 0:
        lista.append("side")
    lista.append("positionPlayed")

    # -------------------------------------------------
    # -------PROCESSANDO OS DADOS COM FILTRO-----------
    # -------------------------------------------------

    # -------------------------------------------------
    # ----------------0.TABELA GENÉRICA----------------
    # -------------------------------------------------

    if numero_time > 0 or numero_tipo > 0 or numero_lado > 0:
        df_partidas = (df.groupby(lista)["ID"].count()) / 1
        df_partidas = df_partidas.reset_index()

        # -------------------------------------------------
        # ----------------1.TABELA DE OURO-----------------
        # -------------------------------------------------

        # OURO POR TEMPO
        df_gold = df.groupby(lista)["diffGold5", "diffGold10", "diffGold15"].sum()
        df_gold = df_gold.round(2)

        df_ouro = df_partidas.merge(df_gold, how="left", on=lista)

        df_ouro["diffGold5"] = df_ouro["diffGold5"] / df_ouro["ID"]
        df_ouro["diffGold10"] = df_ouro["diffGold10"] / df_ouro["ID"]
        df_ouro["diffGold15"] = df_ouro["diffGold15"] / df_ouro["ID"]
        df_ouro = df_ouro.drop(columns=["ID"])

        # -------------------------------------------------
        # ----------------2.TABELA DE MÉDIA----------------
        # -------------------------------------------------
        # MÉDIA DE DURAÇÃO DE TEMPO DE JOGO
        df_media = gd.groupby_mean_merge(df, df_partidas, lista, "KDA")

        lista_media = [
            "KPR",
            "totalGold%",
            "damageDealt",
            "damageDealt%",
            "DDPG",
            "totalWards",
            "destroyedWards",
        ]

        for item in lista_media:
            df_media = gd.groupby_mean_merge(df, df_media, lista, item)

        df_media = df_media.drop(columns=["ID"])

        # -------------------------------------------------
        # -------------3.TABELA DE WIN RATE----------------
        # -------------------------------------------------
        lista_ouro = ["%WR gold5", "%WR gold10", "%WR gold15"]
        win_rate_ouro = df.groupby(lista)[lista_ouro].sum()
        win_rate_ouro = df_partidas.merge(win_rate_ouro, how="left", on=lista)
        for ouro in lista_ouro:
            win_rate_ouro[ouro] = (win_rate_ouro[ouro] / win_rate_ouro["ID"]) * 100
        win_rate_ouro = win_rate_ouro.drop(columns=["ID"])

    # -------------------------------------------------
    # ---------------FILTRANDO OS DADOS----------------
    # -------------------------------------------------
    time = "(team == @team)"
    tipo = "(battleType == @battleType)"
    lado = "(side == @side)"
    semana = "(semana == @lista_data)"
    data = "(data == @lista_data)"
    posicao = "(positionPlayed == @positionPlayed)"

    df_ouro = df_ouro.query(posicao)
    df_media = df_media.query(posicao)
    win_rate_ouro = win_rate_ouro.query(posicao)

    if data_visivel == "Sim, por semana":
        df_ouro = df_ouro.query(semana)
        df_media = df_media.query(semana)
        win_rate_ouro = win_rate_ouro.query(semana)

    if data_visivel == "Sim, por data":
        df_ouro = df_ouro.query(data)
        df_media = df_media.query(data)
        win_rate_ouro = win_rate_ouro.query(data)

    if numero_tipo > 0:
        df_ouro = df_ouro.query(tipo)
        df_media = df_media.query(tipo)
        win_rate_ouro = win_rate_ouro.query(tipo)
        df_grafico_ouro = df_ouro.drop(columns=["battleType"])

    if numero_time > 0:
        df_ouro = df_ouro.query(time)
        df_media = df_media.query(time)
        win_rate_ouro = win_rate_ouro.query(time)
        df_grafico_ouro = df_ouro.drop(columns=["team"])

    if numero_lado > 0:
        df_ouro = df_ouro.query(lado)
        df_media = df_media.query(lado)
        win_rate_ouro = win_rate_ouro.query(lado)
        df_grafico_ouro = df_ouro.drop(columns=["side"])

    # -------------------------------------------------
    # -------COLOCANDO OS DADOS NA TELA----------------
    # -------------------------------------------------
    if numero_time == 0 and numero_tipo == 0 and numero_lado == 0:
        st.header("Selecione pelo menos um filtro para aparecer dados")
    else:
        st.subheader("Dados gerais - Média")
        st.table(df_media.style.format(precision=2))
        st.subheader("Dados de ouro")
        st.table(df_ouro.style.format(precision=2))
        st.subheader("% de WR conforme ouro do jogador")
        st.table(win_rate_ouro.style.format(precision=2))

        # st.area_chart(df_grafico_ouro, x = "diffGold5")
