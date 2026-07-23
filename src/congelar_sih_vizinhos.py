# Congela o recorte interestadual da US-08 (PA-5): residentes da PB internados
# em PE, RN e CE ao longo de 2025.
#
# POR QUE ESTE SCRIPT EXISTE (decisão D-1 do backlog):
#   Os arquivos RD do SIH/DATASUS são organizados pela UF do HOSPITAL, não do
#   paciente. Um paraibano internado em Recife aparece no arquivo de PE
#   (RDPE2501.dbc), nunca no da PB. Para medir a evasão interestadual é preciso
#   baixar os RD das UFs vizinhas e filtrar só as linhas cujo MUNIC_RES
#   (município de residência, código IBGE) começa com "25" — prefixo da PB.
#
# FLUXO (mesmo padrão validado em src/congelar_sih.py):
#   FTP ftp.datasus.gov.br -> .dbc -> .dbf -> DataFrame -> filtro PB -> parquet
#
# ESTRATÉGIA DE ARQUIVOS:
#   - Staging: data/raw/_staging_vizinhos/rd_{uf}_{ano}_{mes}.parquet
#     Um parquet filtrado por UF×mês. É o que dá idempotência: mês já filtrado
#     não é baixado de novo. Fica fora do git (ver .gitignore).
#   - Final: data/raw/sih_pb_residentes_fora_2025.parquet — UM parquet com as
#     36 fatias concatenadas (12 meses × 3 UFs), todas as colunas originais.
#     Só é (re)escrito quando as 36 fatias existem — recorte parcial não entra
#     na base pra não enviesar a análise (guard-rail da US-08: se faltar mês no
#     FTP, reporta e a decisão de degradar a PA-5 é humana).
#   - Os .dbc/.dbf intermediários (grandes, PE ~dezenas de MB/mês) são APAGADOS
#     logo após a conversão de cada mês — não sobra lixo em disco.
#
# Fonte: DATASUS, SIH/SUS — arquivos RD (AIH reduzida), ftp.datasus.gov.br,
# diretório /dissemin/publicos/SIHSUS/200801_/Dados (via PySUS FTP direto;
# a API de conveniência do PySUS não serve — ver wiki do projeto).
import asyncio
from pathlib import Path

import pandas as pd
from pysus.api.ftp.client import FTP
from pysus.api.ftp.databases import SIH
from pyreaddbc import dbc2dbf
from pysus.data.dbf_reader import read_dbf_fast

RAW = Path("data/raw")
STAGING = RAW / "_staging_vizinhos"  # fatias filtradas por UF×mês (fora do git)
STAGING.mkdir(parents=True, exist_ok=True)

ANO = 2025
MESES = range(1, 13)
UFS = ["PE", "RN", "CE"]  # UFs vizinhas da PB
PREFIXO_PB = "25"  # códigos IBGE de municípios da PB começam com 25
FINAL = RAW / f"sih_pb_residentes_fora_{ANO}.parquet"


def staging_path(uf: str, mes: int) -> Path:
    return STAGING / f"rd_{uf.lower()}_{ANO}_{mes:02d}.parquet"


def filtrar_e_congelar(uf: str, mes: int, dbc_path: Path) -> str:
    """DBC -> DBF -> DataFrame -> filtra residentes PB -> parquet de staging.

    Apaga o .dbc e o .dbf ao final (arquivos grandes; só a fatia filtrada,
    que é pequena, fica em disco).
    """
    dbf_path = dbc_path.with_suffix(".dbf")
    try:
        if not dbf_path.exists():
            dbc2dbf(str(dbc_path), str(dbf_path))
        df = read_dbf_fast(dbf_path)
        if "MUNIC_RES" not in df.columns:
            return "ERRO: coluna MUNIC_RES ausente"
        total = len(df)
        # Filtro central da US-08: só quem MORA na PB (código IBGE 25xxxx).
        recorte = df[df["MUNIC_RES"].astype(str).str.startswith(PREFIXO_PB)].copy()
        recorte.to_parquet(staging_path(uf, mes))
        return f"OK — {len(recorte)} residentes PB de {total} internações"
    finally:
        # Limpeza incondicional dos intermediários pesados.
        dbc_path.unlink(missing_ok=True)
        dbf_path.unlink(missing_ok=True)


