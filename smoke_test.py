# Smoke test PySUS 2.7.0 — valida a via de acesso ao SIH antes de investir no projeto.
# Sucesso = 1 mês de SIH-PB vira DataFrame com MUNIC_RES e MUNIC_MOV, salvo em parquet.
#
# Nota: a API de conveniência (pysus.sih) usa um mirror que não tem o grupo RD,
# e o search() do FTP tem bug de filtro — por isso filtramos o nome na mão.
import asyncio
from pathlib import Path

import pandas as pd
from pysus.api.ftp.client import FTP
from pysus.api.ftp.databases import SIH

OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

ALVO = "RDPB2501.dbc"  # RD = AIH Reduzida (residência E internação no mesmo registro)


async def main() -> Path:
    client = FTP()
    await client.connect()
    try:
        sih = SIH(client=client)
        contents = await sih.content
        file = next(f for f in contents if str(f) == ALVO)
        print("Encontrado no FTP:", file)
        local = await client.download(file, OUT / ALVO)
        print("Baixado em:", local)
        return Path(local)
    finally:
        await client.close()


dbc_path = asyncio.run(main())

# DBC → DBF (descompressão) → DataFrame
from pyreaddbc import dbc2dbf  # noqa: E402
from pysus.data.dbf_reader import read_dbf_fast  # noqa: E402

dbf_path = dbc_path.with_suffix(".dbf")
dbc2dbf(str(dbc_path), str(dbf_path))
df = read_dbf_fast(dbf_path)
print("Shape:", df.shape)
cols_od = [c for c in df.columns if c in ("MUNIC_RES", "MUNIC_MOV")]
print("Colunas O-D presentes:", cols_od)
print(df[cols_od].head(10))
print("Nulos em O-D:", df[cols_od].isna().sum().to_dict())

df.to_parquet(OUT / "sih_pb_2025_01.parquet")
print("OK — parquet salvo em", OUT / "sih_pb_2025_01.parquet")
