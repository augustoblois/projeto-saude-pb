"""Baixa a estimativa populacional municipal do IBGE e salva como CSV versionado.

Fonte: API SIDRA do IBGE — tabela 6579 ("População residente estimada"),
variável 9324, nível territorial 6 (município), período `last` (ano mais recente
publicado).

    URL exata usada no download:
    https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/last

    Página de referência da tabela (contexto/metodologia):
    https://sidra.ibge.gov.br/tabela/6579

    Data do download que gerou o CSV versionado no repo: 24/07/2026.
    Ano de referência retornado pela API nesse download: 2025.

Por que este script existe (decisão D-3 do backlog):
- A US-06 (PA-3) pergunta se a taxa de evasão hospitalar depende do PORTE do
  município. "Porte" aqui = população residente estimada pelo IBGE.
- A regra fixa do projeto é que nada na apresentação dependa de fonte viva:
  este script roda UMA vez, com internet, e congela o resultado em
  `data/raw/populacao_ibge_municipios.csv`. O notebook da análise lê o CSV,
  nunca a API.

Detalhe importante (6 vs 7 dígitos):
- O código IBGE oficial tem 7 dígitos (ex.: 2507507 = João Pessoa); o 7º é um
  dígito verificador. O SIH/DATASUS grava só os 6 primeiros (250750).
- Este CSV guarda o código de 7 dígitos (`cod_ibge`), como pedido no contrato da
  story. O de-para para 6 dígitos JÁ EXISTE no repo, em
  `data/raw/municipios_ibge.csv` (colunas `codigo_ibge7` / `codigo_ibge6`,
  gerado por `src/baixar_municipios_ibge.py`) — o notebook reaproveita essa
  tabela para o join com o SIH, em vez de duplicar a regra aqui.

Uso (uma única vez, com internet):
    python src/baixar_populacao_ibge.py
"""

import csv
import gzip
import json
import urllib.request
from pathlib import Path

URL = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/last"
DESTINO = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "populacao_ibge_municipios.csv"
)
# A Paraíba tem 223 municípios (código de UF = 25, os dois primeiros dígitos).
UF_PB = "25"
MUNICIPIOS_PB_ESPERADOS = 223


def baixar(url: str) -> list[dict]:
    """Baixa e decodifica o JSON da API do SIDRA."""
    print(f"Baixando estimativa populacional de {url} ...")
    # A API do SIDRA rejeita clientes sem User-Agent em algumas rotas.
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as resposta:
        dados = resposta.read()
    if dados[:2] == b"\x1f\x8b":  # resposta compactada (gzip)
        dados = gzip.decompress(dados)
    return json.loads(dados)


def main() -> None:
    registros = baixar(URL)
    # A primeira linha do retorno do SIDRA é o CABEÇALHO descritivo (dicionário
    # de rótulos), não um dado. Descartamos.
    cabecalho, registros = registros[0], registros[1:]
    print(f"Recebidos {len(registros)} municípios (cabeçalho: {cabecalho['V']}).")

    linhas = []
    for r in registros:
        codigo7 = str(r["D1C"])
        # O nome vem no formato "Alta Floresta D'Oeste - RO": nome + " - " + UF.
        nome, _, uf = r["D1N"].rpartition(" - ")
        linhas.append(
            {
                "cod_ibge": codigo7,
                "nome_municipio": nome.strip(),
                "uf": uf.strip(),
                "populacao": int(r["V"]),
                "ano_referencia": int(r["D3C"]),
            }
        )

    # --- Validações antes de gravar -------------------------------------
    anos = {linha["ano_referencia"] for linha in linhas}
    assert len(anos) == 1, f"Mais de um ano de referência no retorno: {anos}"
    ano = anos.pop()

    codigos = [linha["cod_ibge"] for linha in linhas]
    assert len(codigos) == len(set(codigos)), "Código IBGE duplicado!"
    assert all(len(c) == 7 for c in codigos), "Código IBGE fora do padrão de 7 dígitos!"

    pb = [linha for linha in linhas if linha["cod_ibge"].startswith(UF_PB)]
    assert len(pb) == MUNICIPIOS_PB_ESPERADOS, (
        f"Esperados {MUNICIPIOS_PB_ESPERADOS} municípios da PB, "
        f"encontrados {len(pb)}."
    )
    assert all(linha["populacao"] > 0 for linha in linhas), "População <= 0!"

    print(f"Ano de referência: {ano}")
    print(f"Municípios da PB encontrados: {len(pb)} (esperados {MUNICIPIOS_PB_ESPERADOS}) — OK")
    print(f"População total da PB: {sum(linha['populacao'] for linha in pb):,}".replace(",", "."))

    linhas.sort(key=lambda linha: linha["cod_ibge"])
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with open(DESTINO, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=["cod_ibge", "nome_municipio", "uf", "populacao", "ano_referencia"],
        )
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"Salvo em {DESTINO} ({len(linhas)} municípios).")


if __name__ == "__main__":
    main()
