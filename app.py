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
DIR_DOCS = Path(__file__).parent / "docs"
DIR_REPORTS = Path(__file__).parent / "reports"

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

TODOS = "Todos"

# Faixas da definição (docs/dados/definicao-indice-dependencia.md, seção 5). Cores escolhidas
# para funcionar tanto no tema claro quanto no escuro — e a leitura não depende só delas:
# a faixa também vem escrita por extenso na tabela e no cartão da região.
CORES_FAIXA = {"baixa": "#2e9e6b", "média": "#d9a12b", "alta": "#c0433a"}

# Tradução dos códigos ESPEC (especialidade do leito) do SIH — nenhum código aparece
# na tela, só o nome. Mesma tabela usada no notebook 01-pa6-perfil-demanda.ipynb.
ESPEC_NOMES = {
    "01": "Cirúrgico", "02": "Obstétrico", "03": "Clínico", "04": "Crônicos",
    "05": "Psiquiatria", "06": "Pneumologia sanitária", "07": "Pediátrico",
    "08": "Reabilitação", "09": "Leito dia — cirúrgico", "10": "Leito dia — Aids",
    "87": "Saúde mental",
}

# Ordem e cor de cada uma das seis caixas da régua de classificação da evasão
# (notebooks/01-pa6-perfil-demanda.ipynb, seção 3) — mesma paleta usada lá, para que
# quem olha o notebook e o painel reconheça a mesma cor com o mesmo significado.
TIPOS_EVASAO_ORDEM = [
    "Referência legítima", "Alta complexidade eletiva", "Urgência cirúrgica sem retaguarda",
    "Demanda represada", "Evasão evitável", "Não classificado",
]
CORES_TIPO_EVASAO = {
    "Referência legítima": "#1E8449",
    "Alta complexidade eletiva": "#2E86C1",
    "Urgência cirúrgica sem retaguarda": "#6C3483",
    "Demanda represada": "#B9770E",
    "Evasão evitável": "#B03A2E",
    "Não classificado": "#BFC9CA",
}
# O que cada caixa significa e a ação que ela implica para a gestão — mesmo par
# significado/ação decidido no notebook (dicionário `acao_por_tipo`), só reescrito em
# linguagem de gestor para o `help=` dos cartões do painel.
CATEGORIA_EVASAO_INFO = {
    "Referência legítima": (
        "Internação de alta complexidade com uso de UTI — o encaminhamento para outra "
        "região é o funcionamento correto do sistema.",
        "Não instalar estrutura nova: pactuar fluxo, regulação e transporte sanitário.",
    ),
    "Alta complexidade eletiva": (
        "Cirurgia de alta complexidade agendada (perfil oncológico/cardiovascular), sem "
        "UTI — é uma referência legítima, mas com fila.",
        "Pactuar o fluxo e garantir agenda/regulação — não duplicar a estrutura.",
    ),
    "Urgência cirúrgica sem retaguarda": (
        "Cirurgia de urgência que precisou atravessar região por falta de retaguarda "
        "cirúrgica 24h na origem.",
        "Retaguarda cirúrgica de urgência / sobreaviso 24h — não resolve com mutirão.",
    ),
    "Demanda represada": (
        "Fila de cirurgia eletiva comum (não é urgência) que não coube na agenda local.",
        "Mutirão ou ampliação da agenda cirúrgica local.",
    ),
    "Evasão evitável": (
        "Internação clínica, obstétrica ou pediátrica comum que faltou estrutura para "
        "resolver na própria região.",
        "Reforçar capacidade local: equipe, plantão, leitos.",
    ),
    "Não classificado": (
        "Não se encaixa em nenhuma das cinco regras da régua de classificação.",
        "Sem ação padrão — precisa investigação caso a caso.",
    ),
}


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
def carregar_indice() -> pd.DataFrame:
    """Índice de dependência das 16 regiões, já calculado e ranqueado no notebook
    `01-indice-dependencia.ipynb`. O painel só exibe — não recalcula nada aqui."""
    return pd.read_csv(DIR_PROCESSED / "indice_dependencia_regional.csv")


