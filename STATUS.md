# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (25/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito, revisado e aprovado** — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação. Os documentos vivem na pasta `docs/` (você não precisa ler; sua referência é este arquivo).
- **Decisões já fechadas e registradas:** painel em **Streamlit** (ferramenta de Python que transforma análise em site interativo); os **paraibanos internados em outros estados** (PE/RN/CE) entram na análise; e o **índice de dependência** — o número principal do projeto — é a porcentagem dos moradores de cada região que precisou internar FORA da própria região.
- **A análise central do projeto está pronta:** cada internação sabe a qual "região de saúde" pertence (a divisão oficial do SUS — a PB tem 16), e já existe a **matriz origem→destino** — a tabela que diz, de cada cidade e de cada região, quantos pacientes foram internar em cada outra, mês a mês. É o coração do projeto: tudo daqui pra frente (análises, índice, painel) consome essa matriz.
- **O número principal do projeto mudou de 47,8% pra 49,8%** (internações de jan/2025 fora do município de residência). O 47,8% veio da fase de pesquisa e não tinha memória de cálculo; ao refazer a conta com a base congelada — de cinco jeitos diferentes — o resultado é 49,8%, sempre. Adotamos o número que conseguimos provar. No ano fechado: **50,5% das internações são fora do município onde o paciente mora**.
- **Também já sabemos quantos paraibanos internaram FORA do estado em 2025: 3.682** (a maioria em Pernambuco e no Rio Grande do Norte). Baixamos os dados dos 3 estados vizinhos e filtramos só quem mora na PB. É pouco perto das 258 mil internações internas — sinal de que o problema de "viajar pra internar" acontece quase todo DENTRO do estado.
- **As cinco análises principais do projeto estão prontas e conferidas.** Em uma linha cada: os pacientes que saem da própria cidade se concentram em **João Pessoa e Campina Grande (58,6% do movimento)**; **cidade pequena perde muito mais** (até 10 mil habitantes, 98% dos moradores internam fora; acima de 100 mil, só 9%); os **caminhos não mudam** ao longo do ano (13 dos 20 trajetos mais usados aparecem nos 12 meses); quem **sai do estado** são 3.682 pessoas (1,41%), por dois motivos que convivem — estar na divisa e buscar tratamento grave — sem que dê pra dizer quanto é de cada; e **8 das 16 regiões de saúde passam de 50%** de dependência.
- **Toda a parte de análise do projeto está concluída.** Do dia 25/07 em diante não há mais conta a fazer: o que falta é montar o painel (o site interativo) e escrever o texto de recomendações para a apresentação.
- **Prazo:** apresentação dia 07/08/2026 (13 dias).

## O que aconteceu na última sessão (25/07/2026)

Sessão curta e de acabamento: fechamos a **explicação escrita do índice de dependência** — o texto que vai aparecer dentro do painel para o visitante entender o número principal do projeto sem precisar de ninguém do lado. Com isso, **acabou toda a parte de análise**; daqui pra frente é painel e apresentação.

**1. O texto da explicação ficou pronto.**
Ele tem a fórmula, um exemplo real destrinchado passo a passo (a 3ª Região, a mais dependente do estado: de cada 100 internações de moradores dela, cerca de 85 acontecem fora), a leitura em linguagem do dia a dia, as faixas do que é dependência baixa/média/alta, e as seis limitações do número — o que ele **não** consegue dizer. Está em `docs/definicao-indice-dependencia.md`.

**2. Conferimos os 12 números que aparecem nesse texto, um por um.**
Refizemos cada conta a partir da base de internações original, sem olhar as tabelas já prontas — de propósito, para que fossem dois caminhos independentes chegando ao mesmo lugar. Os 12 bateram exatamente. A regra do projeto é que nenhum número apareça em lugar nenhum sem ser possível refazer a conta que o gerou, e agora isso está verificado para o texto que o professor vai ler no painel.

**3. Corrigimos uma informação que tinha envelhecido.**
O texto avisava que a base só enxerga hospitais da Paraíba, e dizia que os paraibanos internados em outros estados eram "cerca de 3,7 mil, ainda não confirmado". Só que esse levantamento **já tinha sido concluído** na sessão anterior: são **3.682 internações, 1,41%** do total. Ou seja: era um número certo, mas com um aviso desatualizado grudado nele. É exatamente o tipo de detalhe que alguém da banca percebe — o texto dizendo "ainda não sabemos" ao lado da tabela que mostra o resultado. Agora está atualizado, e ganhou também a ressalva honesta de que **não dá pra cravar** quanto desses 3.682 é gente da divisa e quanto é gente buscando tratamento grave: essa divisão muda demais dependendo do critério de distância que se use, então preferimos não afirmar o que o dado não sustenta.

