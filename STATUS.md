# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (23/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito, revisado e aprovado** — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação. Os documentos vivem na pasta `docs/` (você não precisa ler; sua referência é este arquivo).
- **Decisões já fechadas e registradas:** painel em **Streamlit** (ferramenta de Python que transforma análise em site interativo); os **paraibanos internados em outros estados** (PE/RN/CE) entram na análise; e o **índice de dependência** — o número principal do projeto — é a porcentagem dos moradores de cada região que precisou internar FORA da própria região.
- **A análise avançou mais um degrau:** além do arquivo único com as 258 mil internações e do dicionário de dados (que diz quais colunas são confiáveis), agora **cada internação sabe a qual "região de saúde" pertence** — tanto a região onde o paciente mora quanto a região do hospital. Região de saúde é a divisão oficial que o governo usa pra organizar o SUS: a Paraíba tem 16 delas, cada uma agrupando municípios vizinhos. É a unidade que o nosso produto final vai usar.
- **Prazo:** apresentação dia 07/08/2026 (15 dias).

## O que aconteceu na última sessão (23/07/2026 — segunda sessão do dia)

- **Colocamos a "região de saúde" em cada uma das 258 mil internações.** Por quê: o resultado final do projeto (o mapa de quem depende de quem) é por região de saúde, não por cidade — é assim que a Secretaria de Saúde planeja. Sem esse passo, nenhuma análise regional existiria.
- **De onde veio a informação:** baixamos a tabela oficial do próprio Ministério da Saúde (DATASUS) que diz a qual região cada município pertence — a mesma tabela que os sistemas oficiais do governo usam. Fonte, endereço e data do download ficaram documentados, pra citar na apresentação.
- **Conferências (todas passaram):** os 223 municípios da Paraíba receberam região, cada um em exatamente 1 das 16 regiões; nenhuma internação se perdeu no processo (entraram 258.125, saíram 258.125); e nenhuma linha ficou sem região. Pacientes que moram em outros estados (1.502 internações — a maioria de Pernambuco e Rio Grande do Norte) foram marcados como "Fora da PB".
- **Primeiro retrato regional:** a região de João Pessoa concentra 41% das internações e a de Campina Grande 26% — juntas, dois terços do estado. É exatamente o padrão de "polos que atraem pacientes" que o projeto quer medir.
- **Revisão independente:** todo esse trabalho foi conferido por uma segunda checagem, que refez as contas do zero e bateu os mesmos números antes de darmos a etapa por concluída.

## Pra você, Pedro

1. **Preparar o projeto (uma vez só, se ainda não fez):** abrir o terminal na pasta do projeto e rodar: `pip install -r requirements.txt` — isso instala tudo que o projeto usa.
2. **Novidade: use o arquivo mais novo, que já vem com a região de saúde.** Rodar `jupyter notebook` no terminal e, num notebook novo:
   ```python
   import pandas as pd
   df = pd.read_parquet("data/processed/sih_pb_2025_regioes.parquet")
   ```
   Cada linha é uma internação. As colunas mais úteis pra você: `nome_mun_res` (cidade onde o paciente **mora**), `nome_mun_mov` (cidade onde ele **internou**), `regiao_res` (região de saúde onde mora — ou "Fora da PB" se mora em outro estado) e `regiao_int` (região do hospital). Quando mora num lugar e internou em outro, o paciente viajou — é isso que o projeto investiga, agora também no nível de região.
3. **Se quiser entender como esse arquivo foi montado:** abrir `notebooks/01-tratamento-base.ipynb` — ele foi escrito com explicações em português a cada passo, dá pra ler como um texto.
4. **Explorar e anotar:** salvar seu notebook na pasta `notebooks/` com nome começando em `90-` (ex: `90-eda-pedro.ipynb`). Perguntas boas pra começar: quais cidades mais "mandam" pacientes pra fora? Pra onde eles vão? E no nível de região: quais das 16 regiões mais "perdem" moradores pra hospitais de fora? (Dica: comparar `regiao_res` com `regiao_int` — quando são diferentes, o paciente saiu da própria região.)
   - Se quiser usar outras colunas da base (idade, diagnóstico, valor...), consulte antes o `docs/dicionario-dados.md` — ele diz o que cada coluna significa e se ela é confiável. E o `docs/diario-do-projeto.md` conta a história do projeto até aqui, em poucas páginas.
   - Se quiser ver como a região de saúde foi colocada na base, o `notebooks/01-regiao-saude.ipynb` explica passo a passo, dá pra ler como um texto.
5. **Terminou?** GitHub Desktop → **Commit** (dar um nome pro que você fez) → **Push** (enviar pro GitHub, pro Augusto ver).

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