@st.cache_data
def carregar_definicao() -> list[tuple[str, str]]:
    """Seções numeradas da definição aprovada na US-09, lidas do próprio documento.

    Ler o arquivo em vez de copiar o texto para dentro do painel é deliberado: o critério
    de aceite pede o texto **tal-qual aprovado**, e duas cópias divergiriam no primeiro
    ajuste de redação. É leitura de arquivo local — o painel continua rodando offline.
    O "Roteiro de teste de leitura" fica de fora: é processo interno do projeto, não
    informação para quem consulta o índice.
    """
    bruto = (DIR_DOCS / "dados" / "definicao-indice-dependencia.md").read_text(encoding="utf-8")
    secoes = []
    for bloco in bruto.split("\n## ")[1:]:
        titulo, _, corpo = bloco.partition("\n")
        if not titulo[:1].isdigit():  # só as seções numeradas 1..7
            continue
        corpo = corpo.strip().removesuffix("---").strip()  # tira o separador final
        secoes.append((titulo.strip(), corpo))
    return secoes


@st.cache_data
def carregar_narrativa() -> list[tuple[str, str]]:
    """Seções numeradas da narrativa executiva (US-16), lidas do próprio documento.

    Mesmo motivo de `carregar_definicao`: o critério de aceite da US-14 exige fonte
    única — a aba exibe o texto de `reports/`, não uma cópia. Corrigir uma frase no
    documento corrige o painel junto, e nunca existem duas versões divergentes.
    O cabeçalho de contexto (antes da seção 1) fica de fora: é orientação para quem lê
    o arquivo no repositório, não para quem consulta o painel.
    """
    bruto = (DIR_REPORTS / "narrativa-executiva.md").read_text(encoding="utf-8")
    secoes = []
    for bloco in bruto.split("\n## ")[1:]:
        titulo, _, corpo = bloco.partition("\n")
        if not titulo[:1].isdigit():  # só as seções numeradas
            continue
        # "2. Achado 1 — ..." → "Achado 1 — ...": a numeração serve para ordenar o
        # arquivo, não para ser lida na tela.
        titulo = titulo.split(". ", 1)[-1].strip()
        corpo = corpo.strip().removesuffix("---").strip()
        secoes.append((titulo, corpo))
    return secoes


