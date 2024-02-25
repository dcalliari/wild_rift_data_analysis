from data.imports import st
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
    lista_campeao = list(df["positionPlayed"].unique())
    lista_campeao.append("todas")
    rota = st.sidebar.selectbox("Rota:", options=lista_campeao)

    if rota != "todas":
        df = df.query("(positionPlayed == @rota)")
    df = df.reset_index()
    df = df.drop(columns=["index"])

    # battleType = st.sidebar.multiselect('Tipo de jogo:', options=df["battleType"].unique())
    team = st.sidebar.multiselect("Time:", options=df["team"].unique())
    side = st.sidebar.multiselect("Lado do mapa:", options=df["side"].unique())
    app = st.sidebar.multiselect("Versão do app:", options=df["app"].unique())

    # VERICICANDO ELEMENTOS DENTRO DA LISTA
    numero_time = gd.tamanho_lista(team)
    numero_tipo = 0  # tamanho_lista(battleType)
    numero_lado = gd.tamanho_lista(side)
    numero_versao = gd.tamanho_lista(app)

    # -------------------------------------------------
    # --------------SELECIONANDO FILTRO----------------
    # -------------------------------------------------
    if rota != "todas":
        lista = ["champion", "positionPlayed"]
    else:
        lista = ["champion"]

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

    # -------------------------------------------------
    # ---------------FILTRANDO OS DADOS----------------
    # -------------------------------------------------

    time = "(team == @team)"
    tipo = "(battleType == @battleType)"
    lado = "(side == @side)"
    versao = "(app == @app)"

    # 1 escolha
    if numero_time > 0:
        df_media = df_media.query(time)
    if numero_tipo > 0:
        df_media = df_media.query(tipo)
    if numero_lado > 0:
        df_media = df_media.query(lado)
    if numero_versao > 0:
        df_media = df_media.query(versao)

    # -------------------------------------------------
    # -------COLOCANDO OS DADOS NA TELA----------------
    # -------------------------------------------------
    texto = "Ranking dos Personagem"
    st.header(texto)
    st.text(
        "É possível clicar na tabela para visualizar os dados por ordem crescente/decrescente"
    )
    st.dataframe(df_media.style.format(precision=2))
