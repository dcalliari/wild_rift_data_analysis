from data.imports import pd, st
from data.utils import GameData

gd = GameData()


# Site
def app():

    df = gd.process_game_data()

    # CALCULO
    df["GPS"] = df["totalGolds3"] / df["secondsInGame"]
    df["DDPS"] = df["totalDamageDealtToChampions"] / df["secondsInGame"]

    df_copy = df.copy()

    # -------------------------------------------------
    # ------------------FILTRANDO DADOS----------------
    # -------------------------------------------------
    identificacao = list(df["champion"].unique())
    identificacao = sorted(identificacao)
    champion = st.sidebar.selectbox("Campeão:", options=identificacao)
    # CRIADO ESAA VARIÁVEL AUXILIAR PQ NÃO FUNCIONAVA COM CHAMPION
    campeao = champion
    # CRIAR TABELA TEMPORARIA PRA ACHAR ROTA
    rota_campeao = df.loc[df["champion"] == campeao]
    lista_campeao = list(rota_campeao["positionPlayed"].unique())
    lista_campeao.append("todas")
    rota = st.sidebar.selectbox("Rota:", options=lista_campeao)

    if rota != "todas":
        df = df.query("(champion == @champion) and (positionPlayed == @rota)")
    else:
        df = df.query("champion == @champion")
    df = df.reset_index()
    df = df.drop(columns=["index"])

    battleType = st.sidebar.multiselect(
        "Tipo de jogo:", options=df["battleType"].unique()
    )
    team = st.sidebar.multiselect("Time:", options=df["team"].unique())
    side = st.sidebar.multiselect("Lado do mapa:", options=df["side"].unique())
    app = st.sidebar.multiselect("Versão do app:", options=df["app"].unique())

    # VERICICANDO ELEMENTOS DENTRO DA LISTA
    numero_time = gd.tamanho_lista(team)
    numero_tipo = gd.tamanho_lista(battleType)
    numero_lado = gd.tamanho_lista(side)
    numero_versao = gd.tamanho_lista(app)

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

    lista = ["champion", "positionPlayed"]

    if numero_tipo > 0:
        lista.append("battleType")
    if numero_time > 0:
        lista.append("team")
    if numero_lado > 0:
        lista.append("side")
    if numero_versao > 0:
        lista.append("app")

    # -------------------------------------------------
    # -------PROCESSANDO OS DADOS COM FILTRO-----------
    # -------------------------------------------------

    # -------------------------------------------------
    # ----------------1.TABELA DE PICKS----------------
    # -------------------------------------------------
    df = df[
        [
            "ID",
            "battleType",
            "team",
            "result",
            "champion",
            "positionPlayed",
            "side",
            "app",
            "kills",
            "deaths",
            "assists",
            "GPS",
            "DDPS",
        ]
    ].copy()

    df_copy = df_copy[
        [
            "ID",
            "battleType",
            "team",
            "result",
            "champion",
            "positionPlayed",
            "side",
            "app",
            "kills",
            "deaths",
            "assists",
            "GPS",
            "DDPS",
        ]
    ].copy()

    # FAZENDO MÉDIA DOS DADOS DO PERSONAGEM
    df_media = df.groupby(lista).mean()

    # Contando qtde de jogos
    df_qtde_jogos = df.groupby(lista)["ID"].count().rename("Qtde jogos")

    # Juntando as tabelas
    df_media = df_media.merge(df_qtde_jogos, how="left", on=lista)

    # Removendo coluna desnecessária
    df_media = df_media.drop(columns=["ID"])

    # Arrumando os números
    df_media["result"] = df_media["result"] * 100

    # Renomeando os dados
    df_media = df_media.rename(columns={"result": "% WR"})

    # Ordenando as colunas
    cols = df_media.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_media = df_media[cols]

    tamanho_df_sel = len(df)
    i = 0

    # CRIANDO A TABELA DE PERSONAGENS JOGADOS COM E CONTRA
    while i != tamanho_df_sel:
        lado = df["side"][i]
        chave = df["ID"][i]
        if lado == "blue":
            lado_oposto = "red"
        else:
            lado_oposto = "blue"
        pick = df_copy.query("(side == @lado) and (ID == @chave)")
        pick_inimigo = df_copy.query("(side == @lado_oposto) and (ID == @chave)")

        if i == 0:
            df_pick = pick
            df_inimigo = pick_inimigo
        else:
            df_pick = pd.concat([df_pick, pick])
            df_inimigo = pd.concat([df_inimigo, pick_inimigo])
        i = i + 1
    df_picks = df_pick.drop(df_pick[df_pick["champion"] == campeao].index)

    # -------------------------------------------------
    # -SELECIONANDO OS DADOS QUE SERÃO MOSTRADOS TELA--
    # ------------------------PICKS--------------------
    # -------------------------------------------------

    # Contando qtde de jogos
    df_picks_grouped_qtde = (
        df_picks.groupby(lista)["ID"]
        .count()
        .rename("Qtde jogos")
        .reset_index(drop=False)
    )
    # Contando qtde de vitórias
    df_picks_grouped_result = df_picks.groupby(lista)["result"].sum().rename("Vitória")
    # Agrupando % de vitória e outros dados como KDA, GPM e DDPM
    df_picks_grouped = df_picks.groupby(lista).mean()

    # Renomeando coluna
    df_picks_grouped = df_picks_grouped.rename(columns={"result": "% WR"})
    # Deixando o número com duas casas decimais
    df_picks_grouped["% WR"] = df_picks_grouped["% WR"] * 100

    # Juntando as tabelas
    df_picks_grouped = df_picks_grouped.merge(
        df_picks_grouped_qtde, how="left", on=lista
    )
    df_picks_grouped = df_picks_grouped.merge(
        df_picks_grouped_result, how="left", on=lista
    )

    # ------------------------jogado contra---------------------
    # ----------------------------------------------------------

    # Contando qtde de jogos
    df_inim_grouped_qtde = (
        df_inimigo.groupby(lista)["ID"]
        .count()
        .rename("Qtde jogos")
        .reset_index(drop=False)
    )
    # Contando qtde de vitórias
    df_inim_grouped_result = df_inimigo.groupby(lista)["result"].sum().rename("Vitória")
    # Agrupando % de vitória e outros dados como KDA, GPM e DDPM
    df_inim_grouped = df_inimigo.groupby(lista).mean()

    # Renomeando coluna
    df_inim_grouped = df_inim_grouped.rename(columns={"result": "% WR"})
    # Deixando o número com duas casas decimais
    df_inim_grouped["% WR"] = df_inim_grouped["% WR"] * 100
    df_inim_grouped = df_inim_grouped.reset_index()

    # Juntando as tabelas
    df_inim_grouped = df_inim_grouped.merge(df_inim_grouped_qtde, how="left", on=lista)
    df_inim_grouped = df_inim_grouped.merge(
        df_inim_grouped_result, how="left", on=lista
    )

    # -------------------------------------------------
    # ---------------FILTRANDO OS DADOS----------------
    # -------------------------------------------------

    time = "(team == @team)"
    tipo = "(battleType == @battleType)"
    lado = "(side == @side)"
    versao = "(app == @app)"

    # 1 escolha
    if numero_time > 0:
        df_picks_grouped = df_picks_grouped.query(time)
        df_media = df_media.query(time)
        df_inim_grouped = df_inim_grouped.query(time)

    if numero_tipo > 0:
        df_picks_grouped = df_picks_grouped.query(tipo)
        df_media = df_media.query(tipo)
        df_inim_grouped = df_inim_grouped.query(tipo)

    if numero_lado > 0:
        df_picks_grouped = df_picks_grouped.query(lado)
        df_media = df_media.query(lado)
        df_inim_grouped = df_inim_grouped.query(lado)

    if numero_versao > 0:
        df_picks_grouped = df_picks_grouped.query(versao)
        df_media = df_media.query(versao)
        df_inim_grouped = df_inim_grouped.query(versao)

    # -------------------------------------------------
    # -SELECIONANDO OS DADOS QUE SERÃO MOSTRADOS TELA--
    # ------------------------PICKS--------------------
    # -------------------------------------------------
    # Dropando coluna que não uso
    if numero_time > 0:
        df_picks_grouped = df_picks_grouped.drop(columns=["team"])
        df_inim_grouped = df_inim_grouped.drop(columns=["team"])
    if numero_tipo > 0:
        df_picks_grouped = df_picks_grouped.drop(columns=["battleType"])
        df_inim_grouped = df_inim_grouped.drop(columns=["battleType"])
    if numero_lado > 0:
        df_picks_grouped = df_picks_grouped.drop(columns=["side"])
        df_inim_grouped = df_inim_grouped.drop(columns=["side"])
    if numero_versao > 0:
        df_picks_grouped = df_picks_grouped.drop(columns=["app"])
        df_inim_grouped = df_inim_grouped.drop(columns=["app"])

    df_picks_grouped_filter = df_picks_grouped.drop(
        columns=["ID", "kills", "deaths", "assists", "GPS", "DDPS"]
    )
    df_inim_grouped_filter = df_inim_grouped.drop(
        columns=["ID", "kills", "deaths", "assists", "GPS", "DDPS"]
    )

    # Separando em tabelas menores de exibição
    df_picks_grouped_top = df_picks_grouped_filter.loc[
        df_picks_grouped_filter["positionPlayed"] == "baron"
    ]
    df_picks_grouped_jg = df_picks_grouped_filter.loc[
        df_picks_grouped_filter["positionPlayed"] == "jungler"
    ]
    df_picks_grouped_mid = df_picks_grouped_filter.loc[
        df_picks_grouped_filter["positionPlayed"] == "mid"
    ]
    df_picks_grouped_adc = df_picks_grouped_filter.loc[
        df_picks_grouped_filter["positionPlayed"] == "dragon"
    ]
    df_picks_grouped_sup = df_picks_grouped_filter.loc[
        df_picks_grouped_filter["positionPlayed"] == "support"
    ]

    # Separando em tabelas menores de exibição
    df_inim_grouped_top = df_inim_grouped_filter.loc[
        df_inim_grouped_filter["positionPlayed"] == "baron"
    ]
    df_inim_grouped_jg = df_inim_grouped_filter.loc[
        df_inim_grouped_filter["positionPlayed"] == "jungler"
    ]
    df_inim_grouped_mid = df_inim_grouped_filter.loc[
        df_inim_grouped_filter["positionPlayed"] == "mid"
    ]
    df_inim_grouped_adc = df_inim_grouped_filter.loc[
        df_inim_grouped_filter["positionPlayed"] == "dragon"
    ]
    df_inim_grouped_sup = df_inim_grouped_filter.loc[
        df_inim_grouped_filter["positionPlayed"] == "support"
    ]

    # -------------------------------------------------
    # -------COLOCANDO OS DADOS NA TELA----------------
    # -------------------------------------------------
    texto = "Dados - " + campeao
    st.header(texto)
    st.table(df_media.style.format(precision=2))

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Jogado com:")
        if not df_picks_grouped_top.empty:
            st.subheader("Baron:")
            st.dataframe(df_picks_grouped_top.style.format(precision=2))
        if not df_picks_grouped_jg.empty:
            st.subheader("Jungler:")
            st.dataframe(df_picks_grouped_jg.style.format(precision=2))
        if not df_picks_grouped_mid.empty:
            st.subheader("Mid:")
            st.dataframe(df_picks_grouped_mid.style.format(precision=2))
        if not df_picks_grouped_adc.empty:
            st.subheader("Dragon:")
            st.dataframe(df_picks_grouped_adc.style.format(precision=2))
        if not df_picks_grouped_sup.empty:
            st.subheader("Support:")
            st.dataframe(df_picks_grouped_sup.style.format(precision=2))

    with col2:
        st.subheader("Jogado contra:")
        if not df_inim_grouped_top.empty:
            st.subheader("Baron:")
            st.dataframe(df_inim_grouped_top.style.format(precision=2))
        if not df_inim_grouped_jg.empty:
            st.subheader("Jungler:")
            st.dataframe(df_inim_grouped_jg.style.format(precision=2))
        if not df_inim_grouped_mid.empty:
            st.subheader("Mid:")
            st.dataframe(df_inim_grouped_mid.style.format(precision=2))
        if not df_inim_grouped_adc.empty:
            st.subheader("Dragon:")
            st.dataframe(df_inim_grouped_adc.style.format(precision=2))
        if not df_inim_grouped_sup.empty:
            st.subheader("Support:")
            st.dataframe(df_inim_grouped_sup.style.format(precision=2))
