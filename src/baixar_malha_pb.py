"""Congela a malha geográfica dos 223 municípios da PB e deriva os centroides.

Fonte: API de Malhas Territoriais do IBGE (v3) — malha da UF 25 (Paraíba),
recortada internamente por município.

    URL exata usada no download:
    https://servicodados.ibge.gov.br/api/v3/malhas/estados/25
        ?formato=application/vnd.geo+json
        &intrarregiao=municipio
        &qualidade=intermediaria

    Documentação da API: https://servicodados.ibge.gov.br/api/docs/malhas
    Data do download que gerou o arquivo versionado no repo: 25/07/2026.

Por que ESTA fonte: é a mesma base cartográfica oficial do IBGE que define os
códigos de município usados no SIH/DATASUS — malha e dados vêm do mesmo
universo, sem risco de contorno que não corresponde a nenhum código.

Por que `qualidade=intermediaria` (as quatro opções foram medidas, 25/07/2026):
    minima        =  86 KB — contorno já visivelmente deformado
    intermediaria = 215 KB — escolhida
    maxima        = 837 KB (= o padrão, quando o parâmetro é omitido)
Comparando os centroides de cada versão contra a `maxima` (referência):
`intermediaria` desloca no MÁXIMO 144 m (média 23 m) — irrelevante para um
mapa estadual; `minima` desloca até 2,3 km, o que já move o ponto para fora
do município em casos extremos. `intermediaria` é 4x mais leve que a `maxima`,
versiona confortavelmente no git e renderiza rápido no Streamlit.

O que este script grava (ambos versionados no git — regra fixa nº 1 do
projeto: a apresentação não depende de fonte viva):
    outputs/malha_municipios_pb.geojson  -> polígonos, um por município
    outputs/centroides_municipios_pb.csv -> um ponto (lon, lat) por município

Chave de junção — a armadilha desta tarefa:
- O IBGE identifica cada município por um código de 7 dígitos (`codarea`,
  ex.: 2507507 = João Pessoa); o 7º é dígito verificador.
- O SIH/DATASUS — e portanto TODA a base deste projeto
  (`matriz_od_municipal_mensal.parquet`, `regioes_saude_pb.csv`) — usa os 6
  primeiros dígitos: 250750.
- A chave adotada é a de 6 dígitos (`cod_mun`), obtida por corte dos 7.
  O prefixo de 6 dígitos é único nacionalmente, então o corte é seguro.
- O script só grava se os 223 municípios da malha casarem 1-para-1 com os 223
  de `data/processed/regioes_saude_pb.csv`. Órfão de qualquer lado = ValueError.
  Um casamento errado pintaria a cidade trocada no mapa sem dar erro nenhum.

Enriquecimento das propriedades: o geojson do IBGE traz SÓ `codarea`. Este
script acrescenta `cod_mun` (6 dígitos) e `nome_mun` a cada feature, para o
mapa do Streamlit conseguir ligar polígono <-> dados direto
(`featureidkey="properties.cod_mun"`), sem tabela auxiliar. A geometria não é
tocada. Os nomes vêm de `data/raw/municipios_ibge.csv` (API de Localidades do
IBGE, congelada por `src/baixar_municipios_ibge.py`) — não de
`regioes_saude_pb.csv`, cujos nomes vêm sem acento do DATASUS.

ORIENTAÇÃO DOS ANÉIS (winding order) — NÃO "ARRUME" ISTO:
- A malha chega do IBGE com todos os 223 anéis externos no sentido ANTI-HORÁRIO
  (área assinada positiva), que é o que a RFC 7946 (padrão GeoJSON) pede.
- O Plotly, no backend `geo` (`px.choropleth`), desenha com o d3-geo, que
  interpreta polígonos em geometria ESFÉRICA. Nela um anel anti-horário
  delimita o COMPLEMENTO da figura: "todo o globo, menos este município".
  Resultado observado: os 223 polígonos pintavam o mundo inteiro sobrepostos e
  o mapa virava um bloco retangular sólido, com um único contorno visível.
- Por isso este script grava os anéis externos no sentido HORÁRIO (área
  assinada negativa), invertendo de propósito a convenção da RFC 7946, e os
  anéis internos (buracos) no sentido oposto ao externo. Testado A/B no
  browser: com a inversão a Paraíba aparece com os 223 contornos individuais.
- `validar()` quebra se algum anel externo voltar a ficar anti-horário — a
  checagem existe exatamente para impedir que esta correção seja desfeita sem
  querer numa futura "limpeza" do código.
- A normalização é por ORIENTAÇÃO, não um `reversed()` cego: rodar o script
  duas vezes não desfaz a correção.

Centroide: calculado em Python puro pela fórmula do centroide de ÁREA do
polígono (nada de geopandas/shapely — o projeto não instala dependências novas,
US-18). Não é a média dos vértices, que enviesaria o ponto para o lado do
contorno com mais detalhe. Regra para MultiPolygon (só Cabedelo, 2503209, que
tem ilhas): usa a MAIOR parte por área, para o rótulo cair no continente e não
no meio do mar.

Idempotente: se o geojson já existe, NÃO rebaixa — só relê, revalida e refaz
o CSV de centroides.

Uso (uma única vez, com internet):
    python src/baixar_malha_pb.py
"""

