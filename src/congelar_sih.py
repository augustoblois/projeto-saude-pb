# Congela SIH-PB jan-dez/2025 em parquet local (data/raw/).
# Fluxo validado no smoke test (jan/2025): FTP direto -> .dbc -> .dbf -> parquet.
# Idempotente: mês com parquet existente é pulado; rodar de novo só completa o que falta.
import asyncio
from pathlib import Path

from pysus.api.ftp.client import FTP
from pysus.api.ftp.databases import SIH
from pyreaddbc import dbc2dbf
from pysus.data.dbf_reader import read_dbf_fast

OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

ANO = 2025
MESES = range(1, 13)


async def baixar_faltantes() -> dict[int, Path]:
    """Baixa os .dbc dos meses sem parquet. Uma conexão FTP pra tudo."""
    faltantes = [m for m in MESES if not (OUT / f"sih_pb_{ANO}_{m:02d}.parquet").exists()]
    if not faltantes:
        return {}
    client = FTP()
    await client.connect()
    baixados: dict[int, Path] = {}
    try:
        sih = SIH(client=client)
        contents = await sih.content
        por_nome = {str(f): f for f in contents}
        for mes in faltantes:
            alvo = f"RDPB{ANO % 100:02d}{mes:02d}.dbc"
            if alvo not in por_nome:
                print(f"[{mes:02d}] AUSENTE no FTP: {alvo}")
                continue
            local = OUT / alvo
            if not local.exists():
                print(f"[{mes:02d}] baixando {alvo}...")
                local = Path(await client.download(por_nome[alvo], local))
            baixados[mes] = local
    finally:
        await client.close()
    return baixados


def converter(mes: int, dbc_path: Path) -> str:
    """DBC -> DBF -> DataFrame -> parquet. Valida colunas O-D."""
    dbf_path = dbc_path.with_suffix(".dbf")
    if not dbf_path.exists():
        dbc2dbf(str(dbc_path), str(dbf_path))
    df = read_dbf_fast(dbf_path)
    for col in ("MUNIC_RES", "MUNIC_MOV"):
        if col not in df.columns:
            return f"ERRO: coluna {col} ausente"
        if df[col].isna().any():
            return f"ERRO: nulos em {col} ({int(df[col].isna().sum())})"
    destino = OUT / f"sih_pb_{ANO}_{mes:02d}.parquet"
    df.to_parquet(destino)
    return f"OK — {df.shape[0]} internações -> {destino.name}"


if __name__ == "__main__":
    baixados = asyncio.run(baixar_faltantes())
    placar: dict[int, str] = {}
    for mes, dbc in baixados.items():
        try:
            placar[mes] = converter(mes, dbc)
        except Exception as e:  # falha de um mês não derruba os outros
            placar[mes] = f"ERRO: {e}"
    print("\n=== Placar do congelamento ===")
    for mes in MESES:
        parquet = OUT / f"sih_pb_{ANO}_{mes:02d}.parquet"
        status = placar.get(mes, "já congelado" if parquet.exists() else "não processado")
        print(f"{ANO}-{mes:02d}: {status}")
