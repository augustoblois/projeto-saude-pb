# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (22/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito, revisado e aprovado** — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação. Os documentos vivem na pasta `docs/` (você não precisa ler; sua referência é este arquivo).
- **Decisões já fechadas e registradas:** painel em **Streamlit** (ferramenta de Python que transforma análise em site interativo); os **paraibanos internados em outros estados** (PE/RN/CE) entram na análise; e o **índice de dependência** — o número principal do projeto — é a porcentagem dos moradores de cada região que precisou internar FORA da própria região.
- **A análise começou:** já existe um arquivo único com as 258 mil internações de 2025 e os nomes das cidades legíveis (detalhes na seção abaixo).
- **Prazo:** apresentação dia 07/08/2026 (16 dias).

## O que aconteceu na última sessão (22/07/2026 — segunda sessão do dia)

- **O plano do projeto passou por uma revisão completa e foi aprovado.** Conferimos que tudo se encaixa: a intenção do projeto, o plano detalhado e a lista de tarefas contam a mesma história, sem buraco nem contradição. O resultado dessa conferência está em `docs/qa-report.md` (não precisa ler — resumo: aprovado, com 3 pontos de atenção que já foram tratados).
- **Colocamos duas "regras de segurança" no plano** pra não estourar o prazo:
  1. Se o download dos dados de Pernambuco/RN/Ceará (pros paraibanos que internaram fora) não estiver completo até **29/07**, essa parte vira só uma nota explicativa no relatório — o resto do projeto não depende dela e segue normal.
  2. Já existia uma regra parecida pro mapa interativo: se ele não funcionar em 1 dia de trabalho, trocamos por um mapa mais simples.
- **Começou a análise de verdade — primeira tarefa técnica concluída.** Os 12 arquivos mensais (um por mês de 2025) foram juntados num arquivo único, e os códigos numéricos de cidade viraram nomes legíveis: onde antes se lia "250750", agora se lê "João Pessoa". Pra isso, baixamos a tabela oficial do IBGE com todos os 5.571 municípios do Brasil (ela já está no projeto — `data/raw/municipios_ibge.csv`).
- **Tudo foi conferido duas vezes:** as 258.125 internações do ano estão no arquivo final, nenhuma linha se perdeu na junção, e 100% dos códigos de cidade ganharam nome (zero códigos sem correspondência). O arquivo pronto está em `data/processed/sih_pb_2025_tratado.parquet` ("parquet" é um formato de arquivo que guarda os dados prontos pra análise).
- **Curiosidade que já apareceu:** entre os internados na PB em 2025, cerca de 1.500 moram em outros estados — 760 só de Pernambuco. O caminho inverso (paraibanos internados fora) é o que vamos buscar nos próximos dias.

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
5. **Terminou?** GitHub Desktop → **Commit** (dar um nome pro que você fez) → **Push** (enviar pro GitHub, pro Augusto ver).

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
