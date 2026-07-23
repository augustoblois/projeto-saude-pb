# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (23/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito, revisado e aprovado** — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação. Os documentos vivem na pasta `docs/` (você não precisa ler; sua referência é este arquivo).
- **Decisões já fechadas e registradas:** painel em **Streamlit** (ferramenta de Python que transforma análise em site interativo); os **paraibanos internados em outros estados** (PE/RN/CE) entram na análise; e o **índice de dependência** — o número principal do projeto — é a porcentagem dos moradores de cada região que precisou internar FORA da própria região.
- **A análise começou:** já existe um arquivo único com as 258 mil internações de 2025 e os nomes das cidades legíveis, e agora também um **dicionário de dados** — um documento que explica o que cada coluna da base significa e quais são confiáveis pra usar (detalhes na seção abaixo).
- **Prazo:** apresentação dia 07/08/2026 (15 dias).

## O que aconteceu na última sessão (23/07/2026)

- **Fizemos o "dicionário de dados" da base.** A base de internações tem 118 colunas com nomes em código (tipo `CAR_INT`, `ESPEC`...), e antes de usar qualquer uma numa análise precisávamos saber: o que ela significa oficialmente, e o que ela contém DE VERDADE nos nossos dados. Conferimos as 118, uma a uma: significado, valores que aparecem, e quantos registros vêm vazios.
- **Resultado: ~46 colunas aprovadas pra uso e ~72 descartadas.** As descartadas quase todas vêm vazias ou com valor repetido em tudo (são campos do formulário nacional que não se aplicam ao nosso caso — não é defeito dos nossos dados). Tudo documentado em `docs/dicionario-dados.md`, com veredito e justificativa coluna por coluna.
- **Conferimos contra os documentos oficiais do Ministério da Saúde** — baixamos o manual técnico (está em `docs/IT_SIHSUS_1603.pdf`) e a tabela oficial de códigos. A conferência valeu: 3 códigos estavam descritos errado no nosso rascunho e foram corrigidos.
- **Descobertas boas pra nossa análise final:** 75% das internações são de urgência (só 25% agendadas), e temos colunas confiáveis de diagnóstico, idade, uso de UTI, valor pago e óbito — dá pra caracterizar bem "quem viaja pra internar e por quê".
- **Criamos o `docs/diario-do-projeto.md`** — uma linha do tempo do projeto, etapa por etapa, que vai virar o roteiro da apresentação. Vale a leitura: é um resumo de tudo que foi feito até agora.

## Pra você, Pedro

1. **Preparar o projeto (uma vez só, se ainda não fez):** abrir o terminal na pasta do projeto e rodar: `pip install -r requirements.txt` — isso instala tudo que o projeto usa.
2. **Novidade boa: agora existe um arquivo único, já com nomes de cidade.** Você não precisa mais juntar os 12 meses na mão — esse trabalho está feito. Rodar `jupyter notebook` no terminal e, num notebook novo:
   ```python
   import pandas as pd
   df = pd.read_parquet("data/processed/sih_pb_2025_tratado.parquet")
   ```
   Cada linha é uma internação. As colunas mais úteis pra você agora têm nome legível: `nome_mun_res` (cidade onde o paciente **mora**), `nome_mun_mov` (cidade onde ele **internou**), e `uf_res` (estado onde mora). Quando mora numa cidade e internou em outra, o paciente viajou — é isso que o projeto investiga.
3. **Se quiser entender como esse arquivo foi montado:** abrir `notebooks/01-tratamento-base.ipynb` — ele foi escrito com explicações em português a cada passo, dá pra ler como um texto.
4. **Explorar e anotar:** salvar seu notebook na pasta `notebooks/` com nome começando em `90-` (ex: `90-eda-pedro.ipynb`). Perguntas boas pra começar: quais cidades mais "mandam" pacientes pra fora? Pra onde eles vão? O movimento muda ao longo do ano? (Agora dá pra responder usando nomes, sem decorar código de cidade.)
   - **Novidade desta sessão que ajuda você:** se quiser usar outras colunas da base (idade, diagnóstico, valor...), consulte antes o `docs/dicionario-dados.md` — ele diz o que cada coluna significa e se ela é confiável. E o `docs/diario-do-projeto.md` conta a história do projeto até aqui, em poucas páginas.
5. **Terminou?** GitHub Desktop → **Commit** (dar um nome pro que você fez) → **Push** (enviar pro GitHub, pro Augusto ver).

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
