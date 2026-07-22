# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (22/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **A ideia funciona:** hoje conseguimos baixar os dados de internações de janeiro/2025 direto do sistema do Ministério da Saúde (DATASUS). São 20.029 internações na PB só nesse mês, sem nenhum dado faltando nas colunas que importam. E o achado principal já apareceu: **quase metade dos pacientes (47,8%) internou fora da cidade onde mora**. Ou seja, o problema que queremos mostrar existe e é grande.
- **Prazo:** apresentação dia 07/08/2026 (16 dias).

## O que aconteceu na última sessão (22/07/2026)

- Testamos e confirmamos que conseguimos baixar os dados do governo sem depender de ninguém (o script `smoke_test.py` faz isso — "smoke test" é só o nome que se dá a um teste rápido pra ver se algo funciona antes de investir tempo).
- Criamos este projeto no GitHub, já organizado nas pastas que a disciplina exige.
- Os dados de janeiro/2025 já estão salvos dentro do projeto, no arquivo `data/raw/sih_pb_2025_01.parquet` — **você não precisa baixar nada do governo, quando você clonar o projeto os dados já vêm junto**.

## Pra você, Pedro

1. **Preparar o computador (uma vez só):** instalar o Python (versão 3.11 ou mais nova, em python.org). Depois, abrir o terminal na pasta do projeto e rodar: `pip install -r requirements.txt` — isso instala tudo que o projeto usa.
2. **Abrir os dados:** rodar `jupyter notebook` no terminal (abre no navegador uma ferramenta pra mexer nos dados). Num notebook novo, carregar os dados assim:
   ```python
   import pandas as pd
   df = pd.read_parquet("data/raw/sih_pb_2025_01.parquet")
   ```
   Cada linha é uma internação. As duas colunas mais importantes: `MUNIC_RES` (código da cidade onde o paciente **mora**) e `MUNIC_MOV` (código da cidade onde ele **internou**). Quando as duas são diferentes, o paciente viajou pra internar — é isso que o projeto investiga.
3. **Explorar e anotar:** salvar seu notebook na pasta `notebooks/` com nome começando em `90-` (ex: `90-eda-pedro.ipynb`). Perguntas boas pra começar: quais tipos de internação mais aparecem? Quais cidades mais "mandam" pacientes pra fora?
4. **Terminou?** GitHub Desktop → **Commit** (dar um nome pro que você fez) → **Push** (enviar pro GitHub, pro Augusto ver).

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
