from data.imports import pd, st, np
from data.utils import GameData

import time

gd = GameData()


# Site
def app():

    df = gd.process_game_data()

    # ARRUMANDO DRAGÃO
    df["dragonsKills"] = df["dragonsKills"].fillna(0)
    df["stealDragonCount"] = df["stealDragonCount"].fillna(0)
    df["dragonsKills"] = df["dragonsKills"] + df["stealDragonCount"]

    # -------------------------------------------------
    # ------------------FILTRANDO DADOS----------------
    # -------------------------------------------------

    mes = st.sidebar.selectbox("Mês:", options=list(df["mes"].unique()))
    df = df.loc[df["mes"] == mes]
    data = st.sidebar.selectbox("Data:", options=list(df["data"].unique()))
    df_filtrado = df.loc[df["data"] == data]
    partida = st.sidebar.selectbox(
        "Partida:", options=list(df_filtrado["batalha"].unique())
    )

    # -------------------------------------------------
    # -------PROCESSANDO OS DADOS COM FILTRO-----------
    # -------------------------------------------------

    # TABELA DE KDA
    df_filtrado = df_filtrado.loc[df_filtrado["batalha"] == partida]
    kda = pd.pivot(
        df_filtrado,
        columns=["team"],
        values=["kills", "deaths", "assists", "KDA"],
        index=["positionPlayed"],
    )
    kda = kda.swaplevel(0, 1, axis=1).sort_index(axis=1)

    kda = kda[kda.columns.set_levels(["kills", "deaths", "assists", "KDA"], level=1)]
    kda = kda.rename(
        columns={"kills": "Abates", "deaths": "Mortes", "assists": "Assist."}
    )

    kda = kda.loc[["baron", "jungler", "mid", "dragon", "support"], :]

    # NOME DO TIME E DIVISÃO DA TABELA KDA
    first_team = kda.iloc[:, :4]
    name_temp = first_team.columns[0]
    name_first_team = name_temp[0]
    first_team.columns = first_team.columns.droplevel(0)

    last_team = kda.iloc[:, 4:8]
    name_temp = last_team.columns[0]
    name_last_team = name_temp[0]
    last_team.columns = last_team.columns.droplevel(0)

    # LADO DO TIME
    side_temp = df_filtrado[df_filtrado["team"] == name_first_team]
    side_first_team = side_temp.iloc[0]["side"]

    side_temp = df_filtrado[df_filtrado["team"] == name_last_team]
    side_last_team = side_temp.iloc[0]["side"]

    # RESULTADO
    result_first_team = side_temp.iloc[0]["result"]
    if result_first_team == 0:
        resultado_first_team = "Vencedor"
        resultado_last_team = "Perdedor"
    else:
        resultado_first_team = "Perdedor"
        resultado_last_team = "Vencedor"

    # TABELA DE DANO E OURO
    dano_gold = pd.pivot(
        df_filtrado,
        columns=["team"],
        values=[
            "champion",
            "killParticipationRate",
            "totalDamageDealtToChampions",
            "totalGolds3",
        ],
        index=["positionPlayed"],
    )
    dano_gold = dano_gold.swaplevel(0, 1, axis=1).sort_index(axis=1)

    dano_gold = dano_gold[
        dano_gold.columns.set_levels(
            [
                "champion",
                "killParticipationRate",
                "totalDamageDealtToChampions",
                "totalGolds3",
            ],
            level=1,
        )
    ]
    dano_gold = dano_gold.rename(
        columns={
            "killParticipationRate": "%KP",
            "totalDamageDealtToChampions": "Dano",
            "totalGolds3": "Ouro",
        }
    )

    dano_gold = dano_gold.loc[["baron", "jungler", "mid", "dragon", "support"], :]

    # DIVISÃO DA TABELA DE DANO E OURO
    first_team_dano = dano_gold.iloc[:, :4]
    first_team_dano.columns = first_team_dano.columns.droplevel(0)
    first_team_dano = first_team_dano.reset_index()
    first_team_dano = first_team_dano.drop(columns=["positionPlayed"])

    last_team_dano = dano_gold.iloc[:, 4:8]
    last_team_dano.columns = last_team_dano.columns.droplevel(0)
    last_team_dano = last_team_dano.reset_index()
    last_team_dano = last_team_dano.drop(columns=["positionPlayed"])

    # TABELA DE OBJETIVO
    df_obj = pd.pivot_table(
        df_filtrado,
        columns=["team"],
        values=["dragonsKills", "heraldKills", "baronKills"],
        aggfunc=np.sum,
    )

    # FORMATAÇÃO DAS TABELAS
    first_team = (
        first_team.style.format(subset=first_team.columns[0], formatter="{:.0f}")
        .format(subset=first_team.columns[1], formatter="{:.0f}")
        .format(subset=first_team.columns[2], formatter="{:.0f}")
        .format(subset=first_team.columns[3], formatter="{:.2f}")
    )

    last_team = (
        last_team.style.format(subset=first_team.columns[0], formatter="{:.0f}")
        .format(subset=first_team.columns[1], formatter="{:.0f}")
        .format(subset=first_team.columns[2], formatter="{:.0f}")
        .format(subset=first_team.columns[3], formatter="{:.2f}")
    )

    first_team_dano = first_team_dano.style.format(
        subset=first_team_dano.columns[2], formatter="{:.0f}"
    )

    last_team_dano = last_team_dano.style.format(
        subset=last_team_dano.columns[2], formatter="{:.0f}"
    )

    df_obj = df_obj.style.format(subset=df_obj.columns[0], formatter="{:.0f}").format(
        subset=df_obj.columns[1], formatter="{:.0f}"
    )

    # JUNTANDO TEXTOS
    primeiro_time = (
        name_first_team + " - " + resultado_first_team + " - " + side_first_team
    )
    ultimo_time = name_last_team + " - " + resultado_last_team + " - " + side_last_team

    # TEMPO
    tempo = df_filtrado["secondsInGame"].iat[0]
    tempo_texto = time.strftime("%M:%S", time.gmtime(tempo))

    # -------------------------------------------------
    # -------COLOCANDO OS DADOS NA TELA----------------
    # -------------------------------------------------
    texto = "Dados Gerais - " + tempo_texto
    st.title(texto)
    col1, col2 = st.columns([1, 1])
    col3, col4 = st.columns([1, 1])

    with col1:
        st.subheader(primeiro_time)
        st.table(first_team)
        st.table(first_team_dano)
    with col2:
        st.subheader(ultimo_time)
        st.table(last_team)
        st.table(last_team_dano)

    with col3:
        st.bar_chart(df_obj)
    with col4:
        st.table(df_obj)

    # -------------------------------------------------
    # ------------------ DADOS OURO :)----------------
    # -------------------------------------------------

    # -------------------------------------------------
    # -------PROCESSANDO OS DADOS----------------------
    # -------------------------------------------------
    # COLOCANDO O GRÁFICO DE OURO
    col8, col9, col10 = st.columns([0.9, 0.55, 0.55])
    with col8:
        st.subheader("Gráfico de ouro")
    with col9:
        vis_time_jog = st.multiselect("Visão:", ["team", "player"], ["player"])
    with col10:
        vis_lado = st.selectbox("Perspectiva:", ("blue", "red"))

    col5, col6, col7 = st.columns([0.45, 0.45, 1.1])
    with col5:
        vis_graf_ouro = st.multiselect("Tipo:", ["gold", "diff"], ["gold", "diff"])
    with col6:
        times = df_filtrado["team"].unique()
        team = st.multiselect("Time:", times, times[:2])
    with col7:
        posicoes = df_filtrado["positionPlayed"].unique()
        position = st.multiselect("Posição:", posicoes, posicoes[:5])

    if (gd.tamanho_lista(team) > 0) and (gd.tamanho_lista(position) > 0):
        lista_ouro = ["team", "positionPlayed"]
    elif gd.tamanho_lista(team) > 0:
        lista_ouro = ["team"]
    elif gd.tamanho_lista(position) > 0:
        lista_ouro = ["positionPlayed"]

    if (gd.tamanho_lista(team) > 0) or (gd.tamanho_lista(position) > 0):
        tempo = df_filtrado["secondsInGame"].iat[0]

        ouroDividido = df_filtrado[["goldSnapshot"]].copy()
        ouroDividido = (
            ouroDividido["goldSnapshot"].astype(str).str.replace(r"\[|\]|", "")
        )
        ouroDividido = ouroDividido.str.split(",", expand=True)
        colunasOuro = len(ouroDividido.columns)
        i = 0
        while i != colunasOuro:
            ouroDividido = ouroDividido.rename({i: str(i + 1)}, axis="columns")
            i = i + 1

        ouroDividido[0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        colunasOuro = len(ouroDividido.columns)
        i = 0
        tempoDividido = tempo / colunasOuro
        tempoFim = 0
        while i != colunasOuro:
            ouroDividido = ouroDividido.rename({str(i): tempoFim}, axis="columns")
            tempoFim = tempoFim + tempoDividido
            i = i + 1

        ouroDividido = ouroDividido.reset_index()

        # DIFFGOLD
        ouroDiff = ouroDividido.astype(int)
        ouroDiff.loc["mid"] = ouroDiff.loc[0] - ouroDiff.loc[5]
        ouroDiff.loc["baron"] = ouroDiff.loc[1] - ouroDiff.loc[6]
        ouroDiff.loc["dragon"] = ouroDiff.loc[2] - ouroDiff.loc[7]
        ouroDiff.loc["jungler"] = ouroDiff.loc[3] - ouroDiff.loc[8]
        ouroDiff.loc["support"] = ouroDiff.loc[4] - ouroDiff.loc[9]
        ouroDiff = ouroDiff.tail(ouroDiff.shape[0] - 10)
        ouroDiff = ouroDiff.drop(columns=["index"])
        ouroDiff = ouroDiff.assign(
            positionPlayed=["mid", "baron", "dragon", "jungler", "support"]
        )

        positionPlayed = df_filtrado[lista_ouro].copy()
        positionPlayed = positionPlayed.reset_index()

        ouroDividido = ouroDividido.merge(positionPlayed, how="left", on="index")

        if (gd.tamanho_lista(team) > 0) and (gd.tamanho_lista(position) > 0):
            ouroDividido = ouroDividido.query(
                "(team == @team) and (positionPlayed == @position)"
            )
            ouroDiff = ouroDiff.query("(positionPlayed == @position)")
        elif gd.tamanho_lista(team) > 0:
            ouroDividido = ouroDividido.query("(team == @team)")
        elif gd.tamanho_lista(position) > 0:
            ouroDividido = ouroDividido.query("(positionPlayed == @position)")
            ouroDiff = ouroDiff.query("(positionPlayed == @position)")

        # novo gráfico - agrupamento de ouro (diferença dos jogadores)
        ouroAgrupadoTeam = ouroDiff
        ouroAgrupadoTeam["positionPlayed"] = "diff"
        ouroAgrupadoTeam = ouroDiff.groupby(by=["positionPlayed"]).sum()
        ouroAgrupadoTeam = ouroAgrupadoTeam.T

        # Tratando tabela de ouro diff após o filtro
        ouroDiff = ouroDiff.drop(columns=["positionPlayed"])
        ouroDiff = ouroDiff.T

        # Invertendo conforme lado
        if vis_lado == "red":
            ouroDiff = ouroDiff.mul(-1)

        # novo gráfico - agrupamento de ouro (valor constante)
        ouroAgrupado = ouroDividido
        ouroAgrupado = ouroAgrupado.drop(columns=["positionPlayed"])
        ouroAgrupado = ouroAgrupado.apply(pd.to_numeric, errors="ignore")
        ouroAgrupado = ouroAgrupado.set_index("team")
        ouroAgrupado = ouroAgrupado.drop(columns=["index"])
        ouroAgrupado = ouroAgrupado.groupby(by=["team"]).sum()
        ouroAgrupado = ouroAgrupado.T
        # lines = ouroAgrupado.plot.line()

        # Tratando tabela de ouro após o filtro
        ouroDividido["positionPlayed"] = (
            ouroDividido["positionPlayed"] + ouroDividido["team"]
        )
        ouroDividido = ouroDividido.drop(columns=["team"])

        ouroDividido = ouroDividido.set_index("positionPlayed")
        ouroDividido = ouroDividido.drop(columns=["index"])

        ouroDividido = ouroDividido.T
        # ouroDividido = ouroDividido.append(dict(zip(ouroDividido.columns,[0, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500])), ignore_index=True)
        ouroDividido = ouroDividido.apply(pd.to_numeric, errors="ignore")

        # lines = ouroDividido.plot.line()

        # -------------------------------------------------
        # -------COLOCANDO OS DADOS NA TELA----------------
        # -------------------------------------------------
        if "player" in vis_time_jog and "team" in vis_time_jog:
            if "diff" in vis_graf_ouro:
                textoDiff = "Diferença de ouro - " + vis_lado
                st.subheader(textoDiff)
                st.line_chart(ouroDiff)
                st.subheader("Diferença de ouro agrupado")
                st.line_chart(ouroAgrupadoTeam)
            if "gold" in vis_graf_ouro:
                st.subheader("Ouro dos jogadores")
                st.line_chart(ouroDividido)
                st.subheader("Ouro dos jogadores agrupado")

                st.line_chart(ouroAgrupado)
        elif "player" in vis_time_jog:
            if "diff" in vis_graf_ouro:
                textoDiff = "Diferença de ouro - " + vis_lado
                st.subheader(textoDiff)
                st.line_chart(ouroDiff)
            if "gold" in vis_graf_ouro:
                st.subheader("Ouro dos jogadores")
                st.line_chart(ouroDividido)

        elif "team" in vis_time_jog:
            if "diff" in vis_graf_ouro:
                st.subheader("Diferença de ouro agrupado")
                st.line_chart(ouroAgrupadoTeam)
            if "gold" in vis_graf_ouro:
                st.subheader("Ouro dos jogadores agrupado")
                st.line_chart(ouroAgrupado)
    else:
        st.text("Defina um filtro para visualizar gráfico de ouro")
