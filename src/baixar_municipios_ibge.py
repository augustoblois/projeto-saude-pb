"""Baixa a tabela oficial de municípios do IBGE e salva como CSV versionado.

Fonte: API de Localidades do IBGE
    https://servicodados.ibge.gov.br/api/v1/localidades/municipios

Por que este script existe:
- O SIH/DATASUS identifica municípios por CÓDIGO (ex.: 250750), não por nome.
- Para as análises falarem "João Pessoa" em vez de "250750", precisamos da
  tabela código -> nome. Ela é baixada UMA vez aqui e fica versionada no git
  (`data/raw/municipios_ibge.csv`) — depois disso, nada no projeto depende
  de internet (regra fixa: dados congelados, apresentação 100% offline).

Detalhe importante (6 vs 7 dígitos):
- O código IBGE oficial tem 7 dígitos (ex.: 2507507 = João Pessoa).
  O 7º dígito é um dígito verificador (como o último dígito do CPF).
- O SIH grava o código com apenas 6 dígitos (sem o verificador): 250750.
- Por isso o CSV salvo traz as duas formas: `codigo_ibge7` (oficial) e
  `codigo_ibge6` (os 6 primeiros dígitos, usados no join com o SIH).
  O prefixo de 6 dígitos é único nacionalmente, então o join é seguro.

Uso (uma única vez, com internet):
    python src/baixar_municipios_ibge.py
"""

import csv
import gzip
import json
import urllib.request
from pathlib import Path

URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
DESTINO = Path(__file__).resolve().parent.parent / "data" / "raw" / "municipios_ibge.csv"


def main() -> None:
    print(f"Baixando lista de municípios de {URL} ...")
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = resposta.read()
    # A API pode responder compactada (gzip); descompacta se for o caso.
    if dados[:2] == b"\x1f\x8b":
        dados = gzip.decompress(dados)
    municipios = json.loads(dados)
    print(f"Recebidos {len(municipios)} municípios.")

    linhas = []
    for m in municipios:
        codigo7 = str(m["id"])
        # A UF vem aninhada na divisão regional. Alguns municípios não têm a
        # divisão antiga (microrregião); nesses casos usa a divisão nova
        # (região imediata -> região intermediária -> UF).
        if m.get("microrregiao"):
            uf = m["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        else:
            uf = m["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
        linhas.append(
            {
                "codigo_ibge7": codigo7,
                "codigo_ibge6": codigo7[:6],
                "nome": m["nome"],
                "uf": uf,
            }
        )

    # Sanidade: o prefixo de 6 dígitos precisa ser único para o join ser seguro.
    codigos6 = [linha["codigo_ibge6"] for linha in linhas]
    assert len(codigos6) == len(set(codigos6)), "Código de 6 dígitos duplicado!"

    linhas.sort(key=lambda linha: linha["codigo_ibge7"])
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with open(DESTINO, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=["codigo_ibge7", "codigo_ibge6", "nome", "uf"]
        )
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"Salvo em {DESTINO} ({len(linhas)} municípios).")


if __name__ == "__main__":
    main()
