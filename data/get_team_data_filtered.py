from data.imports import st, np
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

    # CALCULANDO O TEMPO DE JOGO
    df["durationGame"] = df["secondsInGame"].apply(
        lambda x: (
            "Entre 10 min e 12 min"
            if x <= 720
            else (
                "Entre 12 e 14 min"
                if x <= 840
                else (
                    "Entre 14 e 16 min"
                    if x <= 960
                    else (
                        "Entre 16 e 18 min"
                        if x <= 1080
                        else (
                            "Entre 18 e 20 min"
                            if x <= 1200
                            else (
                                "Entre 20 e 22 min" if x <= 1320 else "Acima de 22 min"
                            )
                        )
                    )
                )
            )
        )
    )

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
            "firstBaronKillSeconds": "1Nashor",
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
        # ----------------1.TABELA DE OURO-----------------
        # -------------------------------------------------

        # OURO POR TEMPO
        df_gold = df.groupby(lista)["totalGolds0", "totalGolds1", "totalGolds2"].mean()
        df_gold = df_gold.round(2)

        df_ouro = df_partidas.merge(df_gold, how="left", on=lista)

        df_ouro = df_ouro.rename(
            columns={
                "ID": "Qtde jogos",
                "totalGolds0": "Gold5",
                "totalGolds1": "Gold10",
                "totalGolds2": "Gold15",
            }
        )

        # DIFF OURO
        df_gold_diff = df.groupby(lista)["diffGold5", "diffGold10", "diffGold15"].sum()
        df_gold_diff = df_gold_diff.round(2)

        df_ouro = df_ouro.merge(df_gold_diff, how="left", on=lista)

        df_ouro["diffGold5"] = df_ouro["diffGold5"] / df_ouro["Qtde jogos"]
        df_ouro["diffGold10"] = df_ouro["diffGold10"] / df_ouro["Qtde jogos"]
        df_ouro["diffGold15"] = df_ouro["diffGold15"] / df_ouro["Qtde jogos"]
        # df_ouro = df_ouro.drop(columns=['ID'])

        # -------------------------------------------------
        # ----------------2.TABELA DE MÉDIA----------------
        # -------------------------------------------------
        # CALCULAR MÉDIA DE DURAÇÃO DE TEMPO DE JOGO --> FUTURAMENTE
        df_media = gd.groupby_mean_merge(df, df_partidas, lista, "KDA")
        lista_media = [
            "kills",
            "Damage Dealt",
            "towersDestroyed",
            "dragonsKills",
            "heraldKills",
            "minionsKills",
        ]

        for item in lista_media:
            df_media = gd.groupby_mean_merge(df, df_media, lista, item)

        df_media = df_media.drop(columns=["ID", "% WR"])

        # -------------------------------------------------
        # ----------------3.TABELA DE ELEMENTOS------------
        # -------------------------------------------------

        # % QTDE ARAUTO
        df_geral_qtde = gd.calcula_porc_obj_merge(
            df, df_partidas, lista, "1Herald", "Arauto"
        )

        # % QTDE DRAGÃO
        df_geral_qtde = gd.calcula_porc_obj_merge(
            df, df_geral_qtde, lista, "1Dragon", "Dragao"
        )

        # % QTDE TORRE
        df_geral_qtde = gd.calcula_porc_obj_merge(
            df, df_geral_qtde, lista, "1Turret", "FT"
        )

        # % QTDE MORTE
        df_count_morte = df.groupby(lista)["1Kill"].sum().rename("Morte")
        df_geral_qtde = df_geral_qtde.merge(df_count_morte, how="left", on=lista)
        df_geral_qtde["% FB"] = df_geral_qtde["Morte"] / df_geral_qtde["ID"]
        df_geral_qtde["% FB"] = df_geral_qtde["% FB"] * 100
        df_geral_qtde = df_geral_qtde.drop(columns=["Morte"])

        # FALTOU BARÃO -> DROP LINHAS NULAS. PEGAR O MENOR VALOR E USAR
        df_barao = df.loc[df["1Nashor"] != 0]
        df_geral_qtde = gd.calcula_porc_obj_merge(
            df_barao, df_geral_qtde, lista, "1Nashor", "Barao"
        )

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

        # --------------4.2 DRAGÃO---------------
        objetivo = "1Dragon"
        df_perc_drag = df.loc[
            df.groupby(["ID"])[objetivo].transform("min").eq(df[objetivo])
        ].reset_index(drop=True)

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
        df_perc_barao = df_perc_barao.loc[df_perc_barao["1Nashor"] == 1]

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
        df_vitoria_combinado = df_win_rate.merge(df_resultado, how="left", on=lista_id)

        # ---------------------------------------------------------
        # -------------5.TABELA DE WIN RATE DE OURO----------------
        # ---------------------------------------------------------

        for ouro in lista_ouro:
            for posicao in lista_posicao:
                ouro_posicao = ouro + posicao
                df_perc_ouro = df.loc[
                    df.groupby(["ID"])[ouro_posicao]
                    .transform("max")
                    .eq(df[ouro_posicao])
                ].reset_index(drop=True)
                df_perc_ouro = df_perc_ouro.loc[df_perc_ouro[ouro_posicao] == 1]

                # ANÁLISE CRUZADO COM OUTROS OBJETIVOS
                lista_ouro_id = [*lista]
                lista_ouro_id.append(ouro_posicao)
                lista_ouro_id.append("ID")
                df_win_ouro = df_perc_ouro[lista_ouro_id].copy()
                if ouro_posicao == "%WRgold5baron":
                    df_win_rate_ouro = df_win_ouro
                else:
                    df_win_rate_ouro = df_win_rate_ouro.merge(
                        df_win_ouro, how="outer", on=lista_id
                    )

        # --------------TRATAMENTO DE DADOS DA TABELA DE WIN RATE---------------
        # LISTA COM ID
        df_win_rate_tudo = df_vitoria_combinado.merge(
            df_win_rate_ouro, how="left", on=lista_id
        )
    # -------------------------------------------------
    # ---------------FILTRANDO OS DADOS----------------
    # -------------------------------------------------

    time = "(team == @team)"
    tipo = "(battleType == @battleType)"
    lado = "(side == @side)"
    semana = "(semana == @lista_data)"
    data = "(data == @lista_data)"

    if data_visivel == "Sim, por semana":
        df_ouro = df_ouro.query(semana)
        df_geral_qtde = df_geral_qtde.query(semana)
        df_media = df_media.query(semana)
        df_geral = df_geral.query(semana)
        df_win_rate_tudo = df_win_rate_tudo.query(semana)

    if data_visivel == "Sim, por data":
        df_ouro = df_ouro.query(data)
        df_geral_qtde = df_geral_qtde.query(data)
        df_media = df_media.query(data)
        df_geral = df_geral.query(data)
        df_win_rate_tudo = df_win_rate_tudo.query(data)

    if numero_tipo > 0:
        df_ouro = df_ouro.query(tipo)
        df_geral_qtde = df_geral_qtde.query(tipo)
        df_media = df_media.query(tipo)
        df_geral = df_geral.query(tipo)
        df_win_rate_tudo = df_win_rate_tudo.query(tipo)

    if numero_time > 0:
        df_ouro = df_ouro.query(time)
        df_geral_qtde = df_geral_qtde.query(time)
        df_media = df_media.query(time)
        df_geral = df_geral.query(time)
        df_win_rate_tudo = df_win_rate_tudo.query(time)

    if numero_lado > 0:
        df_ouro = df_ouro.query(lado)
        df_geral_qtde = df_geral_qtde.query(lado)
        df_media = df_media.query(lado)
        df_geral = df_geral.query(lado)
        df_win_rate_tudo = df_win_rate_tudo.query(lado)

    # -------------------------------------------------
    # -------COMBINAÇÃO ENTRE OS ELEMENTOS-------------
    # -------------------------------------------------

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

        st.subheader("% de objetivos, torre e morte conquistado primeiro")
        st.table(df_geral_qtde.style.format(precision=2))

        st.subheader("% de WR conforme o 1° elemento do jogo")
        st.table(df_geral.style.format(precision=2))

        st.subheader("% de WR cruzado")
        objetivo = ["1Herald", "1Dragon", "1Turret", "1Nashor", "1Kill"]
        objetivo = st.multiselect("", objetivo, objetivo[:3])

        col1, col2 = st.columns([1, 1])

        with col1:
            st.text("Ouro:")
            ouro = st.multiselect("", lista_ouro)
        with col2:
            st.text("Rota:")
            posicao = st.multiselect("", lista_posicao)

        if not objetivo:
            st.text("Não será calculado o WR com objetivo")

        ouro_rota = []
        if ouro and posicao:
            for o in ouro:
                for r in posicao:
                    texto = o + r
                    ouro_rota.append(texto)
        else:
            st.text("Não será calculado o WR com ouro por rota")

        filtro_tabela = ouro_rota + objetivo + lista_resultado
        ouro_objetivo = ouro_rota + objetivo

        df_win_rate_tudo = df_win_rate_tudo[
            df_win_rate_tudo.columns.intersection(filtro_tabela)
        ]
        df_win_rate_tudo = df_win_rate_tudo.dropna(subset=ouro_objetivo)

        df_win_rate_obj = df_win_rate_tudo.groupby(lista)[ouro_objetivo].count()
        df_win_rate_obj_total = df_win_rate_tudo.groupby(lista_resultado)[
            ouro_objetivo
        ].count()
        df_win_rate_obj = df_win_rate_obj.reset_index()
        df_win_rate_obj_total = df_win_rate_obj_total.reset_index()
        df_win_rate_obj = df_win_rate_obj_total.merge(
            df_win_rate_obj, how="left", on=lista
        )
        df_win_rate_obj = df_win_rate_obj[df_win_rate_obj.result != 0]
        df_win_rate_obj = df_win_rate_obj.drop(columns=["result"])

        for obj in ouro_objetivo:
            qtde = obj + "_x"
            total = obj + "_y"

            df_win_rate_obj["Qtde jogos"] = df_win_rate_obj[total]
            df_win_rate_obj["Win rate"] = (
                df_win_rate_obj[qtde] / df_win_rate_obj[total]
            ) * 100
            df_win_rate_obj = df_win_rate_obj.drop(columns=[qtde, total])

        st.table(df_win_rate_obj.style.format(precision=2))
