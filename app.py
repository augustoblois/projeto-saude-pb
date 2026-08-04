"""Painel — Mapa de Evasão Assistencial da Paraíba.

Consome APENAS as pré-agregações congeladas em `data/processed/` (produzidas pelos
notebooks `01-*`). Nenhuma interação do usuário recalcula nada a partir da base bruta,
e nada aqui depende de rede: o painel roda com a internet desligada.

Execução:  streamlit run app.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import ui

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

# Rótulo com que o notebook marca, na matriz regional, quem mora fora do estado.
FORA_DA_PB = "Fora da PB"

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
def carregar_matriz_bruta() -> pd.DataFrame:
    """A matriz como saiu do notebook: TODA internação ocorrida em hospital da Paraíba.

    Inclui quem mora em outro estado e veio internar aqui. O painel não analisa essas
    linhas (ver `carregar_matriz_municipal`) — esta função existe só para a aba "De onde
    vêm os dados" poder declarar, com o número na mão, o que ficou de fora e por quê.
    """
    return pd.read_parquet(DIR_PROCESSED / "matriz_od_municipal_mensal.parquet")


@st.cache_data
def carregar_matriz_municipal() -> pd.DataFrame:
    """A matriz do painel: só internações de quem MORA na Paraíba.

    O filtro fica aqui, na carga, e não em cada função que consome a matriz. É uma
    decisão de robustez: o painel inteiro pergunta "para onde vai o morador da Paraíba",
    e a base traz junto 0,6% de internações de gente que mora em outro estado e veio
    internar aqui. Quando o filtro vive espalhado, basta uma função esquecer dele para
    a capa passar a falar de uma população e o mapa logo abaixo de outra — que foi
    exatamente o que aconteceu antes desta mudança. Filtrando na porta de entrada, não
    existe caminho no código que alcance a base completa por engano.

    Quem precisa do universo completo chama `carregar_matriz_bruta` de propósito.
    """
    df = carregar_matriz_bruta()
    return df[df["uf_res"] == "PB"].reset_index(drop=True)


@st.cache_data
def carregar_matriz_regional() -> pd.DataFrame:
    """Mesma regra da matriz municipal, no nível das 16 regiões de saúde.

    Aqui os residentes de fora aparecem agrupados sob a região de origem "Fora da PB" —
    um rótulo que não é uma região de saúde e não tem índice de dependência, porque
    ninguém mede a autossuficiência de um lugar que não faz parte do estado.
    """
    df = pd.read_csv(DIR_PROCESSED / "matriz_od_regional_mensal.csv")
    return df[df["regiao_res"] != FORA_DA_PB].reset_index(drop=True)


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
def municipios_por_regiao() -> dict[str, list[str]]:
    """Quais municípios formam cada região de saúde, com o nome acentuado.

    O `regioes_saude_pb.csv` guarda os nomes sem acento ("Esperanca", "Sao Sebastiao de
    Lagoa de Roca"), do jeito que saem da tabela de origem. Exibir assim ficaria errado
    na tela, então o nome vem do arquivo de centróides — mesma base do IBGE, com a grafia
    correta — cruzado pelo código do município, que é o campo estável entre os dois.
    """
    mapa = pd.read_csv(DIR_PROCESSED / "regioes_saude_pb.csv", dtype={"codigo_municipio": str})
    nomes = carregar_centroides().set_index("cod_mun")["nome_mun"]
    # `fillna` guarda o caso de um município novo entrar no CSV de regiões antes de
    # entrar na malha: aparece com a grafia sem acento em vez de sumir da lista.
    mapa["exibicao"] = mapa["codigo_municipio"].map(nomes).fillna(mapa["nome_municipio"])
    return {
        regiao: sorted(grupo["exibicao"])
        for regiao, grupo in mapa.groupby("nome_regiao_saude")
    }


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


# --------------------------------------------------------------------------- #
# Aba: matriz origem → destino
# --------------------------------------------------------------------------- #
def aba_matriz() -> None:
    ui.cabecalho_secao(
        "route",
        "Quem sai de onde, e vai para onde",
        "Cada linha da tabela é um caminho percorrido por pacientes: a cidade onde eles moram "
        "e a cidade onde acabaram internados. Quando as duas são diferentes, alguém precisou "
        "viajar para conseguir um leito.",
    )

    ui.dica(
        "Escolha uma cidade abaixo para ver <strong>para onde os moradores dela vão</strong>, ou "
        "deixe em “Todas” para ver o estado inteiro. Cada internação aqui é uma "
        "<strong>AIH</strong> — o nome da autorização que o SUS emite a cada internação. "
        "Conta internações, não pessoas: quem internou três vezes no ano aparece três vezes.",
        titulo="Como usar esta tela",
    )

    nivel = st.radio(
        "Ver o caminho entre",
        ["Cidades", "Regiões de saúde"],
        horizontal=True,
        help="Cidades mostra o caminho município a município. Regiões agrupa os 223 municípios "
        "nas 16 regiões de saúde oficiais da Paraíba.",
    )

    if nivel == "Cidades":
        df = carregar_matriz_municipal()
        col_origem, col_destino, col_evasao = "nome_mun_res", "nome_mun_int", "evasao_municipal"
        rotulo_origem = "Cidade onde a pessoa mora"
        rot_de, rot_para = "De (cidade onde mora)", "Para (cidade onde internou)"
    else:
        df = carregar_matriz_regional()
        col_origem, col_destino, col_evasao = "regiao_res", "regiao_int", "evasao_regional"
        rotulo_origem = "Região onde a pessoa mora"
        rot_de, rot_para = "De (região onde mora)", "Para (região onde internou)"

    col_a, col_b = st.columns(2)
    with col_a:
        origem = st.selectbox(
            rotulo_origem,
            [TODOS] + sorted(df[col_origem].unique()),
            format_func=lambda v: "Todas" if v == TODOS else v,
        )
    with col_b:
        mes = st.selectbox(
            "Período",
            [TODOS] + sorted(df["mes"].unique()),
            format_func=lambda v: "Ano de 2025 inteiro" if v == TODOS else MESES[int(v)],
        )

    filtrado = filtrar(df, col_origem, origem, mes)

    total = int(filtrado["internacoes"].sum())
    fora = int(filtrado.loc[filtrado[col_evasao], "internacoes"].sum())
    pct_fora = 100 * fora / total if total else 0.0

    onde = "da própria cidade" if nivel == "Cidades" else "da própria região"
    ui.cartoes_numero(
        [
            {
                "rotulo": "Internações no recorte",
                "valor": mil(total),
                "icone": "cross",
                "nota": "Total de internações que este filtro seleciona.",
            },
            {
                "rotulo": f"Tiveram de sair {onde}",
                "valor": mil(fora),
                "icone": "route",
                "cor": ui.ALERTA,
                "nota": f"Foram internadas fora {onde} onde moram.",
            },
            {
                "rotulo": "Proporção que se deslocou",
                "valor": pct(pct_fora),
                "icone": "trending-up",
                "cor": ui.ALERTA if pct_fora >= 50 else ui.TEXTO,
                "nota": "Quanto do total acima precisou viajar.",
            },
        ]
    )

    if total == 0:
        st.info("Nenhuma internação neste recorte.")
        return

    tabela = (
        filtrado.groupby([col_origem, col_destino], as_index=False)["internacoes"]
        .sum()
        .sort_values("internacoes", ascending=False)
        .rename(columns={col_origem: rot_de, col_destino: rot_para, "internacoes": "Internações"})
    )
    tabela["Fatia do recorte"] = 100 * tabela["Internações"] / total

    st.dataframe(
        tabela,
        width="stretch",
        hide_index=True,
        # altura fixa maior: a tabela é o conteúdo principal desta aba, e a altura
        # automática do Streamlit mostrava só ~7 linhas antes de exigir rolagem
        height=520,
        column_config={
            rot_de: st.column_config.TextColumn(rot_de, width="medium"),
            rot_para: st.column_config.TextColumn(rot_para, width="medium"),
            # `localized` usa a formatação do idioma do navegador — é o que põe o ponto
            # de milhar sem precisar converter o número em texto (o que quebraria a
            # ordenação por clique no cabeçalho)
            "Internações": st.column_config.NumberColumn(
                "Internações", format="localized", width="small"
            ),
            # barra em vez de número solto: era exatamente o "percentual que não está
            # alinhado com nada" — agora o comprimento da barra é comparável de relance
            # entre as linhas, e o número fica ancorado nela
            "Fatia do recorte": st.column_config.ProgressColumn(
                "Fatia do recorte",
                format="%.1f%%",
                min_value=0,
                max_value=float(tabela["Fatia do recorte"].max()),
                width="medium",
            ),
        },
    )
    st.caption(
        f"{len(tabela)} caminhos diferentes neste recorte, do maior para o menor. "
        "Clique no cabeçalho para reordenar; o conteúdo pode ser copiado direto para citação."
    )


# --------------------------------------------------------------------------- #
# Aba: mapa dos fluxos
# --------------------------------------------------------------------------- #
@st.cache_data
def evasao_por_municipio(mes: str) -> pd.DataFrame:
    """Taxa de evasão de cada município da PB: % das internações dos seus moradores
    que aconteceu em hospital de outro município. Cacheada por mês."""
    df = filtrar(carregar_matriz_municipal(), "nome_mun_res", TODOS, mes)
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
    df = filtrar(carregar_matriz_municipal(), "nome_mun_res", TODOS, mes)

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
    df = filtrar(df[df["evasao_municipal"]], "nome_mun_res", TODOS, mes)
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


def arco(lon_a: float, lat_a: float, lon_b: float, lat_b: float, pontos: int = 36):
    """Curva suave ligando dois pontos, em vez do segmento de reta que os une.

    Por que curvar: com 25 fluxos saindo quase todos para os mesmos dois destinos, as
    retas se sobrepõem e o mapa vira uma teia opaca — não dá para seguir nenhum caminho
    com o olho. Arcos com curvaturas ligeiramente diferentes se separam visualmente, que
    é o mesmo truque usado em mapas de rota de voo.

    A curva é uma Bézier quadrática: dois extremos fixos e um ponto de controle no meio,
    empurrado perpendicularmente à reta. `t` percorre 0→1 e a fórmula devolve a posição
    ao longo da curva.
    """
    meio_lon, meio_lat = (lon_a + lon_b) / 2, (lat_a + lat_b) / 2
    d_lon, d_lat = lon_b - lon_a, lat_b - lat_a

    # A curvatura encolhe conforme o traço fica longo: sem isso, um fluxo que atravessa
    # o estado inteiro arqueia tanto que sai da moldura do mapa.
    comprimento = float(np.hypot(d_lon, d_lat))
    curvatura = 0.16 / (1 + comprimento)

    # Deslocar o ponto de controle por (-d_lat, +d_lon) é girar o vetor da reta em 90°,
    # ou seja: empurrar o meio da curva para o lado, não ao longo dela.
    ctrl_lon = meio_lon - d_lat * curvatura
    ctrl_lat = meio_lat + d_lon * curvatura

    t = np.linspace(0, 1, pontos)
    lon = (1 - t) ** 2 * lon_a + 2 * (1 - t) * t * ctrl_lon + t**2 * lon_b
    lat = (1 - t) ** 2 * lat_a + 2 * (1 - t) * t * ctrl_lat + t**2 * lat_b
    return lon, lat


def montar_mapa(mes: str, quantos_fluxos: int) -> go.Figure:
    """Três camadas: cores (área de captação), arcos (maiores fluxos) e pinos dos polos.

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
    # Contorno escuro entre municípios: sobre o fundo escuro do painel, o branco anterior
    # brilhava mais que o próprio dado e transformava a malha numa grade luminosa.
    fig.update_traces(marker_line_color="rgba(11,15,26,0.55)", marker_line_width=0.5)

    fluxos = maiores_fluxos(mes, quantos_fluxos)
    maior = fluxos["internacoes"].max() if len(fluxos) else 1
    for _, f in fluxos.iterrows():
        lon, lat = arco(f["lon_res"], f["lat_res"], f["lon_int"], f["lat_int"])
        peso = f["internacoes"] / maior
        espessura = 0.8 + 3.6 * peso
        rotulo = (
            f"{f['nome_mun_res']} → {f['nome_mun_int']}: "
            f"{f['internacoes']:,} internações".replace(",", ".")
        )

        # Duas passadas na MESMA curva formam o brilho: primeiro um traço largo e quase
        # transparente (o halo, que "vaza" luz para os lados), depois um traço fino e
        # opaco por cima (o núcleo). É como um letreiro de neon é desenhado — e é o que
        # faz a linha se destacar sobre qualquer cor de município por baixo.
        fig.add_trace(
            go.Scattergeo(
                lon=lon, lat=lat, mode="lines",
                line=dict(width=espessura * 3.2, color="rgba(56,189,248,0.13)"),
                hoverinfo="skip", showlegend=False,
            )
        )
        fig.add_trace(
            go.Scattergeo(
                lon=lon, lat=lat, mode="lines",
                # fluxo maior fica mais opaco: o volume é lido pela espessura E pelo
                # brilho, então os grandes saltam mesmo com muitas linhas na tela
                line=dict(width=espessura, color=f"rgba(125,211,252,{0.45 + 0.5 * peso:.2f})"),
                hoverinfo="text", text=rotulo, showlegend=False,
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

    # O pino é montado em três marcadores concêntricos no mesmo ponto, do maior para o
    # menor — halo, anel e núcleo. O Scattergeo não aceita um símbolo desenhado por nós
    # (isso exigiria mapbox e, portanto, rede), então o "alvo" das referências é obtido
    # empilhando círculos, que é o que dá a ele o aspecto de foco luminoso.
    base = 7 + 15 * polos["internacoes"] / polos["internacoes"].max()
    for escala, cor, borda in [
        (3.0, "rgba(56,189,248,0.10)", None),                  # halo externo
        (1.9, "rgba(56,189,248,0.22)", None),                  # anel médio
        (1.0, "#38BDF8", dict(width=2, color="#0B0F1A")),      # núcleo
    ]:
        fig.add_trace(
            go.Scattergeo(
                lon=polos["lon"], lat=polos["lat"], mode="markers",
                marker=dict(size=base * escala, color=cor, line=borda or dict(width=0)),
                hoverinfo="skip", showlegend=False,
            )
        )

    fig.add_trace(
        go.Scattergeo(
            lon=polos["lon"],
            lat=polos["lat"],
            mode="text",
            text=rotulos,
            textposition=posicoes,
            # nome quase branco sobre fundo escuro; o peso vem do tamanho, não mais de
            # uma família "Black", que engrossava demais em tela de projetor
            textfont=dict(size=13, color="#E8EDF7", family="Arial"),
            hoverinfo="text",
            hovertext=[
                f"{n}: recebeu {v:,} internações de fora".replace(",", ".")
                for n, v in zip(polos["nome_mun_int"], polos["internacoes"])
            ],
            showlegend=False,
        )
    )

    aplicar_tema_mapa(fig, titulo_legenda="A maioria se interna em")
    return fig


def aplicar_tema_mapa(fig: go.Figure, titulo_legenda: str) -> None:
    """Aplica o fundo escuro e a moldura comuns aos dois mapas.

    Existe para os dois mapas não divergirem: antes, cada um repetia o próprio bloco de
    `update_layout` e bastava ajustar um para o outro ficar diferente.

    `fitbounds="locations"` enquadra a Paraíba pelos próprios polígonos e `visible=False`
    remove o cenário embutido do Plotly (costa, fronteiras de países) — nada é buscado na
    rede, então o mapa continua abrindo offline.
    """
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",   # transparente: quem pinta o fundo é o papel do gráfico
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=620,
        # o mapa vinha com fundo branco padrão do Plotly dentro de um painel escuro —
        # era o retângulo claro no meio da tela
        paper_bgcolor=ui.FUNDO,
        plot_bgcolor=ui.FUNDO,
        font=dict(color=ui.TEXTO_SUAVE, size=12),
        legend=dict(
            title=dict(text=titulo_legenda, font=dict(color=ui.TEXTO, size=12)),
            yanchor="top", y=0.98, xanchor="left", x=0.01,
            bgcolor="rgba(19,26,43,0.82)",   # a legenda flutua sobre o mapa: precisa de
            bordercolor=ui.BORDA,            # um fundo próprio para o texto não competir
            borderwidth=1,                   # com os municípios coloridos por baixo
            font=dict(color=ui.TEXTO_SUAVE, size=11),
        ),
        dragmode="pan",
        hoverlabel=dict(
            bgcolor=ui.SUPERFICIE_ALTA,
            bordercolor=ui.BORDA_FORTE,
            font=dict(color=ui.TEXTO, size=12),
        ),
    )


# Nomes das duas camadas em forma de pergunta: "área de captação" e "tipo de evasão
# dominante" são termos do projeto, e quem abre o painel pela primeira vez não tem como
# saber qual dos dois botões responde a dúvida dele.
CAMADA_CAPTACAO = "Para onde as pessoas vão"
CAMADA_TIPO_EVASAO = "Por que elas precisam sair"


def montar_mapa_tipo_evasao() -> go.Figure:
    """Camada opcional: um marcador por região de saúde, colorido pelo tipo de evasão que
    domina o volume evadido dela (PA6). A malha municipal continua de fundo, em cinza
    neutro, só para dar contexto geográfico — a informação nova está nos marcadores.

    Marcadores em vez de choropleth por região: a malha disponível é municipal, e o
    projeto não usa geopandas para dissolver polígonos por região (nenhuma dependência
    nova). Um marcador por região é estável e não arrisca um choropleth quebrado.
    """
    base = carregar_matriz_municipal()[["cod_mun_res"]].drop_duplicates()
    base["cor"] = "PB"
    fig = px.choropleth(
        base,
        geojson=carregar_malha(),
        locations="cod_mun_res",
        featureidkey="properties.cod_mun",
        color="cor",
        # cinza-azulado escuro, um degrau acima do fundo: a malha aqui é só contexto
        # geográfico, e não pode competir com os marcadores, que são a informação
        color_discrete_map={"PB": ui.SUPERFICIE_ALTA},
    )
    fig.update_traces(
        marker_line_color=ui.BORDA, marker_line_width=0.5, showlegend=False
    )

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
                    # contorno na cor do fundo: separa marcadores que se encostam sem
                    # acrescentar um anel branco brilhante a cada um deles
                    line=dict(width=2, color=ui.FUNDO),
                ),
                text=sub["regiao"].str.replace(" - PB", "", regex=False),
                textposition="top center",
                textfont=dict(size=10, color=ui.TEXTO_SUAVE),
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

    aplicar_tema_mapa(fig, titulo_legenda="O que mais faz a região perder paciente")
    return fig


def aba_mapa() -> None:
    ui.cabecalho_secao(
        "map",
        "O caminho desenhado no mapa",
        "A mesma informação da tabela anterior, agora sobre o desenho da Paraíba: dá para ver "
        "de relance que o estado inteiro converge para pouquíssimos endereços.",
    )

    camada = st.radio(
        "O que mostrar no mapa",
        [CAMADA_CAPTACAO, CAMADA_TIPO_EVASAO],
        horizontal=True,
        help="A primeira responde PARA ONDE o paciente vai. A segunda responde POR QUE ele foi — "
        "se faltou estrutura na cidade dele, se é fila de cirurgia ou se o encaminhamento está correto.",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        mes = st.selectbox(
            "Período",
            [TODOS] + list(range(1, 13)),
            format_func=lambda v: "Ano de 2025 inteiro" if v == TODOS else MESES[int(v)],
            key="mapa_mes",
        )
    with col_b:
        quantos = st.slider(
            "Quantos caminhos desenhar",
            5,
            60,
            25,
            step=5,
            disabled=camada != CAMADA_CAPTACAO,
            help="São centenas de caminhos no total — desenhar todos deixaria o mapa ilegível. "
            "Esta barra escolhe quantos dos MAIORES aparecem. Em 25, vê-se o esqueleto da rede; "
            "aumentando, aparecem os fluxos menores. Só vale para o mapa de áreas de captação.",
        )

    if camada == CAMADA_CAPTACAO:
        ui.dica(
            "Cada município está pintado com a <strong>cor da cidade que mais interna os moradores "
            "dele</strong> — quem tem a mesma cor manda gente para o mesmo hospital, e as manchas de "
            "cor são as áreas de influência de cada polo. As <strong>linhas luminosas</strong> são os "
            "maiores caminhos: quanto mais grossa e mais clara, mais gente passa por ali. Os "
            "<strong>círculos brilhantes</strong> marcam as cidades que mais recebem pacientes de fora. "
            "Passe o mouse sobre qualquer município ou linha para ver os números.",
            titulo="Como ler este mapa",
            icone_nome="map-pin",
        )

        st.plotly_chart(montar_mapa(str(mes), quantos), width="stretch")

        polos = polos_receptores(str(mes), quantos=2)
        total_polos = int(polos["internacoes"].sum())
        ui.cartoes_numero(
            [
                {
                    "rotulo": f"Recebido por {polos.iloc[0]['nome_mun_int']} e {polos.iloc[1]['nome_mun_int']}",
                    "valor": mil(total_polos),
                    "icone": "map-pin",
                    "cor": ui.ACENTO,
                    "nota": "Internações de gente que mora em outra cidade, no período selecionado.",
                },
                {
                    "rotulo": "Caminhos desenhados agora",
                    "valor": str(quantos),
                    "icone": "route",
                    "nota": "Dos maiores para os menores — ajuste na barra acima.",
                },
            ]
        )
    else:
        ui.dica(
            "Cada <strong>círculo colorido</strong> é uma das 16 regiões de saúde da Paraíba, e a cor "
            "diz qual é o <strong>motivo principal</strong> de os moradores dela se internarem fora. "
            "O tamanho do círculo acompanha quanta gente saiu. Passe o mouse sobre um deles para ler "
            "a região, o motivo e a providência que ele pede. "
            "Este mapa cobre o ano inteiro — o filtro de período acima não se aplica a ele.",
            titulo="Como ler este mapa",
            icone_nome="compass",
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
    return ui.tema_grafico(fig)


def cartao_regiao(df: pd.DataFrame) -> None:
    """Ficha de uma região: quais municípios são, o índice, o volume e para onde vai a gente."""
    regiao = st.selectbox("Escolha uma região para ver em detalhe", df["regiao"].tolist())
    linha = df[df["regiao"] == regiao].iloc[0]

    # Os municípios vêm ANTES dos números: o nome "3ª Região - PB" é um código
    # administrativo, e sem saber que cidades ele cobre, os números abaixo não têm
    # como ser interpretados por quem não trabalha na Secretaria.
    ui.lista_municipios(regiao, municipios_por_regiao().get(regiao, []))

    faixa = str(linha["faixa_dependencia"])
    ui.cartoes_numero(
        [
            {
                "rotulo": "Depende de fora",
                "valor": pct(linha["indice_dependencia_pct"]),
                "icone": "route",
                "cor": CORES_FAIXA.get(faixa, ui.TEXTO),
                "nota": f"Dependência {faixa}. É a fatia das internações dos moradores "
                "que aconteceu em hospital de outra região.",
            },
            {
                "rotulo": "Posição no estado",
                "valor": f"{int(linha['posicao'])}ª de {len(df)}",
                "icone": "trending-up",
                "nota": "1ª é a região que mais depende de fora.",
            },
            {
                "rotulo": "Internações de moradores",
                "valor": mil(linha["internacoes_residentes"]),
                "icone": "cross",
                "nota": "Total em 2025, dentro e fora da região somados.",
            },
        ]
    )

    dentro = int(linha["internacoes_realizadas_dentro"])
    fora = int(linha["internacoes_realizadas_fora"])
    frase = (
        f"Das {mil(linha['internacoes_residentes'])} internações de moradores desta região em "
        f"2025, <strong>{mil(dentro)} foram resolvidas dentro de casa</strong> e "
        f"<strong>{mil(fora)} exigiram sair da região</strong>."
    )

    destino = destino_principal_regiao(regiao)
    if destino:
        nome_destino, volume = destino
        share = 100 * volume / fora if fora else 0
        frase += (
            f" Quem sai vai principalmente para a <strong>{nome_destino}</strong>: "
            f"{mil(volume)} internações, {share:.0f}% de tudo o que saiu daqui."
        )
    ui.dica(frase, titulo="O que este quadro diz", icone_nome="info")


def aba_indice() -> None:
    df = carregar_indice()
    media = media_estadual(df)
    # lê a faixa já classificada no notebook em vez de reaplicar o corte de 50% aqui:
    # a regra vive num só lugar (a tabela) e painel e tabela não podem divergir.
    n_alta = int((df["faixa_dependencia"] == "alta").sum())

    ui.cabecalho_secao(
        "chart-bar",
        "Que regiões não conseguem se virar sozinhas",
        "A Paraíba é dividida oficialmente em 16 regiões de saúde — grupos de municípios que "
        "deveriam se sustentar entre si. Aqui está o quanto cada uma delas de fato consegue.",
    )

    ui.achado_central(
        etiqueta="O retrato do estado",
        frase=(
            f"{n_alta} das {len(df)} regiões de saúde da Paraíba internam a maioria dos seus "
            "moradores fora da própria região"
        ),
        numero=f"{n_alta}/{len(df)}",
        legenda="regiões que dependem mais de fora do que de si mesmas",
    )

    ui.dica(
        "Para cada região, medimos <strong>quanto da internação dos moradores dela acontece "
        "fora dela</strong>. Zero por cento seria uma região que resolve tudo em casa; cem por "
        "cento, uma que não resolve nada. A média da Paraíba é "
        f"<strong>{pct(media)}</strong> — no gráfico, quem está à direita da linha pontilhada "
        "perde mais gente do que o estado perde na média. "
        "As barras <strong>vermelhas</strong> passam de 50%: ali, a maioria dos moradores se "
        "interna fora. A conta completa, com fórmula e limitações, está no fim desta aba.",
        titulo="O que é este número",
        icone_nome="target",
    )

    st.plotly_chart(grafico_ranking(df), width="stretch")

    st.markdown("---")
    ui.cabecalho_secao(
        "search",
        "Uma região de cada vez",
        "Os nomes das regiões são códigos administrativos. Escolha uma abaixo para ver que "
        "cidades ela cobre e o que acontece com os moradores dela.",
    )
    cartao_regiao(df)

    st.markdown("---")
    ui.cabecalho_secao(
        "table",
        "As 16 regiões lado a lado",
        "O índice aparece sempre ao lado do volume: região pequena tem número mais instável, "
        "e comparar porcentagens sem olhar o tamanho leva a conclusão injusta.",
    )
    st.dataframe(
        df.rename(
            columns={
                "posicao": "#",
                "regiao": "Região de saúde",
                "internacoes_residentes": "Internações de moradores",
                "internacoes_realizadas_dentro": "Resolvidas em casa",
                "internacoes_realizadas_fora": "Precisaram sair",
                "indice_dependencia_pct": "Depende de fora",
                "faixa_dependencia": "Dependência",
            }
        ),
        width="stretch",
        hide_index=True,
        height=600,
        column_config={
            "#": st.column_config.NumberColumn("#", width="small"),
            "Internações de moradores": st.column_config.NumberColumn(format="localized"),
            "Resolvidas em casa": st.column_config.NumberColumn(format="localized"),
            "Precisaram sair": st.column_config.NumberColumn(format="localized"),
            # mesma barra da matriz: a comparação entre as 16 regiões passa a ser visual
            "Depende de fora": st.column_config.ProgressColumn(
                "Depende de fora", format="%.1f%%", min_value=0, max_value=100, width="medium"
            ),
        },
    )

    st.markdown("---")
    ui.cabecalho_secao(
        "file-text",
        "Como este número é calculado",
        "Texto integral da definição aprovada do projeto — o mesmo documento que está no "
        "repositório, exibido aqui para que o índice possa ser conferido sem sair do painel.",
    )
    st.write("")
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
    fig.add_vline(x=0, line=dict(color=ui.BORDA_FORTE, width=1.5, dash="dot"))
    fig.update_layout(
        height=max(220, 70 + 55 * len(ordenado)),
        margin=dict(l=0, r=40, t=10, b=0),
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return ui.tema_grafico(fig)


def bloco_o_que_falta_por_regiao(df_reco: pd.DataFrame, df_assinatura: pd.DataFrame) -> None:
    """US do notebook PA6 plugada no painel: destino, especialidade que mais falta e
    composição das seis caixas da régua de classificação, região por região."""
    ui.cabecalho_secao(
        "stethoscope",
        "O que falta em cada região",
        "A seção anterior conta QUANTA gente cada região perde. Esta conta DE QUÊ: que tipo de "
        "internação está saindo, e o que isso pede da Secretaria — porque falta de leito clínico "
        "e fila de cirurgia eletiva são problemas diferentes, com soluções diferentes.",
    )

    regiao = st.selectbox(
        "Escolha uma região", df_reco["regiao"].tolist(), key="achados_regiao"
    )
    linha = df_reco[df_reco["regiao"] == regiao].iloc[0]

    ui.lista_municipios(regiao, municipios_por_regiao().get(regiao, []))

    ui.cartoes_numero(
        [
            {
                "rotulo": "Depende de fora",
                "valor": pct(linha["indice_dependencia_pct"]),
                "icone": "route",
                "cor": ui.ALERTA,
                "nota": "Das internações dos moradores, esta fatia aconteceu em outra região.",
            },
            {
                "rotulo": f"Vai principalmente para {linha['destino_principal']}",
                "valor": pct(linha["pct_para_destino_principal"]),
                "icone": "map-pin",
                "cor": ui.ACENTO,
                "nota": "De tudo que saiu da região, esta fatia parou nesse destino.",
            },
            {
                "rotulo": "Pessoas que saíram no ano",
                "valor": mil(linha["volume_evadido_total"]),
                "icone": "users",
                "nota": "Internações de moradores realizadas fora da região em 2025.",
            },
        ]
    )

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
        ui.dica(
            "O zero deste gráfico é a <strong>média da própria região</strong>, não a do estado. "
            "Uma barra para a direita é um tipo de internação que esta região manda para fora "
            "<strong>mais do que ela costuma mandar</strong> — é ali que falta serviço. Uma barra "
            "para a esquerda é o que ela resolve melhor do que a média dela mesma.",
            titulo="Como ler este gráfico",
            icone_nome="chart-bar",
        )
        st.plotly_chart(grafico_assinatura_regiao(sub), width="stretch")

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

    st.markdown("##### Por que essas pessoas saíram")
    st.caption(
        "Toda internação que saiu da região foi classificada em uma destas seis caixas — as "
        "fatias somam 100%, nenhuma fica de fora. Nem toda saída é problema: as duas primeiras "
        "são o sistema funcionando como deveria."
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
    st.plotly_chart(ui.tema_grafico(fig_comp), width="stretch")

    # A ação recomendada sai do tooltip e vira texto visível no cartão: escondida atrás
    # do "?" ela só era lida por quem já sabia que havia algo ali — e ela é justamente
    # a parte que interessa a um gestor.
    ui.cartoes_categoria(
        [
            {
                "titulo": tipo,
                "valor": pct(linha[f"pct_{tipo}"]),
                "cor": CORES_TIPO_EVASAO[tipo],
                "significado": CATEGORIA_EVASAO_INFO[tipo][0],
                "acao": CATEGORIA_EVASAO_INFO[tipo][1],
            }
            for tipo in TIPOS_EVASAO_ORDEM
        ]
    )


def titulo_de_cartao(titulo: str) -> str:
    """"Achado 3 — o tamanho da cidade decide" → "O tamanho da cidade decide".

    O selo numerado do cartão já mostra o "3", então repetir "Achado 3" no título gasta
    a linha mais visível do bloco com informação que o olho já tem. No documento a frase
    começa em minúscula porque é continuação do travessão; como título isolado, precisa
    da maiúscula — e só a primeira letra sobe, para não estragar nomes próprios.
    """
    _, _, resto = titulo.partition("—")
    frase = (resto or titulo).strip()
    return frase[:1].upper() + frase[1:]


def aba_achados() -> None:
    capa = numeros_de_capa()

    secoes = carregar_narrativa()
    achados = [s for s in secoes if s[0].startswith("Achado")]
    recomendacoes = [s for s in secoes if s[0].startswith("Recomendação")]
    # O que não é achado nem recomendação: o achado central (primeira seção), o
    # enquadramento e as limitações. Renderizados na ordem do documento.
    restantes = [s for s in secoes if s not in achados and s not in recomendacoes]
    central, fechamento = restantes[0], restantes[1:]

    # O achado central abre com a frase em negrito da narrativa; o resto do texto vira
    # o parágrafo de apoio. Separar assim mantém a fonte única (o .md) e ainda deixa a
    # frase de impacto isolada, que é o que dá peso ao bloco.
    frase, _, apoio = central[1].strip().partition("\n\n")
    ui.achado_central(
        etiqueta=central[0],
        frase=frase.strip().strip("*"),
        numero=pct(capa["fora_pct"]),
        legenda="das internações acontecem fora da cidade onde a pessoa mora",
    )
    ui.escrever(f'<div class="ui-achado-corpo">{ui.markdown_para_html(apoio)}</div>')

    st.markdown("---")
    # A contagem sai do próprio documento: o título dizia "os cinco achados" enquanto a
    # narrativa já tinha sete, e um número escrito à mão volta a divergir na próxima vez.
    ui.cabecalho_secao(
        "search",
        f"Os {len(achados)} achados",
        "Cada um é uma conclusão fechada, com o número que a sustenta e o que ela implica "
        "para quem decide onde instalar serviço de saúde na Paraíba.",
    )
    st.write("")
    for i, (titulo, corpo) in enumerate(achados, start=1):
        ui.cartao_achado(i, titulo_de_cartao(titulo), corpo)

    st.markdown("---")
    ui.cabecalho_secao(
        "lightbulb",
        "O que fazer a respeito",
        "Nenhuma recomendação aparece sem a evidência que a sustenta: cada uma termina com "
        "os códigos dos números que a ancoram, rastreáveis em reports/sumario-evidencias.md.",
    )
    st.write("")
    for i, (titulo, corpo) in enumerate(recomendacoes, start=1):
        ui.cartao_acao(i, titulo_de_cartao(titulo), corpo)

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
    no dia em que um mês novo entrar, e este é justamente o texto que fala disso.

    Devolve os dois totais: o que o arquivo traz (`baixadas`) e o que o painel analisa
    (`internacoes`). A diferença entre eles é a parcela declarada logo abaixo na tela —
    e ela também sai da conta, nunca de um número escrito à mão.
    """
    matriz = carregar_matriz_municipal()
    meses = sorted(int(m) for m in matriz["mes"].unique())
    bruta = carregar_matriz_bruta()
    baixadas = int(bruta["internacoes"].sum())
    analisadas = int(matriz["internacoes"].sum())

    # De que estados vem quem mora fora da PB, do maior para o menor.
    de_fora = (
        bruta[bruta["uf_res"] != "PB"]
        .groupby("uf_res")["internacoes"]
        .sum()
        .sort_values(ascending=False)
    )
    return {
        "n_meses": len(meses),
        "primeiro": MESES[meses[0]],
        "ultimo": MESES[meses[-1]],
        "internacoes": analisadas,
        "baixadas": baixadas,
        "de_fora": baixadas - analisadas,
        "de_fora_pct": 100 * (baixadas - analisadas) / baixadas,
        "ufs_de_fora": ", ".join(
            f"{uf} ({mil(v)})" for uf, v in de_fora.head(4).items()
        ),
        "n_ufs_de_fora": len(de_fora),
    }


@st.cache_data
def fluxo_interestadual() -> dict[str, float | int | str]:
    """O sentido de SAÍDA da fronteira: paraibanos internados em PE, RN ou CE.

    Vem da tabela da PA-5 (`01-pa5-interestadual.ipynb`), e não da matriz do painel, por
    um motivo da própria fonte: o SIH organiza os arquivos pela UF do HOSPITAL, então um
    paraibano internado em Recife nunca aparece no arquivo da Paraíba. Foi preciso baixar
    os arquivos dos três vizinhos e filtrar quem mora aqui — é outra base, e por isso
    esses casos não entram em nenhum número das outras abas.
    """
    df = pd.read_csv(DIR_OUTPUTS / "tables" / "pa5_ranking_destinos.csv")
    maior = df.loc[df["internacoes"].idxmax()]
    total = int(df["internacoes"].sum())
    de_fora = int(carregar_matriz_bruta()["internacoes"].sum()) - int(
        carregar_matriz_municipal()["internacoes"].sum()
    )
    return {
        "total": total,
        "destino_principal": f"{maior['nome_mun_destino']}/{maior['uf_destino']}",
        "pct_principal": float(maior["pct_do_total_fora"]),
        "razao": total / de_fora,
    }


def aba_sobre() -> None:
    # Esta aba é a formalidade do trabalho — a procedência do dado. Recebe de propósito
    # menos destaque visual que as demais: quem chega aqui já quer ler texto, não ser
    # convencido de nada.
    ui.cabecalho_secao(
        "database",
        "De onde vêm estes números",
        "Uma fonte pública, baixada uma vez e guardada dentro do projeto. Nada aqui foi "
        "estimado, ajustado ou completado por nós.",
    )

    cob = cobertura_da_base()
    ui.cartoes_numero(
        [
            {"rotulo": "Fonte", "valor": "SIH/SUS", "icone": "database",
             "nota": "Sistema de Informações Hospitalares do DATASUS / Ministério da Saúde."},
            {"rotulo": "Período coberto", "valor": f"{cob['n_meses']} meses", "icone": "calendar",
             "nota": f"De {cob['primeiro'].lower()} a {cob['ultimo'].lower()} de 2025."},
            {"rotulo": "Internações analisadas", "valor": mil(cob["internacoes"]), "icone": "cross",
             "nota": "De moradores da Paraíba, cada uma com o município de moradia e o de internação."},
        ]
    )

    st.markdown(
        f"""
Tudo o que aparece neste painel vem de **uma única fonte pública**: o SIH/SUS, o sistema
em que o Ministério da Saúde registra toda internação paga pelo SUS no país. O arquivo que
usamos se chama **RD** ("AIH reduzida") e traz uma linha por internação, com duas
informações que são o coração do projeto: **em que município o paciente mora** e **em que
município ele foi internado**. É a diferença entre esses dois campos que chamamos de
*evasão*.

Baixamos os arquivos da Paraíba de **{cob["primeiro"].lower()} a {cob["ultimo"].lower()} de
2025** — {cob["n_meses"]} meses, {mil(cob["baixadas"])} internações — direto do
servidor do DATASUS.
"""
    )

    inter = fluxo_interestadual()
    with st.expander("A fronteira atravessa nos dois sentidos", expanded=True):
        st.markdown(
            f"""
O arquivo que o DATASUS publica para a Paraíba traz **as internações que aconteceram em
hospitais daqui** — e não "as internações dos paraibanos". São coisas diferentes, porque
hospital não pede comprovante de residência, e a divisa não é uma parede. Há gente
cruzando a fronteira nos dois sentidos, e o painel trata cada sentido de um jeito.

**Quem vem de fora e interna aqui: {mil(cob["de_fora"])} internações
({pct(cob["de_fora_pct"])} do arquivo).** Moradores de {cob["n_ufs_de_fora"]} estados —
os maiores volumes são {cob["ufs_de_fora"]}. É o vizinho de Pernambuco que interna em
Patos, o do Rio Grande do Norte que interna em Catolé do Rocha.

**Essas internações ficam de fora de tudo o que este painel mostra.** Os
{mil(cob["internacoes"])} casos analisados são só de quem **mora na Paraíba**. O motivo
não é conveniência, é a pergunta que o projeto faz: *a região de saúde onde a pessoa mora
dá conta de atendê-la?* Quem mora em Pernambuco não tem região de saúde na Paraíba — não
há autossuficiência a medir, e incluir esse caso inflaria o índice de dependência de um
lugar que nunca foi responsável por aquele morador.

**Quem mora aqui e interna fora: {mil(inter["total"])} internações.** Este é o sentido
mais volumoso — {inter["razao"]:.1f} vezes o de entrada — e ele **também não está na base
principal**, por um motivo técnico: o SIH organiza os arquivos pelo estado *do hospital*,
então um paraibano internado em Recife está no arquivo de Pernambuco. Ele foi medido à
parte, baixando os arquivos de PE, RN e CE: {pct(inter["pct_principal"])} desse fluxo vai
para um único destino, **{inter["destino_principal"]}**. O que ele significa está na aba
**“O que descobrimos”**, no Achado 5 e na Recomendação 4.

**A consequência honesta disso:** como a saída interestadual não entra nos cálculos desta
tela, **todo índice deste painel é um piso**. A dependência real de cada região é igual ou
maior que a mostrada aqui — nunca menor.
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
    ui.injetar_estilo()

    capa = numeros_de_capa()
    ui.capa(
        etiqueta="Paraíba · 2025 · SIH/DATASUS",
        titulo="Para onde o paraibano vai",
        destaque="quando precisa internar",
        subtitulo=(
            f"{mil(capa['internacoes'])} internações de moradores da Paraíba pelo SUS em 2025, "
            "rastreadas da cidade onde a pessoa mora até o hospital onde ela foi atendida."
        ),
    )

    # Os quatro números de capa ficam ANTES das abas, não dentro de uma delas: são a
    # resposta curta do projeto, e quem abre o painel deve recebê-la sem precisar clicar.
    ui.cartoes_numero(
        [
            {
                "rotulo": "Internações em 2025",
                "valor": mil(capa["internacoes"]),
                "icone": "cross",
                "nota": "Internações de moradores da Paraíba pagas pelo SUS.",
            },
            {
                "rotulo": "Saíram da própria cidade",
                "valor": pct(capa["fora_pct"]),
                "icone": "route",
                "cor": ui.ALERTA,
                "nota": "Precisaram viajar para se internar.",
            },
            {
                "rotulo": f"Absorvido por {capa['polos_nomes']}",
                "valor": pct(capa["polos_pct"]),
                "icone": "map-pin",
                "cor": ui.ACENTO,
                "nota": "De tudo que se deslocou, esta fatia parou em duas cidades.",
            },
            {
                "rotulo": "Regiões que dependem de fora",
                "valor": f"{capa['regioes_alta']} de {capa['regioes_total']}",
                "icone": "triangle-alert",
                "cor": ui.CRITICO,
                "nota": "Internam a maioria dos moradores fora da região.",
            },
        ]
    )

    # Rótulos das abas em linguagem de quem não conhece o projeto: "Matriz O-D" e
    # "Índice de dependência" são nomes internos — na tela viram a pergunta que a aba
    # responde. O nome técnico continua dentro da aba, junto da explicação.
    matriz, mapa, indice, achados, sobre = st.tabs(
        [
            "Quem vai para onde",
            "No mapa",
            "Quem depende de quem",
            "O que descobrimos",
            "De onde vêm os dados",
        ]
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
