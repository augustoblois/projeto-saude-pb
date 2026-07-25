"""Painel — Mapa de Evasão Assistencial da Paraíba.

Consome APENAS as pré-agregações congeladas em `data/processed/` (produzidas pelos
notebooks `01-*`). Nenhuma interação do usuário recalcula nada a partir da base bruta,
e nada aqui depende de rede: o painel roda com a internet desligada.

Execução:  streamlit run app.py
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DIR_PROCESSED = Path(__file__).parent / "data" / "processed"
DIR_OUTPUTS = Path(__file__).parent / "outputs"

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

TODOS = "Todos"


# --------------------------------------------------------------------------- #
# Carga (cacheada: lê do disco uma vez por sessão, não a cada clique)
# --------------------------------------------------------------------------- #
@st.cache_data
def carregar_matriz_municipal() -> pd.DataFrame:
    return pd.read_parquet(DIR_PROCESSED / "matriz_od_municipal_mensal.parquet")


@st.cache_data
def carregar_matriz_regional() -> pd.DataFrame:
    return pd.read_csv(DIR_PROCESSED / "matriz_od_regional_mensal.csv")


@st.cache_data
def carregar_malha() -> dict:
    """Malha dos 223 municípios da PB, congelada em outputs/ (IBGE, ver src/baixar_malha_pb.py)."""
    with open(DIR_OUTPUTS / "malha_municipios_pb.geojson", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def carregar_centroides() -> pd.DataFrame:
    """Ponto central de cada município — origem e destino das linhas de fluxo."""
    return pd.read_csv(DIR_OUTPUTS / "centroides_municipios_pb.csv", dtype={"cod_mun": str})


# --------------------------------------------------------------------------- #
# Filtro (função pura — o mesmo código é exercitado pelo script de verificação)
# --------------------------------------------------------------------------- #
def filtrar(df: pd.DataFrame, col_origem: str, origem: str, mes: str) -> pd.DataFrame:
    """Aplica os filtros de origem e mês. `TODOS` em qualquer um deles = sem filtro."""
    if origem != TODOS:
        df = df[df[col_origem] == origem]
    if mes != TODOS:
        df = df[df["mes"] == int(mes)]
    return df


def formatar_mes(valor) -> str:
    return TODOS if valor == TODOS else MESES[int(valor)]


# --------------------------------------------------------------------------- #
# Aba: matriz origem → destino
# --------------------------------------------------------------------------- #
def aba_matriz() -> None:
    st.subheader("Matriz origem → destino das internações (SIH/DATASUS, 2025)")
    st.caption(
        "Cada linha é um fluxo: de onde o paciente **mora** para onde ele foi **internado**. "
        "A unidade é a AIH (Autorização de Internação Hospitalar) — uma internação paga pelo SUS."
    )

    nivel = st.radio(
        "Nível de detalhe",
        ["Município", "Região de saúde"],
        horizontal=True,
        help="Município mostra o fluxo cidade a cidade; região agrega nas 16 regiões de saúde da PB.",
    )

    if nivel == "Município":
        df = carregar_matriz_municipal()
        col_origem, col_destino, col_evasao = "nome_mun_res", "nome_mun_int", "evasao_municipal"
        rotulo_origem = "Município de residência"
    else:
        df = carregar_matriz_regional()
        col_origem, col_destino, col_evasao = "regiao_res", "regiao_int", "evasao_regional"
        rotulo_origem = "Região de saúde de residência"

    col_a, col_b = st.columns(2)
    with col_a:
        origem = st.selectbox(
            rotulo_origem,
            [TODOS] + sorted(df[col_origem].unique()),
        )
    with col_b:
        mes = st.selectbox(
            "Mês de 2025",
            [TODOS] + sorted(df["mes"].unique()),
            format_func=formatar_mes,
        )

    filtrado = filtrar(df, col_origem, origem, mes)

    total = int(filtrado["internacoes"].sum())
    fora = int(filtrado.loc[filtrado[col_evasao], "internacoes"].sum())
    pct_fora = 100 * fora / total if total else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric("Internações no recorte", f"{total:,}".replace(",", "."))
    m2.metric("Internações fora da origem", f"{fora:,}".replace(",", "."))
    m3.metric("% que saiu da origem", f"{pct_fora:.1f}%".replace(".", ","))

    if total == 0:
        st.info("Nenhuma internação neste recorte.")
        return

    tabela = (
        filtrado.groupby([col_origem, col_destino], as_index=False)["internacoes"]
        .sum()
        .sort_values("internacoes", ascending=False)
        .rename(
            columns={
                col_origem: "Origem (onde mora)",
                col_destino: "Destino (onde internou)",
                "internacoes": "Internações",
            }
        )
    )
    tabela["% do recorte"] = (100 * tabela["Internações"] / total).round(1)

    st.dataframe(tabela, width="stretch", hide_index=True)
    st.caption(
        f"{len(tabela)} pares origem→destino no recorte. "
        "A tabela é ordenável e o conteúdo pode ser copiado direto para citação."
    )


# --------------------------------------------------------------------------- #
# Aba: mapa dos fluxos
# --------------------------------------------------------------------------- #
@st.cache_data
def evasao_por_municipio(mes: str) -> pd.DataFrame:
    """Taxa de evasão de cada município da PB: % das internações dos seus moradores
    que aconteceu em hospital de outro município. Cacheada por mês."""
    df = carregar_matriz_municipal()
    df = df[df["uf_res"] == "PB"]
    df = filtrar(df, "nome_mun_res", TODOS, mes)
    # coluna auxiliar: o volume só conta como "fora" quando a internação foi em outro município
    df = df.assign(fora=df["internacoes"].where(df["evasao_municipal"], 0))
    tab = df.groupby(["cod_mun_res", "nome_mun_res"], as_index=False).agg(
        internacoes=("internacoes", "sum"),
        fora=("fora", "sum"),
    )
    tab["taxa_evasao_pct"] = (100 * tab["fora"] / tab["internacoes"]).round(1)
    return tab


@st.cache_data
def captacao_por_municipio(mes: str, min_municipios: int = 4) -> pd.DataFrame:
    """Para cada município da PB, PARA ONDE vai a maior parte dos seus moradores.

    É o que pinta o mapa: municípios que mandam sua gente para o mesmo hospital-polo
    recebem a mesma cor, e o mapa vira um mosaico de áreas de captação.
    Destinos que captam menos de `min_municipios` municípios viram "Outros", para a
    legenda não explodir em dezenas de cores indistinguíveis.
    """
    df = carregar_matriz_municipal()
    df = filtrar(df[df["uf_res"] == "PB"], "nome_mun_res", TODOS, mes)

    # soma o ano (ou o mês escolhido) ANTES de procurar o maior destino —
    # senão o "maior" seria o maior de um mês isolado, não do recorte.
    pares = df.groupby(["cod_mun_res", "nome_mun_res", "nome_mun_int"], as_index=False)[
        "internacoes"
    ].sum()
    principal = pares.loc[pares.groupby("cod_mun_res")["internacoes"].idxmax()].rename(
        columns={"nome_mun_int": "destino_principal", "internacoes": "internacoes_destino"}
    )

    tab = principal.merge(evasao_por_municipio(mes), on=["cod_mun_res", "nome_mun_res"])
    tab["pct_destino"] = (100 * tab["internacoes_destino"] / tab["internacoes"]).round(1)

    captadores = tab["destino_principal"].value_counts()
    principais = captadores[captadores >= min_municipios].index
    tab["captador"] = tab["destino_principal"].where(
        tab["destino_principal"].isin(principais), "Outros"
    )
    return tab


@st.cache_data
def maiores_fluxos(mes: str, quantos: int) -> pd.DataFrame:
    """Os N maiores fluxos entre municípios diferentes, já com as coordenadas
    de origem e destino prontas para virar linha no mapa."""
    df = carregar_matriz_municipal()
    df = filtrar(df[df["evasao_municipal"] & (df["uf_res"] == "PB")], "nome_mun_res", TODOS, mes)
    pares = (
        df.groupby(["cod_mun_res", "nome_mun_res", "cod_mun_int", "nome_mun_int"], as_index=False)[
            "internacoes"
        ]
        .sum()
        .nlargest(quantos, "internacoes")
    )
    cent = carregar_centroides()
    pares = pares.merge(
        cent.rename(columns={"cod_mun": "cod_mun_res", "lon": "lon_res", "lat": "lat_res"})[
            ["cod_mun_res", "lon_res", "lat_res"]
        ],
        on="cod_mun_res",
        how="left",
    ).merge(
        cent.rename(columns={"cod_mun": "cod_mun_int", "lon": "lon_int", "lat": "lat_int"})[
            ["cod_mun_int", "lon_int", "lat_int"]
        ],
        on="cod_mun_int",
        how="left",
    )
    return pares


@st.cache_data
def polos_receptores(mes: str, quantos: int = 6) -> pd.DataFrame:
    """Municípios que mais internam gente de fora — os polos concentradores."""
    df = carregar_matriz_municipal()
    df = filtrar(df[df["evasao_municipal"]], "nome_mun_res", TODOS, mes)
    polos = (
        df.groupby(["cod_mun_int", "nome_mun_int"], as_index=False)["internacoes"]
        .sum()
        .nlargest(quantos, "internacoes")
    )
    cent = carregar_centroides()
    return polos.merge(
        cent.rename(columns={"cod_mun": "cod_mun_int"})[["cod_mun_int", "lon", "lat"]],
        on="cod_mun_int",
        how="left",
    )


def montar_mapa(mes: str, quantos_fluxos: int) -> go.Figure:
    """Três camadas: cores (evasão por origem), linhas (maiores fluxos) e polos.

    Usa `px.choropleth` (projeção geográfica pura), NUNCA a variante mapbox:
    mapbox baixaria tiles pela internet e quebraria o requisito de rodar offline.
    """
    captacao = captacao_por_municipio(mes)

    # ordem da legenda: quem capta mais municípios primeiro, "Outros" sempre por último
    ordem = [c for c in captacao["captador"].value_counts().index if c != "Outros"]
    tem_outros = "Outros" in captacao["captador"].values

    # uma cor distinta por polo — cor repetida daria a entender que duas cidades são
    # o mesmo polo. Paleta montada à mão: Dark24 traz tons quase pretos que somem no
    # tema escuro do painel, e cinzas que se confundiriam com o "Outros".
    paleta = px.colors.qualitative.Bold[:10] + px.colors.qualitative.Vivid[:10]
    cores = dict(zip(ordem, paleta))
    if tem_outros:
        ordem.append("Outros")
        cores["Outros"] = "#9aa0a6"

    fig = px.choropleth(
        captacao,
        geojson=carregar_malha(),
        locations="cod_mun_res",
        featureidkey="properties.cod_mun",
        color="captador",
        category_orders={"captador": ordem},
        color_discrete_map=cores,
        hover_name="nome_mun_res",
        hover_data={
            "cod_mun_res": False,
            "captador": False,
            "destino_principal": True,
            "pct_destino": ":.1f",
            "internacoes": ":,",
            "taxa_evasao_pct": ":.1f",
        },
        labels={
            "destino_principal": "Vai mais para",
            "pct_destino": "% dos moradores que vai para lá",
            "internacoes": "Internações de moradores",
            "taxa_evasao_pct": "% que se interna fora do município",
        },
    )
    fig.update_traces(marker_line_color="white", marker_line_width=0.4)

    fluxos = maiores_fluxos(mes, quantos_fluxos)
    maior = fluxos["internacoes"].max() if len(fluxos) else 1
    for _, f in fluxos.iterrows():
        fig.add_trace(
            go.Scattergeo(
                lon=[f["lon_res"], f["lon_int"]],
                lat=[f["lat_res"], f["lat_int"]],
                mode="lines",
                # quase-preto translúcido: precisa aparecer tanto sobre as cores de
                # captação quanto sobre o fundo claro do mapa (linha branca sumia no fundo)
                line=dict(width=0.6 + 5 * f["internacoes"] / maior, color="rgba(15,15,25,0.65)"),
                hoverinfo="text",
                text=f"{f['nome_mun_res']} → {f['nome_mun_int']}: "
                f"{f['internacoes']:,} internações".replace(",", "."),
                showlegend=False,
            )
        )

    polos = polos_receptores(mes)

    # Rótulos: quem está no litoral leste recebe o nome à esquerda (senão o texto sai
    # pela borda do mapa), e polos vizinhos demais ficam só com o marcador — dois nomes
    # sobrepostos são ilegíveis, e o maior deles é sempre o que interessa nomear.
    posicoes, rotulos, ja_rotulados = [], [], []
    for _, p in polos.sort_values("internacoes", ascending=False).iterrows():
        colide = any(
            abs(p["lon"] - lon) < 0.45 and abs(p["lat"] - lat) < 0.35
            for lon, lat in ja_rotulados
        )
        rotulos.append("" if colide else p["nome_mun_int"])
        posicoes.append("middle left" if p["lon"] > -35.4 else "top center")
        if not colide:
            ja_rotulados.append((p["lon"], p["lat"]))
    polos = polos.sort_values("internacoes", ascending=False)

    fig.add_trace(
        go.Scattergeo(
            lon=polos["lon"],
            lat=polos["lat"],
            mode="markers+text",
            marker=dict(
                size=8 + 22 * polos["internacoes"] / polos["internacoes"].max(),
                color="rgba(15,15,15,0.9)",
                line=dict(width=1.5, color="white"),
            ),
            text=rotulos,
            textposition=posicoes,
            # nome em branco com contorno escuro: precisa continuar legível por cima
            # de qualquer uma das cores de captação
            textfont=dict(size=13, color="white", family="Arial Black"),
            hoverinfo="text",
            hovertext=[
                f"{n}: recebeu {v:,} internações de fora".replace(",", ".")
                for n, v in zip(polos["nome_mun_int"], polos["internacoes"])
            ],
            showlegend=False,
        )
    )

    # fitbounds enquadra a PB pelos próprios polígonos; visible=False remove
    # qualquer cenário de fundo (costa, países) — nada é buscado na rede.
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=620,
        legend=dict(title="Maioria se interna em", yanchor="top", y=0.98, xanchor="left", x=0.01),
        dragmode="pan",
    )
    return fig


def aba_mapa() -> None:
    st.subheader("Para onde os paraibanos se deslocam para internar")
    st.caption(
        "Cada município está pintado com a **cor da cidade onde a maioria dos seus moradores "
        "acaba internada** — municípios da mesma cor formam a área de captação de um mesmo polo. "
        "As **linhas** são os maiores fluxos, com espessura proporcional ao volume, e os "
        "**pontos escuros** marcam os municípios que mais recebem gente de fora."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        mes = st.selectbox(
            "Mês de 2025",
            [TODOS] + list(range(1, 13)),
            format_func=formatar_mes,
            key="mapa_mes",
        )
    with col_b:
        quantos = st.slider("Quantos fluxos mostrar", 5, 60, 25, step=5)

    st.plotly_chart(montar_mapa(str(mes), quantos), width="stretch")

    polos = polos_receptores(str(mes), quantos=2)
    total_polos = int(polos["internacoes"].sum())
    st.caption(
        f"Só {polos.iloc[0]['nome_mun_int']} e {polos.iloc[1]['nome_mun_int']} receberam "
        f"{total_polos:,}".replace(",", ".")
        + " internações de moradores de outros municípios no recorte selecionado."
    )


# --------------------------------------------------------------------------- #
# Abas ainda não construídas (US-13, US-14)
# --------------------------------------------------------------------------- #
def aba_em_construcao(nome: str, story: str) -> None:
    st.subheader(nome)
    st.info(f"Aba em construção — entrega da story {story}.")


# --------------------------------------------------------------------------- #
def main() -> None:
    st.set_page_config(page_title="Evasão Assistencial — PB", layout="wide")
    st.title("Mapa de Evasão Assistencial da Paraíba")
    st.caption(
        "Para onde os paraibanos vão se internar — matriz origem→destino do SIH/DATASUS, "
        "ano de 2025, dados congelados localmente (o painel funciona sem internet)."
    )

    matriz, mapa, indice, achados = st.tabs(
        ["Matriz O-D", "Mapa", "Índice de dependência", "Achados & recomendações"]
    )
    with matriz:
        aba_matriz()
    with mapa:
        aba_mapa()
    with indice:
        aba_em_construcao("Índice de dependência por região de saúde", "US-13")
    with achados:
        aba_em_construcao("Achados & recomendações", "US-14")


if __name__ == "__main__":
    main()