*(O detalhe das cinco análises da sessão anterior saiu daqui para esta seção não crescer sem parar — está resumido em "Onde estamos", acima, e contado por inteiro em `docs/diario-do-projeto.md`.)*

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
   - Se quiser ver como a região de saúde foi colocada na base, o `notebooks/01-regiao-saude.ipynb` explica passo a passo, dá pra ler como um texto. E o `notebooks/01-matriz-od.ipynb` mostra como a matriz origem→destino foi montada — inclusive a investigação do número que mudou (47,8% → 49,8%).
   - **Atalho bom pra você:** duas tabelas já prontas em `data/processed/` abrem direto no Excel: `matriz_od_regional_mensal.csv` (fluxos entre as 16 regiões, mês a mês) e `taxas_evasao_regional.csv` (a % de moradores de cada região que interna fora dela). Dá pra explorar sem escrever código.
5. **Terminou?** GitHub Desktop → **Commit** (dar um nome pro que você fez) → **Push** (enviar pro GitHub, pro Augusto ver).

### Mudança: aquela tarefa de leitura deixou de ser obrigatória

Se você leu este arquivo nos últimos dias, viu aqui uma tarefa marcada como **travando o projeto**: ler a explicação do índice de dependência e responder 7 perguntas do Augusto, sem se preparar. **Ela não trava mais nada** — o Augusto decidiu no dia 25/07 tirar isso do caminho, e o projeto seguiu em frente.

O motivo é o oposto de "deixa pra lá": ele leu o texto inteiro e concluiu que estava claro o bastante. O raciocínio dele foi que você é leigo na **ferramenta** (GitHub, Python, os termos técnicos), não no **conteúdo** — e o que aquele teste mediria é se o texto se explica sozinho para quem raciocina bem, coisa que ele já considera respondida. Então não é uma pendência sua, e não tem nada esperando por você aí.

**Se ainda assim você quiser fazer (15 minutos, e continua valendo a pena):** abra `docs/definicao-indice-dependencia.md`, leia **só até a seção 5**, uma vez só, e chame o Augusto antes de ler o resto — o final do arquivo tem as próprias perguntas, e uma delas entrega a resposta. Qualquer trecho em que você travar é trecho pra reescrever antes de 07/08, porque quem estiver assistindo a apresentação vai estar exatamente na sua posição: vendo o número pela primeira vez.

### O que de fato importa pra você agora: você é quem apresenta

Isso é o ponto mais importante deste arquivo. **A apresentação do dia 07/08 é sua** — e ela não é só ler slide: pode vir pergunta do professor. Faltam **13 dias**, e toda a parte de análise está pronta, o que quer dizer que **os números que você vai defender já existem, e dá pra começar a se familiarizar com eles agora**, sem esperar o painel ficar pronto.

O caminho mais curto pra isso, em ordem:
1. **`docs/diario-do-projeto.md`** — conta a história do projeto inteiro, etapa por etapa, em poucas páginas. É a leitura que mais rende por minuto gasto.
2. **As duas tabelas que abrem no Excel** (`data/processed/indice_dependencia_regional.csv` e `outputs/tables/pa3_saldo_municipios.csv`) — olhar os números com os próprios olhos gruda muito mais do que ler sobre eles.
3. **Os gráficos em `outputs/figures/`** — são as imagens que provavelmente vão pro slide. Vale saber de cor o que cada um mostra.

Se em algum ponto você pensar "não sei explicar esse número se me perguntarem", **fala pro Augusto** — é exatamente esse tipo de aviso que ainda dá tempo de resolver com 13 dias, e não dá com 1.

### Novas tabelas prontas pra abrir no Excel

Ficaram na pasta `outputs/tables/` (nomes começando com `pa1_`, `pa3_`, `pa4_`, `pa5_`) e em `data/processed/indice_dependencia_regional.csv`. Todas abrem direto no Excel, sem precisar escrever código. As mais interessantes pra dar uma olhada:
- `pa3_saldo_municipios.csv` — mostra, por cidade, quantos pacientes ela **recebe** de fora menos quantos ela **manda** pra fora. Número positivo = a cidade atrai pacientes; negativo = perde.
- `indice_dependencia_regional.csv` — o índice das 16 regiões, do mais dependente ao mais autossuficiente.

Os gráficos que geramos estão em `outputs/figures/` (arquivos de imagem, é só abrir).

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
