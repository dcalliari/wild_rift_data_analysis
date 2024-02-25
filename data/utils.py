from data.imports import pd


class GameData:
    def __init__(self):
        self.df = pd.read_csv("data/raw_game_data/df_final_liberty.csv", sep=";")

    def tamanho_lista(self, lista):
        if not lista:
            return 0
        else:
            return len(lista)

    def minimo_valor(tupla):
        return tupla[0]

    def maximo_valor(tupla):
        return tupla[1]

    def add_elem_cria_lista(self, lista, elem):
        lista = [*lista]
        lista.append(elem)
        return lista

    def groupby_mean_merge(self, df, df_fim, lista, coluna):
        df_temp = df.groupby(lista)[coluna].mean()
        df_fim = df_fim.merge(df_temp, how="left", on=lista)
        return df_fim

    def winrate_merge(self, df_obj, lista, lista_resultado, objetivo, nome_objetivo):
        total = "total" + nome_objetivo
        wr = "%WR" + nome_objetivo
        df_total = df_obj.groupby(lista)[objetivo].count().rename(total)
        df_perc_obj = df_obj.groupby(lista_resultado)[objetivo].count().rename(wr)
        df_perc_obj = df_perc_obj.reset_index()
        df_perc_obj = df_perc_obj.merge(df_total, how="left", on=lista)
        df_perc_obj = df_perc_obj[df_perc_obj.result != 0]
        df_perc_obj = df_perc_obj.drop(columns=["result"])
        df_perc_obj[wr] = (df_perc_obj[wr] / df_perc_obj[total]) * 100
        df_perc_obj = df_perc_obj.drop(columns=[total])
        return df_perc_obj

    def calcula_porc_obj_merge(self, df, df_fim, lista, coluna, objetivo):
        df_temp = df.loc[
            df.groupby("ID")[coluna].transform("min").eq(df[coluna])
        ].reset_index(drop=True)
        df_temp = df_temp.groupby(lista)[coluna].count().rename(objetivo)
        df_fim = df_fim.merge(df_temp, how="left", on=lista)
        porcentagem = "% " + objetivo
        df_fim[porcentagem] = df_fim[objetivo] / df_fim["ID"]
        df_fim[porcentagem] = df_fim[porcentagem] * 100
        df_fim = df_fim.drop(columns=[objetivo])
        return df_fim

    def df_inimigo_obj(self, df, df_origem, tam_df_original):
        i = 0

        # CRIANDO A TABELA DE PERSONAGENS JOGADOS COM E CONTRA
        while i != tam_df_original:
            lado = df["side"][i]
            chave = df["ID"][i]
            if lado == "blue":
                lado_oposto = "red"
            else:
                lado_oposto = "blue"
            pick_inimigo = df_origem.query("(side == @lado_oposto) and (ID == @chave)")

            if i == 0:
                df_inimigo = pick_inimigo
            else:
                df_inimigo = pd.concat([df_inimigo, pick_inimigo])
            i = i + 1
        return df_inimigo

    def process_game_data(self):
        self.df["secondsInGame"] = pd.to_numeric(
            self.df["secondsInGame"], errors="coerce"
        )
        df = self.df.dropna(subset=["secondsInGame"])
        df = df[df["secondsInGame"] >= 600]
        return df