@st.cache_data
def carregar_malha() -> dict:
    """Malha dos 223 municípios da PB, congelada em outputs/ (IBGE, ver src/baixar_malha_pb.py)."""
    with open(DIR_OUTPUTS / "malha_municipios_pb.geojson", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def carregar_centroides() -> pd.DataFrame:
    """Ponto central de cada município — origem e destino das linhas de fluxo."""
    return pd.read_csv(DIR_OUTPUTS / "centroides_municipios_pb.csv", dtype={"cod_mun": str})


@st.cache_data
def carregar_recomendacao_regiao() -> pd.DataFrame:
    """Recomendação nominal por região (PA6): destino principal, especialidade de maior
    excesso e composição das seis caixas de evasão. Já ordenada por índice de dependência
    decrescente — as regiões prioritárias primeiro, mesmo critério do resto do painel."""
    df = pd.read_csv(DIR_OUTPUTS / "tables" / "pa6_recomendacao_regiao.csv")
    return df.sort_values("indice_dependencia_pct", ascending=False).reset_index(drop=True)


@st.cache_data
def carregar_assinatura_regiao() -> pd.DataFrame:
    """Assinatura de evasão por região × eixo × categoria (PA6): taxa de evasão da
    categoria menos a taxa geral da região (`excesso_pp`), com o piso de volume `n_min_ok`
    já calculado no notebook — o painel só filtra, não recalcula o piso."""
    return pd.read_csv(DIR_OUTPUTS / "tables" / "pa6_assinatura_regiao.csv")


@st.cache_data
def centroide_regioes() -> pd.DataFrame:
    """Ponto aproximado de cada região de saúde: média dos centroides dos municípios que
    a compõem. Não é um centroide geométrico da malha (o painel não usa geopandas) — é
    aproximado o bastante só para posicionar um marcador por região no mapa."""
    mapa = pd.read_csv(DIR_PROCESSED / "regioes_saude_pb.csv", dtype={"codigo_municipio": str})
    cent = carregar_centroides()
    juntos = mapa.merge(cent, left_on="codigo_municipio", right_on="cod_mun", how="inner")
    return juntos.groupby("nome_regiao_saude", as_index=False)[["lon", "lat"]].mean().rename(
        columns={"nome_regiao_saude": "regiao"}
    )


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


def mil(n: int) -> str:
    """10815 → '10.815'. Formata só o número: aplicar o replace na frase inteira
    trocaria também as vírgulas gramaticais do texto por pontos."""
    return f"{int(n):,}".replace(",", ".")


def pct(v: float) -> str:
    """84.5 → '84,5%'. Mesmo motivo do `mil`: o replace nunca encosta no texto."""
    return f"{v:.1f}%".replace(".", ",")


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


CAMADA_CAPTACAO = "Área de captação (padrão)"
CAMADA_TIPO_EVASAO = "Tipo de evasão dominante, por região"


def montar_mapa_tipo_evasao() -> go.Figure:
    """Camada opcional: um marcador por região de saúde, colorido pelo tipo de evasão que
    domina o volume evadido dela (PA6). A malha municipal continua de fundo, em cinza
    neutro, só para dar contexto geográfico — a informação nova está nos marcadores.

    Marcadores em vez de choropleth por região: a malha disponível é municipal, e o
    projeto não usa geopandas para dissolver polígonos por região (nenhuma dependência
    nova). Um marcador por região é estável e não arrisca um choropleth quebrado.
    """
    matriz = carregar_matriz_municipal()
    base = matriz.loc[matriz["uf_res"] == "PB", ["cod_mun_res"]].drop_duplicates()
    base["cor"] = "PB"
    fig = px.choropleth(
        base,
        geojson=carregar_malha(),
        locations="cod_mun_res",
        featureidkey="properties.cod_mun",
        color="cor",
        color_discrete_map={"PB": "#e9e9ec"},
    )
    fig.update_traces(marker_line_color="white", marker_line_width=0.4, showlegend=False)

    dados = carregar_recomendacao_regiao().merge(centroide_regioes(), on="regiao", how="left")
    sem_centro = dados[dados["lon"].isna()]
    if len(sem_centro):
        st.error(
            "Região sem centróide calculado: "
            f"{', '.join(sem_centro['regiao'])}. Verifique data/processed/regioes_saude_pb.csv."
        )
        st.stop()

    maior_volume = dados["volume_evadido_total"].max()
    for tipo in TIPOS_EVASAO_ORDEM:
        sub = dados[dados["tipo_evasao_dominante"] == tipo]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scattergeo(
                lon=sub["lon"],
                lat=sub["lat"],
                mode="markers+text",
                marker=dict(
                    size=14 + 26 * sub["volume_evadido_total"] / maior_volume,
                    color=CORES_TIPO_EVASAO[tipo],
                    line=dict(width=1.5, color="white"),
                ),
                text=sub["regiao"].str.replace(" - PB", "", regex=False),
                textposition="top center",
                textfont=dict(size=10, color="#222"),
                name=tipo,
                hoverinfo="text",
                hovertext=[
                    f"<b>{r}</b><br>Tipo dominante: {tipo} ({p:.0f}% do volume evadido)<br>"
                    f"Volume evadido: {mil(v)} internações<br>Ação recomendada: {acao}"
                    for r, p, v, acao in zip(
                        sub["regiao"],
                        sub["pct_tipo_dominante_do_evadido_regiao"],
                        sub["volume_evadido_total"],
                        sub["acao_recomendada"],
                    )
                ],
            )
        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=620,
        legend=dict(
            title="Tipo de evasão dominante", yanchor="top", y=0.98, xanchor="left", x=0.01
        ),
        dragmode="pan",
    )
    return fig


