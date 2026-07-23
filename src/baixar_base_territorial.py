# Congela a relação oficial município -> região de saúde da PB (US-02).
#
# FONTE OFICIAL: FTP do DATASUS (ftp.datasus.gov.br), arquivo
#   /territorio/tabelas/2025/10-base_territorial_out25.zip
# Essa é a "base territorial" que o próprio TabWin do Ministério da Saúde usa.
# Dentro do zip, dois arquivos nos interessam:
#   - rl_municip_regsaud.csv -> relação município -> código da região de saúde
#   - tb_regsaud.csv         -> nome de cada região de saúde
#   - tb_municip.csv         -> nome de cada município (mesma fonte, sem mistura)
# Escolhemos a versão de out/2025 por ser a última de 2025 — mesmo ano da base
# de internações que estamos analisando (coerência temporal).
#
# Idempotente: se o zip já está em data/raw/ não baixa de novo; se a tabela
# final já existe em data/processed/ o script só revalida e reporta.
# Download em 2026-07-23. O zip bruto fica FORA do git (regra data/raw/*.zip).
import io
import zipfile
from ftplib import FTP
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
PROCESSED = Path("data/processed")

FTP_HOST = "ftp.datasus.gov.br"
FTP_ARQUIVO = "/territorio/tabelas/2025/10-base_territorial_out25.zip"
ZIP_LOCAL = RAW / "base_territorial_out25.zip"
TABELA_FINAL = PROCESSED / "regioes_saude_pb.csv"

# Fatos conhecidos sobre a PB, usados como validação (não como fonte):
N_MUNICIPIOS_PB = 223
N_REGIOES_PB = 16


def baixar_zip() -> Path:
    """Baixa o zip da base territorial do FTP do DATASUS (se ainda não existir)."""
    if ZIP_LOCAL.exists():
        print(f"zip já baixado: {ZIP_LOCAL.name} ({ZIP_LOCAL.stat().st_size:,} bytes)")
        return ZIP_LOCAL
    RAW.mkdir(parents=True, exist_ok=True)
    print(f"baixando {FTP_ARQUIVO} de {FTP_HOST}...")
    ftp = FTP(FTP_HOST, timeout=120)
    ftp.login()  # FTP público, login anônimo — nenhuma credencial envolvida
    try:
        with open(ZIP_LOCAL, "wb") as f:
            ftp.retrbinary(f"RETR {FTP_ARQUIVO}", f.write)
    finally:
        ftp.quit()
    print(f"ok: {ZIP_LOCAL.name} ({ZIP_LOCAL.stat().st_size:,} bytes)")
    return ZIP_LOCAL


def _ler_csv_do_zip(z: zipfile.ZipFile, nome: str) -> pd.DataFrame:
    """Lê um CSV de dentro do zip sem extrair pro disco.

    dtype=str porque códigos IBGE são identificadores, não números —
    ler como número derrubaria zeros à esquerda e quebraria o join.
    sep=None + engine python porque o DATASUS mistura separadores no MESMO
    zip (tb_municip usa ';', os demais usam ',') — o pandas detecta sozinho.
    """
    return pd.read_csv(
        io.BytesIO(z.read(nome)),
        sep=None,
        engine="python",
        encoding="utf-8",
        dtype=str,
    )


def montar_tabela_pb() -> pd.DataFrame:
    """Monta a tabela município -> região de saúde só da PB, com nomes.

    Três joins dentro da MESMA fonte oficial (nada de misturar fontes):
    rl_municip_regsaud (o vínculo) + tb_municip (nome do município)
    + tb_regsaud (nome da região).
    """
    with zipfile.ZipFile(ZIP_LOCAL) as z:
        rel = _ler_csv_do_zip(z, "rl_municip_regsaud.csv")
        municip = _ler_csv_do_zip(z, "tb_municip.csv")
        regsaud = _ler_csv_do_zip(z, "tb_regsaud.csv")

    # Só municípios da PB: código IBGE começa com 25 (código da UF).
    pb = rel[rel["CO_MUNICIP"].str.startswith("25")].copy()

    # Nome do município (tb_municip traz também extintos/ignorados; o join
    # é por código, então cada linha da relação acha exatamente seu nome).
    pb = pb.merge(
        municip[["CO_MUNICIP", "DS_NOME"]].rename(columns={"DS_NOME": "nome_municipio"}),
        on="CO_MUNICIP",
        how="left",
    )

    # Nome da região de saúde (chave em tb_regsaud chama REGSAUD).
    pb = pb.merge(
        regsaud[["REGSAUD", "DS_NOME"]].rename(
            columns={"REGSAUD": "CO_REGSAUD", "DS_NOME": "nome_regiao_saude"}
        ),
        on="CO_REGSAUD",
        how="left",
    )

    pb = pb.rename(
        columns={"CO_MUNICIP": "codigo_municipio", "CO_REGSAUD": "codigo_regiao_saude"}
    )
    return pb[
        ["codigo_municipio", "nome_municipio", "codigo_regiao_saude", "nome_regiao_saude"]
    ].sort_values("codigo_municipio").reset_index(drop=True)


def validar(pb: pd.DataFrame) -> None:
    """Valida os fatos conhecidos: 223 municípios, 1 região cada, 16 regiões."""
    erros: list[str] = []
    if len(pb) != N_MUNICIPIOS_PB:
        erros.append(f"esperava {N_MUNICIPIOS_PB} municípios, veio {len(pb)}")
    duplicados = pb["codigo_municipio"].duplicated().sum()
    if duplicados:
        erros.append(f"{duplicados} municípios em mais de uma região")
    n_regioes = pb["codigo_regiao_saude"].nunique()
    if n_regioes != N_REGIOES_PB:
        erros.append(f"esperava {N_REGIOES_PB} regiões de saúde, veio {n_regioes}")
    if pb["nome_municipio"].isna().any() or pb["nome_regiao_saude"].isna().any():
        erros.append("nome de município ou de região ficou sem preencher no join")
    if erros:
        raise ValueError("validação FALHOU: " + "; ".join(erros))
    print(
        f"validação OK: {len(pb)} municípios da PB, cada um em exatamente "
        f"1 das {n_regioes} regiões de saúde"
    )


if __name__ == "__main__":
    baixar_zip()
    tabela = montar_tabela_pb()
    validar(tabela)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    # CSV pequeno e versionável: o Pedro clona o repo e já tem a tabela pronta.
    tabela.to_csv(TABELA_FINAL, index=False, encoding="utf-8")
    print(f"salvo: {TABELA_FINAL} ({len(tabela)} linhas)")
