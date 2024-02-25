from data.imports import pd, st, np
from data.utils import GameData

gd = GameData()


# Site
def app():
    st.title("Win Rate - 1° Objetivo")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown("#### Dragão")
    prim_dragao = col1.radio("", (-1, 0, 1), horizontal=True, key="dragon", index=1)
    col1.markdown("---")

    col2.markdown("#### Arauto")
    prim_arauto = col2.radio("", (-1, 0, 1), horizontal=True, key="herald", index=1)
    col2.markdown("---")

    col3.markdown("#### Torre")
    prim_torre = col3.radio("", (-1, 0, 1), horizontal=True, key="turret", index=1)
    col3.markdown("---")

    col4.markdown("#### Morte")
    prim_morte = col4.radio("", (-1, 0, 1), horizontal=True, key="blood", index=1)
    col4.markdown("---")

    col5.markdown("#### Barão")
    prim_barao = col5.radio("", (-1, 0, 1), horizontal=True, key="baron", index=1)
    col5.markdown("---")

    # -------------------------------------------------
    # ------PROCESSANDO DADOS DA TABELA----------------
    # -------------------------------------------------

    df = pd.read_csv("data/raw_game_data/df_final_liberty.csv", sep=";")

    # APAGANDO JOGO COM MENOS DE 10 MINUTOS
    df["secondsInGame"] = pd.to_numeric(df["secondsInGame"])
    df = df.loc[df["secondsInGame"] >= 630]

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

    # CRIANDO NOVAS COLUNAS PARA CALCULAR WIN RATE
    lista_ouro = ["%WRgold5", "%WRgold10", "%WRgold15"]
    lista_posicao = ["baron", "jungler", "mid", "dragon", "support"]
    for ouro in lista_ouro:
        for posicao in lista_posicao:
            ouro_posicao = ouro + posicao  # %WRgold5baron
            ouro_texto = ouro[:3] + " " + ouro[3:]  # WR gold5
            df[ouro_posicao] = np.where(
                df["positionPlayed"] == posicao, df[ouro_texto], 0
            )

    # FILLNA
    df["firstHeraldKillSeconds"] = df["firstHeraldKillSeconds"].fillna(0)
    df["firstDragonKillSeconds"] = df["firstDragonKillSeconds"].fillna(0)
    df["firstTowerDestroyedSeconds"] = df["firstTowerDestroyedSeconds"].fillna(0)

    # ARRUMANDO DADOS - REPLACE DE VALOR NULO POR 10000
    df["firstHeraldKillSeconds"] = (
        df["firstHeraldKillSeconds"].replace(0, 10000).astype(int)
    )
    df["firstDragonKillSeconds"] = (
        df["firstDragonKillSeconds"].replace(0, 10000).astype(int)
    )
    df["firstTowerDestroyedSeconds"] = (
        df["firstTowerDestroyedSeconds"].replace(0, 10000).astype(int)
    )

    # CRIANDO COPIA DA COLUNA
    df["baronTime"] = df["firstBaronKillSeconds"]
    df["baronTime"] = df["baronTime"].fillna(0)

    # ARRUMANDO DADOS - TRANSFORMANDO OS SEGUNDOS DA COLUNA EM VALOR BINÁRIO
    df["firstBloodSeconds"] = df["firstBloodSeconds"].fillna(0)
    df["firstBloodSeconds"] = df["firstBloodSeconds"].map(lambda x: 0 if x == 0 else 1)
    df["firstBaronKillSeconds"] = df["firstBaronKillSeconds"].fillna(0)
    df["firstBaronKillSeconds"] = df["firstBaronKillSeconds"].map(
        lambda x: 0 if x == 0 else 1
    )

    # REPLACE 0 TO NAN PARA CALCULAR MÉDIA
    df["towersDestroyed"] = df["towersDestroyed"].replace(0, np.nan)
    df["dragonsKills"] = df["dragonsKills"].replace(0, np.nan)
    df["heraldKills"] = df["heraldKills"].replace(0, np.nan)

    # RENOMEANDO COLUNAS GRANDES
    df = df.rename(
        columns={
            "firstHeraldKillSeconds": "1Herald",
            "firstDragonKillSeconds": "1Dragon",
            "firstTowerDestroyedSeconds": "1Turret",
            "firstBloodSeconds": "1Kill",
            "baronTime": "1Nashor",
            "totalDamageDealtToChampions": "Damage Dealt",
        }
    )

    # -------------------------------------------------
    # ------------------FILTRANDO DADOS----------------
    # -------------------------------------------------
    # filtro_data - https://www.samproell.io/posts/datascience/adhoc-data-filters-streamlit/
    # https://discuss.streamlit.io/t/filtering-data-with-pandas/20724/2

    battleType = st.sidebar.multiselect(
        "Tipo de jogo:", options=df["battleType"].unique(), default="Scrim"
    )
    team = st.sidebar.multiselect("Time:", options=df["team"].unique(), default="LBR")
    side = st.sidebar.multiselect("Lado do mapa:", options=df["side"].unique())

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
    if data_visivel == "Não":
        if numero_tipo == 0 and numero_time == 0 and numero_lado == 0:
            st.text("Nenhum filtro_data selecionado. Selecione um para poder analisar")
    else:
        lista.append(filtro_data)
    if numero_tipo > 0:
        lista.append("battleType")
    if numero_time > 0:
        lista.append("team")
    if numero_lado > 0:
        lista.append("side")

    # -------------------------------------------------
    # -------PROCESSANDO OS DADOS COM FILTRO-----------
    # -------------------------------------------------

    # -------------------------------------------------
    # ----------------0.TABELA GENÉRICA----------------
    # -------------------------------------------------

    if numero_time > 0 or numero_tipo > 0 or numero_lado > 0:
        df_partidas = (df.groupby(lista)["ID"].count()) / 5
        df_vitorias = (df.groupby(lista)["result"].sum()) / 5
        df_partidas = df_partidas.reset_index()
        df_vitorias = df_vitorias.reset_index()
        df_partidas = df_partidas.merge(df_vitorias, how="left", on=lista)
        df_partidas["result"] = (df_partidas["result"] / df_partidas["ID"]) * 100
        df_partidas = df_partidas.rename(columns={"result": "% WR"})

        lista_resultado = [*lista]
        lista_resultado.append("result")

        # -------------------------------------------------
        # ----------------4.TABELA DE WR ELEMENTOS---------
        # -------------------------------------------------
        # --------------4.1 ARAUTO---------------
        objetivo = "1Herald"
        df_perc_arauto = df.loc[
            df.groupby(["ID"])[objetivo].transform("min").eq(df[objetivo])
        ].reset_index(drop=True)

        # ANÁLISE CRUZADO COM OUTROS OBJETIVOS
        lista_objetivo = gd.add_elem_cria_lista(lista, objetivo)
        lista_objetivo.append("ID")
        df_win_arauto = df_perc_arauto[lista_objetivo].copy()

        # LISTA COM ID
        lista_id = gd.add_elem_cria_lista(lista, "ID")
        df_geral = gd.winrate_merge(
            df_perc_arauto, lista, lista_resultado, objetivo, "Arauto"
        )

        # OPOSTO DE NÃO OBTER O OBJETIVO E CONSEGUIR GANHAR
        df_inimigo = gd.df_inimigo_obj(df_perc_arauto, df, len(df_perc_arauto))

        df_geral_oposto = gd.winrate_merge(
            df_inimigo, lista, lista_resultado, objetivo, "Arauto"
        )

        # --------------4.2 DRAGÃO---------------
        objetivo = "1Dragon"
        df_perc_drag = df.loc[
            df.groupby(["ID"])[objetivo].transform("min").eq(df[objetivo])
        ].reset_index(drop=True)

        # OPOSTO DE NÃO OBTER O OBJETIVO E CONSEGUIR GANHAR
        df_inimigo = gd.df_inimigo_obj(df_perc_drag, df, len(df_perc_drag))
        df_geral_oposto_2 = gd.winrate_merge(
            df_inimigo, lista, lista_resultado, objetivo, "Dragao"
        )
        if not df_geral_oposto_2.empty:
            df_geral_oposto = df_geral_oposto_2.merge(
                df_geral_oposto, how="outer", on=lista
            )

        # ANÁLISE CRUZADO COM OUTROS OBJETIVOS
        lista_objetivo = gd.add_elem_cria_lista(lista, objetivo)
        lista_objetivo.append("ID")
        df_win_dragao = df_perc_drag[lista_objetivo].copy()
        df_win_rate = df_win_arauto.merge(df_win_dragao, how="outer", on=lista_id)

        df_perc_drag = gd.winrate_merge(
            df_perc_drag, lista, lista_resultado, objetivo, "Dragao"
        )
        df_geral = df_geral.merge(df_perc_drag, how="outer", on=lista)

        # --------------4.3 TORRE---------------
        objetivo = "1Turret"
        df_perc_torre = df.loc[
            df.groupby(["ID"])[objetivo].transform("min").eq(df[objetivo])
        ].reset_index(drop=True)

        # OPOSTO DE NÃO OBTER O OBJETIVO E CONSEGUIR GANHAR
        df_inimigo = gd.df_inimigo_obj(df_perc_torre, df, len(df_perc_torre))
        df_geral_oposto_2 = gd.winrate_merge(
            df_inimigo, lista, lista_resultado, objetivo, "FT"
        )
        if not df_geral_oposto_2.empty:
            df_geral_oposto = df_geral_oposto_2.merge(
                df_geral_oposto, how="outer", on=lista
            )

        # ANÁLISE CRUZADO COM OUTROS OBJETIVOS
        lista_objetivo = gd.add_elem_cria_lista(lista, objetivo)
        lista_objetivo.append("ID")
        df_win_torre = df_perc_torre[lista_objetivo].copy()
        df_win_rate = df_win_rate.merge(df_win_torre, how="outer", on=lista_id)

        df_perc_torre = gd.winrate_merge(
            df_perc_torre, lista, lista_resultado, objetivo, "FT"
        )
        df_geral = df_geral.merge(df_perc_torre, how="outer", on=lista)

        # --------------4.4 BARÃO---------------
        objetivo = "1Nashor"
        df_perc_barao = df.loc[
            df.groupby(["ID"])[objetivo].transform("max").eq(df[objetivo])
        ].reset_index(drop=True)
        df_perc_barao = df_perc_barao.loc[df_perc_barao[objetivo] != 0]
        df_perc_barao = df_perc_barao.reset_index()

        # OPOSTO DE NÃO OBTER O OBJETIVO E CONSEGUIR GANHAR
        df_inimigo = gd.df_inimigo_obj(df_perc_barao, df, len(df_perc_barao))
        df_geral_oposto_2 = gd.winrate_merge(
            df_inimigo, lista, lista_resultado, objetivo, "Barao"
        )
        if not df_geral_oposto_2.empty:
            df_geral_oposto = df_geral_oposto_2.merge(
                df_geral_oposto, how="outer", on=lista
            )

        # ANÁLISE CRUZADO COM OUTROS OBJETIVOS
        lista_objetivo = gd.add_elem_cria_lista(lista, objetivo)
        lista_objetivo.append("ID")
        df_win_barao = df_perc_barao[lista_objetivo].copy()
        df_win_rate = df_win_rate.merge(df_win_barao, how="outer", on=lista_id)

        df_perc_barao = gd.winrate_merge(
            df_perc_barao, lista, lista_resultado, objetivo, "Barao"
        )
        df_geral = df_geral.merge(df_perc_barao, how="outer", on=lista)

        # --------------4.5 MORTE---------------
        objetivo = "1Kill"
        df_perc_morte = df.loc[
            df.groupby(["ID"])[objetivo].transform("max").eq(df[objetivo])
        ].reset_index(drop=True)
        df_perc_morte = df_perc_morte.reset_index()

        # OPOSTO DE NÃO OBTER O OBJETIVO E CONSEGUIR GANHAR
        df_inimigo = gd.df_inimigo_obj(df_perc_morte, df, len(df_perc_morte))
        df_geral_oposto_2 = gd.winrate_merge(
            df_inimigo, lista, lista_resultado, objetivo, "FB"
        )
        if not df_geral_oposto_2.empty:
            df_geral_oposto = df_geral_oposto_2.merge(
                df_geral_oposto, how="outer", on=lista
            )

        # ANÁLISE CRUZADO COM OUTROS OBJETIVOS
        lista_objetivo = gd.add_elem_cria_lista(lista, objetivo)
        lista_objetivo.append("ID")
        df_win_morte = df_perc_morte[lista_objetivo].copy()
        df_win_rate = df_win_rate.merge(df_win_morte, how="outer", on=lista_id)

        df_perc_morte = gd.winrate_merge(
            df_perc_morte, lista, lista_resultado, objetivo, "FB"
        )
        df_geral = df_geral.merge(df_perc_morte, how="outer", on=lista)

        # --------------TRATAMENTO DE DADOS DA TABELA DE WIN RATE---------------
        # LISTA COM ID
        lista_resultado_id = gd.add_elem_cria_lista(lista_resultado, "ID")

        df_resultado = df[lista_resultado_id].copy()
        df_resultado = df_resultado.drop_duplicates()
        df_vitoria_combinado = df_win_rate.merge(df_resultado, how="outer", on=lista_id)

        # -----------------WIN RATE POSITIVO E NEGATIVO ------------------------
        df_geral["result"] = 1
        df_geral_oposto["result"] = -1
        df_vit_comb = pd.concat([df_geral, df_geral_oposto])

    # -------------------------------------------------
    # ---------------FILTRANDO OS DADOS----------------
    # -------------------------------------------------

    time = "(team == @team)"
    tipo = "(battleType == @battleType)"
    lado = "(side == @side)"
    semana = "(semana == @lista_data)"
    data = "(data == @lista_data)"

    if data_visivel == "Sim, por semana":
        df_geral = df_geral.query(semana)
        df_vitoria_combinado = df_vitoria_combinado.query(semana)
        df_vit_comb = df_vit_comb.query(semana)
        # df_geral_oposto = df_geral_oposto.query(semana)

    if data_visivel == "Sim, por data":
        df_geral = df_geral.query(data)
        df_vitoria_combinado = df_vitoria_combinado.query(data)
        df_vit_comb = df_vit_comb.query(data)
        # df_geral_oposto = df_geral_oposto.query(data)

    if numero_tipo > 0:
        df_geral = df_geral.query(tipo)
        df_vitoria_combinado = df_vitoria_combinado.query(tipo)
        df_vit_comb = df_vit_comb.query(tipo)
        # df_geral_oposto = df_geral_oposto.query(tipo)

    if numero_time > 0:
        df_geral = df_geral.query(time)
        df_vitoria_combinado = df_vitoria_combinado.query(time)
        df_vit_comb = df_vit_comb.query(time)
        # df_geral_oposto = df_geral_oposto.query(time)

    if numero_lado > 0:
        df_geral = df_geral.query(lado)
        df_vitoria_combinado = df_vitoria_combinado.query(lado)
        # df_geral_oposto = df_geral_oposto.query(lado)

    # -------------------------------------------------
    # -------COLOCANDO OS DADOS NA TELA----------------
    # -------------------------------------------------
    if numero_time == 0 and numero_tipo == 0 and numero_lado == 0:
        st.header("Selecione pelo menos um filtro para aparecer dados")
    else:
        # st.subheader("% de WR conforme o 1° elemento do jogo")
        # st.table(df_geral.style.format(precision=2))

        # st.subheader("% de WR cruzado")
        objetivo = []
        if (prim_dragao) == -1 or (prim_dragao) == 1:
            objetivo.append("1Dragon")

        if (prim_arauto) == -1 or (prim_arauto) == 1:
            objetivo.append("1Herald")

        if (prim_torre) == -1 or (prim_torre) == 1:
            objetivo.append("1Turret")

        if (prim_morte) == -1 or (prim_morte) == 1:
            objetivo.append("1Kill")

        if (prim_barao) == -1 or (prim_barao) == 1:
            objetivo.append("1Nashor")

        # SEPARANDO COLUNAS PARA FAZER CÁLCULOS
        nome_colunas = lista_resultado_id + objetivo
        df_vitoria_obj_sel = df_vitoria_combinado[nome_colunas].copy()

        # TRATANDO O DATAFRAME
        df_vitoria_obj_sel = df_vitoria_obj_sel.fillna(0)

        for item in objetivo:
            if item == "1Dragon":
                if (prim_dragao) == -1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] == 0
                    ]
                elif (prim_dragao) == 1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] > 0
                    ]

            if item == "1Herald":
                if (prim_arauto) == -1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] == 0
                    ]
                elif (prim_arauto) == 1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] > 0
                    ]

            if item == "1Turret":
                if (prim_torre) == -1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] == 0
                    ]
                elif (prim_torre) == 1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] > 0
                    ]

            if item == "1Kill":
                if (prim_morte) == -1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] == 0
                    ]
                elif (prim_morte) == 1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] > 0
                    ]

            if item == "1Nashor":
                if (prim_barao) == -1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] == 0
                    ]
                elif (prim_barao) == 1:
                    df_vitoria_obj_sel = df_vitoria_obj_sel.loc[
                        df_vitoria_obj_sel[item] > 0
                    ]

        if len(objetivo) > 1:
            objetivo = objetivo[0]

        print(df_vitoria_obj_sel.groupby(lista)[objetivo].count())
        df_total = df_vitoria_obj_sel.groupby(lista)[objetivo].count().rename("Total")
        df_perc_obj = (
            df_vitoria_obj_sel.groupby(lista_resultado)[objetivo]
            .count()
            .rename("Qtde jogos")
        )
        df_total = df_total.reset_index()
        df_perc_obj = df_perc_obj.reset_index()
        df_perc_obj = df_perc_obj.merge(df_total, how="left", on=lista)
        df_perc_obj = df_perc_obj[df_perc_obj.result != 0]
        df_perc_obj = df_perc_obj.drop(columns=["result"])
        df_perc_obj["% WR"] = (df_perc_obj["Qtde jogos"] / df_perc_obj["Total"]) * 100

        st.table(df_perc_obj.style.format(precision=2))