async def baixar_e_processar() -> list[tuple[str, int]]:
    """Baixa e processa cada UF×mês sem fatia de staging. Uma conexão FTP.

    Retorna a lista de (uf, mes) AUSENTES no FTP (guard-rail: só reportar,
    nunca improvisar fonte alternativa).
    """
    pendentes = [
        (uf, mes) for uf in UFS for mes in MESES if not staging_path(uf, mes).exists()
    ]
    if not pendentes:
        print("Todas as 36 fatias já estão em staging — nada a baixar.")
        return []
    ausentes: list[tuple[str, int]] = []
    client = FTP()
    await client.connect()
    try:
        sih = SIH(client=client)
        contents = await sih.content
        por_nome = {str(f): f for f in contents}
        for uf, mes in pendentes:
            alvo = f"RD{uf}{ANO % 100:02d}{mes:02d}.dbc"
            if alvo not in por_nome:
                print(f"[{uf} {mes:02d}] AUSENTE no FTP: {alvo}")
                ausentes.append((uf, mes))
                continue
            print(f"[{uf} {mes:02d}] baixando {alvo}...")
            local = Path(await client.download(por_nome[alvo], RAW / alvo))
            try:
                status = filtrar_e_congelar(uf, mes, local)
            except Exception as e:  # falha de um mês não derruba os outros
                status = f"ERRO: {e}"
            print(f"[{uf} {mes:02d}] {status}")
    finally:
        await client.close()
    return ausentes


def consolidar_e_validar(ausentes: list[tuple[str, int]]) -> None:
    """Concatena as 36 fatias no parquet final e imprime as validações da US-08."""
    existentes = [(uf, mes) for uf in UFS for mes in MESES if staging_path(uf, mes).exists()]

    print("\n=== Validação (a): completude 12 meses × 3 UFs ===")
    print(f"Fatias processadas: {len(existentes)}/36")
    faltando = [(uf, mes) for uf in UFS for mes in MESES if (uf, mes) not in existentes]
    if faltando:
        for uf, mes in faltando:
            motivo = "AUSENTE NO FTP" if (uf, mes) in ausentes else "falha no processamento"
            print(f"  FALTA: {uf} {ANO}-{mes:02d} ({motivo})")
        print(
            "\nCongelamento INCOMPLETO — parquet final NÃO será escrito.\n"
            "Guard-rail US-08: não improvisar fonte alternativa; decisão de\n"
            "degradar a PA-5 para nota metodológica é humana."
        )
        return
    print("  OK — 36/36 fatias presentes.")

    df = pd.concat(
        [pd.read_parquet(staging_path(uf, mes)) for uf, mes in existentes],
        ignore_index=True,
    )
    df.to_parquet(FINAL)

    print("\n=== Validação (b): linhas por UF do hospital e total ===")
    # A UF do hospital é o prefixo de MUNIC_MOV (26=PE, 24=RN, 23=CE).
    prefixo_uf = {"26": "PE", "24": "RN", "23": "CE"}
    uf_hosp = df["MUNIC_MOV"].astype(str).str[:2].map(prefixo_uf).fillna("OUTRA?")
    print(uf_hosp.value_counts().to_string())
    print(f"TOTAL: {len(df)}")

    print("\n=== Validação (c): 100% MUNIC_RES iniciando em 25 ===")
    fora = (~df["MUNIC_RES"].astype(str).str.startswith(PREFIXO_PB)).sum()
    print("  OK — todas as linhas são de residentes PB." if fora == 0
          else f"  ERRO — {fora} linhas com MUNIC_RES fora da PB!")

    print("\n=== Validação (d): distribuição por mês (sem buracos) ===")
    por_mes = df.groupby("MES_CMPT").size().reindex(
        [f"{m:02d}" for m in MESES], fill_value=0
    )
    print(por_mes.to_string())
    buracos = por_mes[por_mes == 0].index.tolist()
    print(f"  {'OK — 12 meses com registros.' if not buracos else f'ATENÇÃO — meses sem registros: {buracos}'}")

    tam_mb = FINAL.stat().st_size / 1024 / 1024
    print(f"\nParquet final: {FINAL} ({tam_mb:.1f} MB, {len(df)} linhas, {df.shape[1]} colunas)")


if __name__ == "__main__":
    if FINAL.exists():
        print(f"{FINAL.name} já existe — revalidando sem baixar nada.")
        ausentes: list[tuple[str, int]] = []
    else:
        ausentes = asyncio.run(baixar_e_processar())
    consolidar_e_validar(ausentes)