def aba_mapa() -> None:
    st.subheader("Para onde os paraibanos se deslocam para internar")

    camada = st.radio(
        "Camada do mapa",
        [CAMADA_CAPTACAO, CAMADA_TIPO_EVASAO],
        horizontal=True,
        help="A área de captação mostra PARA ONDE o paciente vai; o tipo de evasão mostra "
        "POR QUE ele foi — se é falta de estrutura local, fila de cirurgia ou encaminhamento correto.",
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
        quantos = st.slider(
            "Quantos fluxos mostrar",
            5,
            60,
            25,
            step=5,
            disabled=camada != CAMADA_CAPTACAO,
            help="Só se aplica à camada de área de captação.",
        )

    if camada == CAMADA_CAPTACAO:
        st.caption(
            "Cada município está pintado com a **cor da cidade onde a maioria dos seus moradores "
            "acaba internada** — municípios da mesma cor formam a área de captação de um mesmo polo. "
            "As **linhas** são os maiores fluxos, com espessura proporcional ao volume, e os "
            "**pontos escuros** marcam os municípios que mais recebem gente de fora."
        )

        st.plotly_chart(montar_mapa(str(mes), quantos), width="stretch")

        polos = polos_receptores(str(mes), quantos=2)
        total_polos = int(polos["internacoes"].sum())
        st.caption(
            f"Só {polos.iloc[0]['nome_mun_int']} e {polos.iloc[1]['nome_mun_int']} receberam "
            f"{total_polos:,}".replace(",", ".")
            + " internações de moradores de outros municípios no recorte selecionado."
        )
    else:
        st.caption(
            "Cada **marcador** é uma das 16 regiões de saúde, colorida pelo tipo de evasão que "
            "domina o volume que saiu dela em 2025 (a régua de classificação da PA6) — e o "
            "tamanho do marcador acompanha o volume evadido da região. Passe o mouse para ver "
            "a ação recomendada. Esta camada é anual: não tem filtro por mês."
        )
        st.plotly_chart(montar_mapa_tipo_evasao(), width="stretch")


# --------------------------------------------------------------------------- #
# Aba: índice de dependência por região de saúde
# --------------------------------------------------------------------------- #
def media_estadual(df: pd.DataFrame) -> float:
    """Média da Paraíba: % das internações de moradores do estado que saiu da sua região.

    É o corte da faixa "baixa" na definição (seção 5) — e sai da soma das colunas, não
    de um número digitado, para nunca descolar da tabela exibida ao lado.
    """
    return 100 * df["internacoes_realizadas_fora"].sum() / df["internacoes_residentes"].sum()


@st.cache_data
def destino_principal_regiao(regiao: str) -> tuple[str, int] | None:
    """Para onde vai a maior parte de quem sai da região: (região de destino, internações).

    Derivado da matriz regional no mesmo instante da consulta — nenhum destino está
    escrito à mão no painel. Devolve None quando a região não exporta ninguém.
    """
    df = carregar_matriz_regional()
    fora = df[(df["regiao_res"] == regiao) & df["evasao_regional"]]
    if fora.empty:
        return None
    por_destino = fora.groupby("regiao_int")["internacoes"].sum()
    return por_destino.idxmax(), int(por_destino.max())


def grafico_ranking(df: pd.DataFrame) -> go.Figure:
    """Barras horizontais do índice, com as duas réguas da definição desenhadas por cima."""
    # ascendente: o Plotly empilha a primeira categoria embaixo, então quem depende mais
    # termina no topo — que é onde o olho do gestor cai primeiro.
    ordenado = df.sort_values("indice_dependencia_pct")

    fig = px.bar(
        ordenado,
        x="indice_dependencia_pct",
        y="regiao",
        orientation="h",
        color="faixa_dependencia",
        color_discrete_map=CORES_FAIXA,
        text=ordenado["indice_dependencia_pct"].map(pct),
        custom_data=["posicao", "internacoes_residentes", "internacoes_realizadas_fora"],
        labels={
            "indice_dependencia_pct": "% das internações que aconteceu fora da região",
            "regiao": "",
            "faixa_dependencia": "Dependência",
        },
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Índice: %{x:.1f}%<br>"
        "Posição no ranking: %{customdata[0]}ª de 16<br>"
        "Internações de moradores: %{customdata[1]:,}<br>"
        "Dessas, fora da região: %{customdata[2]:,}<extra></extra>",
    )

    media = media_estadual(df)
    for valor, texto in [
        (media, f"média da PB: {pct(media)}"),
        (50, "metade das internações"),
    ]:
        fig.add_vline(
            x=valor,
            line=dict(color="#888", width=1.5, dash="dot"),
            annotation_text=texto,
            annotation_position="top",
        )

    fig.update_layout(
        height=560,
        margin=dict(l=0, r=40, t=40, b=0),
        xaxis_range=[0, 100],
        legend=dict(title="Dependência", orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return fig


def cartao_regiao(df: pd.DataFrame) -> None:
    """Ficha de uma região: o índice com a posição, o volume e para onde a gente vai."""
    regiao = st.selectbox("Ver uma região em detalhe", df["regiao"].tolist())
    linha = df[df["regiao"] == regiao].iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Índice de dependência",
        pct(linha["indice_dependencia_pct"]),
        help="% das internações de moradores desta região que aconteceu em hospital de outra região.",
    )
    m2.metric("Posição no ranking", f"{int(linha['posicao'])}ª de {len(df)}")
    m3.metric("Internações de moradores (2025)", mil(linha["internacoes_residentes"]))

    dentro = int(linha["internacoes_realizadas_dentro"])
    fora = int(linha["internacoes_realizadas_fora"])
    frase = (
        f"Dependência **{linha['faixa_dependencia']}**: das "
        f"{mil(linha['internacoes_residentes'])} internações de moradores da região em 2025, "
        f"{mil(dentro)} aconteceram dentro da própria região e {mil(fora)} fora dela."
    )

    destino = destino_principal_regiao(regiao)
    if destino:
        nome_destino, volume = destino
        share = 100 * volume / fora if fora else 0
        frase += (
            f" O destino mais procurado por quem sai é a **{nome_destino}**, "
            f"com {mil(volume)} internações — {share:.0f}% de tudo o que saiu da região."
        )
    st.markdown(frase)


def aba_indice() -> None:
    st.subheader("Índice de dependência por região de saúde")

    df = carregar_indice()
    media = media_estadual(df)
    # lê a faixa já classificada no notebook em vez de reaplicar o corte de 50% aqui:
    # a regra vive num só lugar (a tabela) e painel e tabela não podem divergir.
    n_alta = int((df["faixa_dependencia"] == "alta").sum())

    st.markdown(
        f"### {n_alta} das {len(df)} regiões de saúde da Paraíba internam a **maioria** "
        "dos seus moradores fora da própria região"
    )
    media_txt = pct(media)
    st.caption(
        "O índice de uma região é a porcentagem das internações dos seus moradores que "
        f"aconteceu em hospital de outra região. A média do estado é {media_txt} — quem está "
        "acima da linha pontilhada perde mais gente do que o estado perde na média. "
        "A definição completa, com fórmula, exemplo e limitações, está no fim desta aba."
    )

    st.plotly_chart(grafico_ranking(df), width="stretch")

    cartao_regiao(df)

    st.markdown("#### A tabela completa")
    st.caption(
        "O índice aparece sempre ao lado do volume: região pequena tem número mais instável, "
        "então comparar índices sem olhar o tamanho da região leva a conclusão injusta."
    )
    st.dataframe(
        df.rename(
            columns={
                "posicao": "#",
                "regiao": "Região de saúde",
                "internacoes_residentes": "Internações de moradores",
                "internacoes_realizadas_dentro": "Internadas dentro da região",
                "internacoes_realizadas_fora": "Internadas fora da região",
                "indice_dependencia_pct": "Índice (%)",
                "faixa_dependencia": "Dependência",
            }
        ),
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Como este número é calculado")
    st.caption(
        "Texto integral da definição aprovada do projeto — o mesmo documento que está no "
        "repositório, exibido aqui para que o índice possa ser entendido sem sair do painel."
    )
    for titulo, corpo in carregar_definicao():
        with st.expander(titulo):
            st.markdown(corpo)


# --------------------------------------------------------------------------- #
# Aba: achados & recomendações
# --------------------------------------------------------------------------- #
def numeros_de_capa() -> dict[str, float | int]:
    """Os quatro números do topo da aba, calculados das pré-agregações.

    Poderiam ser digitados — estão todos escritos na narrativa. Não são, de propósito:
    a regra RNF-05 vale também dentro do painel, e um número calculado nunca fica para
    trás quando a base é atualizada.
    """
    matriz = carregar_matriz_municipal()
    total = int(matriz["internacoes"].sum())
    fora = int(matriz.loc[matriz["evasao_municipal"], "internacoes"].sum())

    # Fatia dos dois maiores destinos sobre tudo que se deslocou.
    por_destino = (
        matriz[matriz["evasao_municipal"]]
        .groupby("nome_mun_int")["internacoes"]
        .sum()
        .sort_values(ascending=False)
    )
    polos = por_destino.head(2)

    indice = carregar_indice()

    return {
        "internacoes": total,
        "fora_pct": fora / total * 100,
        "polos_nomes": " e ".join(polos.index),
        "polos_pct": polos.sum() / fora * 100,
        "regioes_alta": int((indice["faixa_dependencia"] == "alta").sum()),
        "regioes_total": len(indice),
    }


def grafico_assinatura_regiao(sub: pd.DataFrame) -> go.Figure:
    """Barras horizontais do excesso de evasão por especialidade, para UMA região.

    `excesso_pp` já vem calculado no notebook: taxa de evasão da especialidade menos a
    taxa de evasão geral da PRÓPRIA região — zero é a média dela mesma, não a do estado.
    """
    ordenado = sub.sort_values("excesso_pp")
    sinal = ordenado["excesso_pp"].map(
        lambda v: "Acima da média da própria região" if v >= 0 else "Abaixo da média da própria região"
    )
    fig = px.bar(
        ordenado,
        x="excesso_pp",
        y="especialidade",
        orientation="h",
        color=sinal,
        color_discrete_map={
            "Acima da média da própria região": CORES_FAIXA["alta"],
            "Abaixo da média da própria região": CORES_FAIXA["baixa"],
        },
        text=ordenado["excesso_pp"].map(lambda v: f"{v:+.1f} p.p.".replace(".", ",")),
        custom_data=["n", "taxa_evasao_pct"],
        labels={"excesso_pp": "Excesso de evasão (pontos percentuais)", "especialidade": "", "color": ""},
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Excesso: %{x:+.1f} p.p.<br>"
        "Taxa de evasão da especialidade: %{customdata[1]:.1f}%<br>"
        "Internações de moradores nesta especialidade: %{customdata[0]:,}<extra></extra>",
    )
    fig.add_vline(x=0, line=dict(color="#888", width=1.5, dash="dot"))
    fig.update_layout(
        height=max(220, 70 + 55 * len(ordenado)),
        margin=dict(l=0, r=40, t=10, b=0),
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return fig


def bloco_o_que_falta_por_regiao(df_reco: pd.DataFrame, df_assinatura: pd.DataFrame) -> None:
    """US do notebook PA6 plugada no painel: destino, especialidade que mais falta e
    composição das seis caixas da régua de classificação, região por região."""
    st.markdown("### O que falta em cada região")
    st.caption(
        "Índice de dependência conta **quanto** cada região evade; aqui está **de quê** — "
        "que tipo de internação está saindo e o que isso implica para a Secretaria."
    )

    regiao = st.selectbox("Ver uma região em detalhe", df_reco["regiao"].tolist(), key="achados_regiao")
    linha = df_reco[df_reco["regiao"] == regiao].iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Índice de dependência",
        pct(linha["indice_dependencia_pct"]),
        help="% das internações de moradores desta região que aconteceu em hospital de outra região.",
    )
    m2.metric(
        f"Destino principal: {linha['destino_principal']}",
        pct(linha["pct_para_destino_principal"]),
        help="% de tudo que evadiu da região que foi parar nesse destino.",
    )
    m3.metric("Volume evadido no ano", mil(linha["volume_evadido_total"]))

    sub = df_assinatura[
        (df_assinatura["regiao"] == regiao)
        & (df_assinatura["eixo"] == "ESPEC")
        & (df_assinatura["n_min_ok"])
    ].copy()
    sub["categoria"] = sub["categoria"].astype(str).str.zfill(2)
    sub["especialidade"] = sub["categoria"].map(ESPEC_NOMES)

    if sub.empty:
        st.info("Nenhuma especialidade desta região passou do piso mínimo de casos para comparação.")
    else:
        st.plotly_chart(grafico_assinatura_regiao(sub), width="stretch")
        st.caption(
            "Zero é a **média de evasão da própria região**, não a do estado — uma barra acima "
            "de zero é uma especialidade que essa região evade mais do que evade em geral."
        )

        frase = (
            f"O maior gargalo da região é **{linha['especialidade_maior_excesso_nome']}**: "
            f"{pct(linha['especialidade_maior_excesso_taxa_evasao_pct'])} dos casos dessa "
            f"especialidade ({mil(linha['especialidade_maior_excesso_n'])} internações) foram "
            f"resolvidos em outra região, {linha['especialidade_maior_excesso_pp']:+.1f} pontos "
            "percentuais acima da evasão geral da região. Ou seja: a região resolve a maior parte "
            f"dos seus casos em casa, mas manda {pct(linha['especialidade_maior_excesso_taxa_evasao_pct'])} "
            f"dos casos de {linha['especialidade_maior_excesso_nome'].lower()} para fora."
        )
        st.markdown(frase)

    st.markdown("##### Composição do que evadiu, por tipo")
    st.caption(
        "As seis caixas somam 100% do volume evadido da região — nenhuma internação evadida fica "
        "de fora da classificação."
    )
    composicao = pd.DataFrame(
        {
            "regiao": [regiao] * len(TIPOS_EVASAO_ORDEM),
            "tipo": TIPOS_EVASAO_ORDEM,
            "pct": [linha[f"pct_{tipo}"] for tipo in TIPOS_EVASAO_ORDEM],
        }
    )
    fig_comp = px.bar(
        composicao,
        x="pct",
        y="regiao",
        color="tipo",
        orientation="h",
        category_orders={"tipo": TIPOS_EVASAO_ORDEM},
        color_discrete_map=CORES_TIPO_EVASAO,
        text=composicao["pct"].map(pct),
        labels={"pct": "% do volume evadido", "regiao": "", "tipo": ""},
    )
    fig_comp.update_traces(textposition="inside", hovertemplate="%{fullData.name}: %{x:.1f}%<extra></extra>")
    fig_comp.update_layout(
        height=140,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        yaxis=dict(showticklabels=False),
        xaxis_range=[0, 100],
    )
    st.plotly_chart(fig_comp, width="stretch")

    cols = st.columns(3)
    for i, tipo in enumerate(TIPOS_EVASAO_ORDEM):
        significado, acao = CATEGORIA_EVASAO_INFO[tipo]
        cols[i % 3].metric(
            tipo,
            pct(linha[f"pct_{tipo}"]),
            help=f"{significado} Ação recomendada: {acao}",
        )


def aba_achados() -> None:
    st.subheader("Achados & recomendações")

    capa = numeros_de_capa()
    a, b, c, d = st.columns(4)
    a.metric("Internações em 2025", mil(capa["internacoes"]))
    b.metric("Fora da cidade onde mora", pct(capa["fora_pct"]))
    c.metric(f"Concentrado em {capa['polos_nomes']}", pct(capa["polos_pct"]))
    d.metric(
        "Regiões de dependência alta",
        f"{capa['regioes_alta']} de {capa['regioes_total']}",
    )

    secoes = carregar_narrativa()
    achados = [s for s in secoes if s[0].startswith("Achado")]
    recomendacoes = [s for s in secoes if s[0].startswith("Recomendação")]
    # O que não é achado nem recomendação: o achado central (primeira seção), o
    # enquadramento e as limitações. Renderizados na ordem do documento.
    restantes = [s for s in secoes if s not in achados and s not in recomendacoes]
    central, fechamento = restantes[0], restantes[1:]

    st.markdown("---")
    st.markdown(f"### {central[0]}")
    st.markdown(central[1])

    st.markdown("---")
    st.markdown("### Os cinco achados")
    st.caption(
        "Cada um traz o número que o sustenta e o que ele implica para a gestão. "
        "Clique para abrir."
    )
    for titulo, corpo in achados:
        with st.expander(titulo):
            st.markdown(corpo)

    st.markdown("---")
    st.markdown("### O que fazer a respeito")
    st.caption(
        "Nenhuma recomendação aparece sem a evidência que a sustenta: cada uma termina "
        "com os códigos dos números que a ancoram, rastreáveis em "
        "`reports/sumario-evidencias.md`."
    )
    for titulo, corpo in recomendacoes:
        with st.expander(titulo):
            st.markdown(corpo)

    st.markdown("---")
    bloco_o_que_falta_por_regiao(carregar_recomendacao_regiao(), carregar_assinatura_regiao())

    st.markdown("---")
    for titulo, corpo in fechamento:
        with st.expander(titulo):
            st.markdown(corpo)

    st.caption(
        "Texto integral de `reports/narrativa-executiva.md` — o painel lê o documento do "
        "repositório em vez de guardar uma cópia, para que nunca existam duas versões."
    )


# --------------------------------------------------------------------------- #
# Aba: sobre os dados
# --------------------------------------------------------------------------- #
# O comando que congela um mês novo. Constante para aparecer uma vez só na tela e
# não ser reescrito no meio de um parágrafo — o passo a passo completo (incluindo
# a ordem de reprocessamento) vive em docs/dados/atualizacao-mensal.md, não aqui.
COMANDO_CONGELAR = "python src/congelar_sih.py"


def cobertura_da_base() -> dict[str, int | str]:
    """Quantos meses e quantas internações o painel está mostrando, contados da própria
    base — pelo mesmo motivo de `numeros_de_capa`: um número digitado à mão envelhece
    no dia em que um mês novo entrar, e este é justamente o texto que fala disso."""
    matriz = carregar_matriz_municipal()
    meses = sorted(int(m) for m in matriz["mes"].unique())
    return {
        "n_meses": len(meses),
        "primeiro": MESES[meses[0]],
        "ultimo": MESES[meses[-1]],
        "internacoes": int(matriz["internacoes"].sum()),
    }


def aba_sobre() -> None:
    st.subheader("Sobre os dados")

    cob = cobertura_da_base()
    a, b, c = st.columns(3)
    a.metric("Fonte", "SIH/SUS — DATASUS")
    b.metric("Período", f"{cob['primeiro']} a {cob['ultimo']} de 2025")
    c.metric("Internações na base", mil(cob["internacoes"]))

    st.markdown(
        f"""
Tudo o que aparece neste painel vem de **uma única fonte pública**: o SIH/SUS, o sistema
em que o Ministério da Saúde registra toda internação paga pelo SUS no país. O arquivo que
usamos se chama **RD** ("AIH reduzida") e traz uma linha por internação, com duas
informações que são o coração do projeto: **em que município o paciente mora** e **em que
município ele foi internado**. É a diferença entre esses dois campos que chamamos de
*evasão*.

Baixamos os arquivos da Paraíba de **{cob["primeiro"].lower()} a {cob["ultimo"].lower()} de
2025** — {cob["n_meses"]} meses, {mil(cob["internacoes"])} internações — direto do
servidor do DATASUS.
"""
    )

    with st.expander("Por que o painel funciona sem internet", expanded=True):
        st.markdown(
            """
Os dados foram **congelados**: baixados uma vez e guardados como arquivos dentro do
próprio repositório do projeto. O painel lê esses arquivos do disco e nunca consulta o
DATASUS enquanto está rodando.

Isso é uma decisão, não uma limitação. Um painel que consulta um servidor ao vivo depende
de o servidor estar no ar e de a rede da sala funcionar — e depende também de o número não
ter mudado desde a última vez que alguém olhou. Congelado, o painel mostra **exatamente**
os mesmos números hoje, na apresentação e daqui a um ano, e qualquer pessoa que baixe o
repositório reproduz a mesma tela.

Como efeito colateral bem-vindo: dá para apresentar com a internet desligada.
"""
        )

    with st.expander("O número pode mudar depois — e por quê"):
        st.markdown(
            """
O DATASUS **corrige o passado**. Quando um hospital envia uma internação com atraso, ou
corrige um registro errado, essa internação entra no sistema *depois* que o mês dela já
tinha sido publicado. Na prática, um mês recém-publicado chega **incompleto e vai subindo**
ao longo dos meses seguintes, até parar de mudar.

Consequência: baixar o mesmo mês em duas datas diferentes pode devolver dois números
diferentes. Não é erro de cálculo — é assim que o dado funciona.

**Dezembro é o caso mais sensível**, porque foi o último mês a ser congelado: teve menos
tempo para receber essas correções. Aqui dezembro aparece como o mês de menor volume do
ano — e, com esta base, **não dá para saber** quanto disso é "houve mesmo menos
internação" e quanto é "o registro ainda não chegou".

**A política do projeto é declarar, não maquiar.** Nenhum mês foi excluído (um ano de onze
meses seria uma invenção), nenhuma correção futura foi estimada (seria inventar dado que
não existe), e a ressalva está escrita em todo lugar em que dezembro é citado. É a leitura
honesta do que a base sustenta.
"""
        )

    with st.expander("Como este painel ganharia um mês novo"):
        st.markdown(
            """
O DATASUS publica cada mês com **cerca de dois meses de atraso**. Para trazer um mês novo,
roda-se um comando na pasta do projeto:
"""
        )
        st.code(COMANDO_CONGELAR, language="powershell")
        st.markdown(
            """
Esse programa se conecta ao servidor do DATASUS, baixa o arquivo do mês, confere se os
campos de origem e destino vieram completos e guarda o resultado no projeto. Ele é
**seguro de repetir**: mês que já foi baixado é pulado, sem baixar de novo e sem sobrescrever
nada — se a conexão cair no meio, é só rodar outra vez.

Baixar, porém, não é o suficiente: os quadros deste painel são **contas prontas**, feitas
antes, para que a tela abra rápido e sem recalcular nada a cada clique. Então é preciso
refazer essas contas, na ordem certa — primeiro a base unificada, depois as regiões de
saúde, depois a matriz de origem e destino, e só então as análises e o índice de
dependência.

O passo a passo completo — a ordem exata, o que cada etapa refaz e o que conferir nos
números — está em **`docs/dados/atualizacao-mensal.md`**, no repositório. Nada aqui no código do
painel precisa mudar: ele passa a exibir o mês novo sozinho.
"""
        )

    st.caption(
        "Unidade de contagem: a AIH (Autorização de Internação Hospitalar). É uma internação "
        "paga pelo SUS, não uma pessoa — quem internou três vezes no ano conta três. "
        "Os arquivos originais e os documentos citados estão no repositório do projeto."
    )


# --------------------------------------------------------------------------- #
def main() -> None:
    st.set_page_config(page_title="Evasão Assistencial — PB", layout="wide")
    st.title("Mapa de Evasão Assistencial da Paraíba")
    st.caption(
        "Para onde os paraibanos vão se internar — matriz origem→destino do SIH/DATASUS, "
        "ano de 2025, dados congelados localmente (o painel funciona sem internet)."
    )

    matriz, mapa, indice, achados, sobre = st.tabs(
        ["Matriz O-D", "Mapa", "Índice de dependência", "Achados & recomendações", "Sobre os dados"]
    )
    with matriz:
        aba_matriz()
    with mapa:
        aba_mapa()
    with indice:
        aba_indice()
    with achados:
        aba_achados()
    with sobre:
        aba_sobre()


if __name__ == "__main__":
    main()
