"""Recalcula, da base congelada, os números citados na narrativa executiva.

Por que este script existe
--------------------------
A regra RNF-05 do projeto diz que nenhum número do texto pode ser digitado à mão: todo
número precisa sair de um notebook ou script versionado. A maior parte dos números da
narrativa vem dos notebooks `01-*.ipynb`. Três blocos, porém, são recortes feitos
especificamente para o texto executivo e não têm notebook próprio:

1. a taxa de evasão municipal contando **só** residentes da PB (o texto fala de
   "paraibanos", então o denominador correto exclui quem mora fora e veio internar aqui);
2. a taxa de evasão **regional** do estado inteiro (a "taxa estadual" de comparação);
3. o **destino principal de cada uma das 8 regiões de dependência alta** — a tabela que
   sustenta a recomendação R2.

Este script recalcula esses três blocos direto de `data/processed/`, para que qualquer
pessoa possa conferir o texto sem abrir notebook nenhum.

Execução:  python src/conferir_narrativa.py
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).parent.parent
DIR_PROCESSED = RAIZ / "data" / "processed"

FORA_DA_PB = "Fora da PB"

# As 8 regiões de dependência alta, na ordem do ranking do índice (US-10).
# Lidas do arquivo, não fixadas no código — se o índice mudar, a lista acompanha.
FAIXA_ALTA = "alta"


def carregar_base() -> pd.DataFrame:
    return pd.read_parquet(DIR_PROCESSED / "sih_pb_2025_regioes.parquet")


def taxas_globais(df: pd.DataFrame) -> dict[str, float | int]:
    """Os números de tamanho do problema (seção 1 do sumário de evidências)."""
    residentes = df[df["regiao_res"] != FORA_DA_PB]

    fora_mun_todos = int((df["nome_mun_res"] != df["nome_mun_mov"]).sum())
    fora_mun_res = int((residentes["nome_mun_res"] != residentes["nome_mun_mov"]).sum())
    fora_reg_res = int((residentes["regiao_res"] != residentes["regiao_int"]).sum())

    return {
        "E-01 internações em hospitais da PB": len(df),
        "E-02 internações de residentes da PB": len(residentes),
        "E-03 fora do município (todas)": fora_mun_todos,
        "E-03 %": round(fora_mun_todos / len(df) * 100, 1),
        "E-04 fora do município (só residentes)": fora_mun_res,
        "E-04 %": round(fora_mun_res / len(residentes) * 100, 1),
        "E-05 fora da região (só residentes)": fora_reg_res,
        "E-05 %": round(fora_reg_res / len(residentes) * 100, 1),
    }


def destino_principal_das_criticas() -> pd.DataFrame:
    """Para onde vai quem sai de cada região de dependência alta (tabela 3.1).

    A pergunta que esta tabela responde: a dependência é difusa (um pouco para cada
    vizinho) ou concentrada em um endereço só? A resposta muda a recomendação — pactuar
    com muitos é diferente de pactuar com um.
    """
    indice = pd.read_csv(DIR_PROCESSED / "indice_dependencia_regional.csv")
    criticas = indice.loc[indice["faixa_dependencia"] == FAIXA_ALTA, "regiao"]

    matriz = pd.read_csv(DIR_PROCESSED / "matriz_od_regional_mensal.csv")
    anual = matriz.groupby(["regiao_res", "regiao_int"])["internacoes"].sum().reset_index()

    linhas = []
    for regiao in criticas:
        saidas = anual[(anual["regiao_res"] == regiao) & (anual["regiao_int"] != regiao)]
        maior = saidas.loc[saidas["internacoes"].idxmax()]
        total = int(saidas["internacoes"].sum())
        linhas.append({
            "regiao": regiao,
            "destino_principal": maior["regiao_int"],
            "internacoes_no_destino": int(maior["internacoes"]),
            "total_de_saidas": total,
            "pct_das_saidas": round(maior["internacoes"] / total * 100, 1),
        })
    return pd.DataFrame(linhas)


def main() -> None:
    df = carregar_base()

    print("=" * 70)
    print("Seção 1 do sumário — o tamanho do problema")
    print("=" * 70)
    for rotulo, valor in taxas_globais(df).items():
        print(f"  {rotulo:42s} {valor:>10}")

    print()
    print("=" * 70)
    print("Seção 3.1 do sumário — destino principal das 8 regiões críticas")
    print("=" * 70)
    print(destino_principal_das_criticas().to_string(index=False))

    concentradas = (destino_principal_das_criticas()["pct_das_saidas"] > 50).sum()
    print(f"\n  Regiões críticas cuja MAIORIA das saídas vai para um único destino: "
          f"{concentradas} de 8")


if __name__ == "__main__":
    main()