import csv
import gzip
import json
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
OUTPUTS = RAIZ / "outputs"
MALHA = OUTPUTS / "malha_municipios_pb.geojson"
CENTROIDES = OUTPUTS / "centroides_municipios_pb.csv"

MUNICIPIOS_IBGE = RAIZ / "data" / "raw" / "municipios_ibge.csv"
REGIOES_SAUDE = RAIZ / "data" / "processed" / "regioes_saude_pb.csv"

URL = (
    "https://servicodados.ibge.gov.br/api/v3/malhas/estados/25"
    "?formato=application/vnd.geo+json"
    "&intrarregiao=municipio"
    "&qualidade=intermediaria"
)

N_MUNICIPIOS_PB = 223
# Retângulo que contém a Paraíba inteira, com folga. Serve para pegar o erro
# clássico de inverter longitude com latitude: um ponto invertido cai
# grosseiramente fora daqui e o script quebra.
LON_MIN, LON_MAX = -38.8, -34.7
LAT_MIN, LAT_MAX = -8.3, -6.0


def baixar_malha() -> dict:
    """Baixa a malha do IBGE (ou relê a já congelada, se existir)."""
    if MALHA.exists():
        print(f"malha já congelada: {MALHA.name} ({MALHA.stat().st_size:,} bytes)")
        return json.loads(MALHA.read_text(encoding="utf-8"))
    print(f"baixando malha municipal da PB de {URL} ...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as resposta:
        dados = resposta.read()
    if dados[:2] == b"\x1f\x8b":  # resposta compactada (gzip)
        dados = gzip.decompress(dados)
    malha = json.loads(dados)
    print(f"recebidas {len(malha['features'])} feições ({len(dados):,} bytes)")
    return malha


def ler_nomes() -> dict[str, str]:
    """Lê o de-para código de 6 dígitos -> nome do município (só PB)."""
    with open(MUNICIPIOS_IBGE, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    return {
        linha["codigo_ibge6"]: linha["nome"] for linha in linhas if linha["uf"] == "PB"
    }


def ler_codigos_do_projeto() -> set[str]:
    """Lê os códigos de 6 dígitos que a base do projeto realmente usa."""
    with open(REGIOES_SAUDE, encoding="utf-8") as arquivo:
        return {linha["codigo_municipio"] for linha in csv.DictReader(arquivo)}


def anotar_features(malha: dict, nomes: dict[str, str]) -> dict:
    """Acrescenta `cod_mun` (6 dígitos) e `nome_mun` às propriedades."""
    for feicao in malha["features"]:
        codigo7 = str(feicao["properties"]["codarea"])
        if len(codigo7) != 7:
            raise ValueError(f"codarea fora do padrão de 7 dígitos: {codigo7!r}")
        codigo6 = codigo7[:6]
        feicao["properties"]["cod_mun"] = codigo6
        feicao["properties"]["nome_mun"] = nomes.get(codigo6)
    return malha


def _area_assinada(anel: list[list[float]]) -> float:
    """Área assinada do anel (fórmula do shoelace).

    O SINAL é o que interessa aqui: positivo = vértices em sentido anti-horário,
    negativo = horário. O valor em si sai em graus², que não é área de verdade.
    """
    soma = 0.0
    for atual, seguinte in zip(anel, anel[1:]):
        soma += atual[0] * seguinte[1] - seguinte[0] * atual[1]
    return soma / 2.0


def _partes(geometria: dict) -> list[list[list[list[float]]]]:
    """Lista as partes de um polígono. Polygon vira uma lista de 1 parte.

    Cada parte é uma lista de anéis: o primeiro é o externo, os demais (se
    houver) são buracos.
    """
    tipo = geometria["type"]
    if tipo == "Polygon":
        return [geometria["coordinates"]]
    if tipo == "MultiPolygon":
        return geometria["coordinates"]
    raise ValueError(f"geometria inesperada: {tipo}")


def orientar_aneis(malha: dict) -> dict:
    """Força anel externo HORÁRIO e buracos ANTI-HORÁRIOS (exigência do d3-geo).

    Ver a seção "ORIENTAÇÃO DOS ANÉIS" no cabeçalho do arquivo: o d3-geo, que o
    Plotly usa em `px.choropleth`, lê polígonos em geometria esférica, onde um
    anel anti-horário significa "todo o globo menos esta figura" — e o mapa sai
    como um bloco sólido cobrindo o plot inteiro. Invertemos de propósito a
    convenção da RFC 7946.

    Normaliza por sinal da área, e não com um `reversed()` cego: quem já está no
    sentido certo não é tocado, então reprocessar o arquivo é seguro.
    """
    invertidos = 0
    for feicao in malha["features"]:
        for parte in _partes(feicao["geometry"]):
            for indice, anel in enumerate(parte):
                horario_esperado = indice == 0  # anel 0 = externo; os demais, buracos
                esta_horario = _area_assinada(anel) < 0
                if esta_horario != horario_esperado:
                    anel.reverse()
                    invertidos += 1
    print(f"orientação dos anéis normalizada: {invertidos} anéis invertidos")
    return malha


def _centroide_do_anel(anel: list[list[float]]) -> tuple[float, float, float]:
    """Centroide de área e área (com sinal) de um anel fechado do polígono.

    Fórmula clássica do centroide de polígono: percorre os pares de vértices
    consecutivos acumulando o produto cruzado. É o "centro de massa" da chapa
    recortada no formato do município — diferente da média dos vértices, que
    puxa o ponto para o trecho de contorno mais detalhado.

    A área sai em graus², o que NÃO é área de verdade — serve só para comparar
    partes do mesmo município (qual ilha é a maior), nunca como km².
    """
    soma_area = soma_x = soma_y = 0.0
    for atual, seguinte in zip(anel, anel[1:]):
        x0, y0 = atual[0], atual[1]
        x1, y1 = seguinte[0], seguinte[1]
        cruzado = x0 * y1 - x1 * y0
        soma_area += cruzado
        soma_x += (x0 + x1) * cruzado
        soma_y += (y0 + y1) * cruzado
    area = soma_area / 2.0
    if area == 0:
        raise ValueError("anel com área zero — geometria degenerada")
    return soma_x / (6 * area), soma_y / (6 * area), abs(area)


def centroide_da_feicao(feicao: dict) -> tuple[float, float]:
    """Centroide de um município. MultiPolygon -> maior parte por área."""
    partes = _partes(feicao["geometry"])
    # partes[i][0] = anel externo; os demais anéis seriam buracos (não há
    # nenhum na malha da PB, e um buraco não deslocaria o rótulo o bastante
    # para justificar a complexidade).
    candidatos = [_centroide_do_anel(parte[0]) for parte in partes]
    lon, lat, _ = max(candidatos, key=lambda item: item[2])
    return lon, lat


def montar_centroides(malha: dict) -> list[dict]:
    """Monta a lista de centroides, um por município, ordenada por código."""
    linhas = []
    for feicao in malha["features"]:
        lon, lat = centroide_da_feicao(feicao)
        linhas.append(
            {
                "cod_mun": feicao["properties"]["cod_mun"],
                "nome_mun": feicao["properties"]["nome_mun"],
                "lon": round(lon, 6),  # ~10 cm de precisão, de sobra
                "lat": round(lat, 6),
            }
        )
    linhas.sort(key=lambda linha: linha["cod_mun"])
    return linhas


def validar(malha: dict, centroides: list[dict], codigos_projeto: set[str]) -> None:
    """Valida a malha e os centroides. Qualquer falha aborta a gravação."""
    erros: list[str] = []

    if len(malha["features"]) != N_MUNICIPIOS_PB:
        erros.append(
            f"esperava {N_MUNICIPIOS_PB} municípios na malha, "
            f"veio {len(malha['features'])}"
        )

    codigos_malha = [linha["cod_mun"] for linha in centroides]
    if len(codigos_malha) != len(set(codigos_malha)):
        erros.append("código de 6 dígitos duplicado na malha")

    # O ponto crítico: casamento 1-para-1 com a base do projeto, nos dois
    # sentidos. Órfão de qualquer lado significa polígono sem dado ou dado sem
    # polígono — e, no pior caso, cidade errada pintada no mapa.
    so_na_malha = set(codigos_malha) - codigos_projeto
    so_no_projeto = codigos_projeto - set(codigos_malha)
    if so_na_malha:
        erros.append(f"{len(so_na_malha)} códigos só na malha: {sorted(so_na_malha)}")
    if so_no_projeto:
        erros.append(
            f"{len(so_no_projeto)} códigos só na base do projeto: "
            f"{sorted(so_no_projeto)}"
        )

    sem_nome = [linha["cod_mun"] for linha in centroides if not linha["nome_mun"]]
    if sem_nome:
        erros.append(f"{len(sem_nome)} municípios sem nome: {sem_nome}")

    fora = [
        linha
        for linha in centroides
        if not (LON_MIN <= linha["lon"] <= LON_MAX and LAT_MIN <= linha["lat"] <= LAT_MAX)
    ]
    if fora:
        erros.append(
            f"{len(fora)} centroides fora do retângulo da PB "
            f"(lon {LON_MIN}..{LON_MAX}, lat {LAT_MIN}..{LAT_MAX}): "
            f"{[(f['cod_mun'], f['lon'], f['lat']) for f in fora[:5]]}"
        )

    # Orientação dos anéis: é o bug que quebrou o mapa e que nenhuma das
    # checagens acima pegaria — contagem, órfãos e retângulo passavam todos
    # enquanto o Plotly pintava um bloco sólido no lugar da Paraíba.
    externos_antihorarios = [
        feicao["properties"]["cod_mun"]
        for feicao in malha["features"]
        for parte in _partes(feicao["geometry"])
        if _area_assinada(parte[0]) > 0
    ]
    if externos_antihorarios:
        erros.append(
            f"{len(externos_antihorarios)} anéis externos anti-horários "
            f"(ex.: {externos_antihorarios[:5]}) — o d3-geo/Plotly pintaria o "
            "complemento e o mapa viraria um bloco sólido; ver a seção "
            "ORIENTAÇÃO DOS ANÉIS no cabeçalho deste arquivo"
        )

    if erros:
        raise ValueError("validação FALHOU: " + "; ".join(erros))

    lons = [linha["lon"] for linha in centroides]
    lats = [linha["lat"] for linha in centroides]
    print(
        f"validação OK: {len(centroides)} municípios na malha casando 1-para-1 "
        f"com os {len(codigos_projeto)} da base do projeto (0 órfãos)"
    )
    print(
        f"  extensão dos centroides: lon {min(lons):.3f}..{max(lons):.3f}, "
        f"lat {min(lats):.3f}..{max(lats):.3f} — dentro da PB"
    )
    print(
        "  todos os anéis externos no sentido horário — como o d3-geo/Plotly "
        "precisa para desenhar o município, e não o resto do mundo"
    )
    multipoligonos = [
        feicao["properties"]["nome_mun"]
        for feicao in malha["features"]
        if feicao["geometry"]["type"] == "MultiPolygon"
    ]
    print(
        f"  municípios com mais de uma parte (ilhas/enclaves): "
        f"{multipoligonos or 'nenhum'} — usada a maior parte por área"
    )


def main() -> None:
    malha = baixar_malha()
    malha = anotar_features(malha, ler_nomes())
    malha = orientar_aneis(malha)
    centroides = montar_centroides(malha)
    validar(malha, centroides, ler_codigos_do_projeto())

    # O que é idempotente é o DOWNLOAD (não rebaixa se o arquivo existe); a
    # gravação acontece sempre, porque anotação e orientação dos anéis são
    # normalizações que precisam ser aplicadas também a um arquivo já congelado.
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    # separators sem espaços: mesmo conteúdo, arquivo bem menor no git.
    MALHA.write_text(
        json.dumps(malha, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"salvo: {MALHA} ({MALHA.stat().st_size:,} bytes)")

    with open(CENTROIDES, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=["cod_mun", "nome_mun", "lon", "lat"]
        )
        escritor.writeheader()
        escritor.writerows(centroides)
    print(f"salvo: {CENTROIDES} ({len(centroides)} municípios)")


if __name__ == "__main__":
    main()
