# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (27/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito, revisado e aprovado** — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação. Os documentos vivem na pasta `docs/` (você não precisa ler; sua referência é este arquivo).
- **Decisões já fechadas e registradas:** painel em **Streamlit** (ferramenta de Python que transforma análise em site interativo); os **paraibanos internados em outros estados** (PE/RN/CE) entram na análise; e o **índice de dependência** — o número principal do projeto — é a porcentagem dos moradores de cada região que precisou internar FORA da própria região.
- **A análise central do projeto está pronta:** cada internação sabe a qual "região de saúde" pertence (a divisão oficial do SUS — a PB tem 16), e já existe a **matriz origem→destino** — a tabela que diz, de cada cidade e de cada região, quantos pacientes foram internar em cada outra, mês a mês. É o coração do projeto: tudo daqui pra frente (análises, índice, painel) consome essa matriz.
- **O número principal do projeto mudou de 47,8% pra 49,8%** (internações de jan/2025 fora do município de residência). O 47,8% veio da fase de pesquisa e não tinha memória de cálculo; ao refazer a conta com a base congelada — de cinco jeitos diferentes — o resultado é 49,8%, sempre. Adotamos o número que conseguimos provar. No ano fechado: **50,5% das internações são fora do município onde o paciente mora**.
- **Também já sabemos quantos paraibanos internaram FORA do estado em 2025: 3.682** (a maioria em Pernambuco e no Rio Grande do Norte). Baixamos os dados dos 3 estados vizinhos e filtramos só quem mora na PB. É pouco perto das 258 mil internações internas — sinal de que o problema de "viajar pra internar" acontece quase todo DENTRO do estado.
- **As cinco análises principais do projeto estão prontas e conferidas.** Em uma linha cada: os pacientes que saem da própria cidade se concentram em **João Pessoa e Campina Grande (58,6% do movimento)**; **cidade pequena perde muito mais** (até 10 mil habitantes, 98% dos moradores internam fora; acima de 100 mil, só 9%); os **caminhos não mudam** ao longo do ano (13 dos 20 trajetos mais usados aparecem nos 12 meses); quem **sai do estado** são 3.682 pessoas (1,41%), por dois motivos que convivem — estar na divisa e buscar tratamento grave — sem que dê pra dizer quanto é de cada; e **8 das 16 regiões de saúde passam de 50%** de dependência.
- **Toda a parte de análise do projeto está concluída.** Do dia 25/07 em diante não há mais conta a fazer: o que falta é montar o painel (o site interativo) e escrever o texto de recomendações para a apresentação.
- **O painel saiu do papel e já roda na máquina.** Ele tem quatro abas previstas; **três já funcionam**: a tabela de quem vai de onde pra onde, o **mapa da Paraíba** e o **ranking do índice de dependência**. Só a última (os achados e recomendações) ainda está vazia — e ela depende do texto que a gente ainda vai escrever.
- **O mapa mostra uma coisa que ninguém tinha desenhado ainda:** cada cidade da Paraíba está pintada com a cor da cidade para onde a maioria dos seus moradores acaba internada. O resultado é um mapa de "territórios": dá pra ver no olho o **território de Campina Grande (62 cidades), o de João Pessoa (48) e o de Patos (30)**.
- **Prazo:** apresentação dia 07/08/2026 (13 dias).

## O que aconteceu na última sessão (27/07/2026)

**Foram entregues as duas últimas abas do painel — o projeto está completo.** E junto com elas, toda a estrutura de números, rastreamento e texto que sustenta a apresentação do dia 07/08.

### US-14 — A aba "Achados & recomendações"

**A quarta aba do painel agora existe e está funcional.** Ela é a vitrine do projeto para quem vai assistir à apresentação — mostra os pontos principais com números e recomendações amarrados um ao outro.

**1. O painel começa com 4 números em destaque no topo:**
- 258.125 internações de paraibanos em 2025
- 50,5% delas fora do município onde cada paciente mora
- 58,6% dos fluxos concentrados em João Pessoa e Campina Grande
- 8 das 16 regiões de saúde com dependência acima de 50%

Nenhum desses números foi digitado à mão — todos vêm de cálculos feitos diretamente da base de dados. Se um dia os dados forem atualizados, esses números acompanham sozinhos.

**2. A estrutura é 5 achados + 4 recomendações, cada um com um número amarrado.**
Exemplo: Achado 2 diz que a concentração é tanta (58,6% em dois polos) e foi por tanto tempo (13 dos 20 maiores fluxos aparecem todos os 12 meses) — aí vem o número a sustentar, a recomendação ("essas regiões precisam de acordo"), e depois a próxima descoberta.

**3. Um achado forte apareceu só na conferência final:**
Em 7 das 8 regiões que mais dependem de fora, a maioria das saídas não é espalhada entre vizinhos — vai tudo para um destino só. A 14ª Região: 92,3% para João Pessoa. A 15ª: 89,6% para Campina Grande. A 3ª: 83,6% também para Campina Grande. Isso muda a recomendação: não é "essas regiões precisam de acordo (genérico)", é **"essas regiões precisam de acordo com este parceiro, nominalmente"** — porque o parceiro é só um.

**4. O texto lê o arquivo `.md` em tempo real.**
Assim como acontece na aba do índice (etapa anterior), a aba não tem uma cópia interna do texto — ela **lê o arquivo de texto original** toda vez que abre. Se uma frase errar na revisão final, a gente corrige no arquivo e o painel corrige junto. Nunca vão existir duas versões divergentes da mesma frase.

### US-16 — Narrativa executiva + rastreamento de números

**Ficaram prontos os três documentos que sustentam a aba e a apresentação inteira:**

**1. Narrativa executiva (`reports/narrativa-executiva.md`):**
É o texto que vai em slides ou relatório. Tem o achado central em uma frase, depois os 5 achados, depois as 4 recomendações, um fecho que explica por que isso importa, e as 4 limitações do estudo (coisas que o número não consegue dizer). Nada foi digitado de cabeça — tudo vem conferido da base. **É o arquivo que Pedro deve ler quando tiver tempo** — é o material de estudo mais direto que existe do projeto.

**2. Sumário de evidências (`reports/sumario-evidencias.md`):**
Uma tabela que diz, para **cada número** que aparece no projeto, de onde ele saiu. Tem um código (E-01, P1-03, P3-02...) e o arquivo ou notebook que o calcula. Serve para responder a "de onde saiu esse número?" — a resposta é uma linha apontando para um lugar específico. Pensada pro momento que alguém na apresentação perguntar.

**3. Script de conferência (`src/conferir_narrativa.py`):**
Roda `python src/conferir_narrativa.py` no terminal e recalcula da base os 3 blocos de números que não tinham notebook próprio (quantas internações foram de residentes da PB contados só quem mora lá mesmo, a taxa estadual de evasão, e a tabela de destinos das 8 regiões mais dependentes). Serve como "teste de integridade" — se o script rodar e os números baterem, o projeto está coeso.

### Duas armadilhas que foram registradas

**1. O 50,5% e o 50,2% são ambos certos, mas medem coisas diferentes.**
- **50,5%:** todas as 258.125 internações que aconteceram na PB — inclui quem vinha de fora pra cá
- **50,2%:** só as internações de residentes da PB — exclui os não-paraibanos

O texto do projeto diz qual está usando em cada contexto. Se confundir, a conclusão pode estar certa e o denominador errado — é o tipo de pegadilha que professor tira.

**2. O 26,4% é a taxa estadual, não a média das regiões.**
Se você somar os 26,4% de cada região e dividir por 16, sai outro número (porque região grande e pequena pesam igual na média simples, enquanto a taxa estadual pesa pelo volume). O texto agora diz "taxa estadual" pra deixar claro qual das duas está sendo usada.

### O que falta conferir

**A aba "Achados & recomendações" foi pronta, mas ninguém olhou a tela ainda** — o Augusto vai testar se está quebrado visualmente. Se aparecer algo fora de lugar, será corrigido. Mas a estrutura e os números já estão validados.

*(O detalhe das etapas anteriores está resumido em "Onde estamos", acima, e contado por inteiro em `docs/diario-do-projeto.md`.)*

## Pra você, Pedro

### ⏳ Tem uma coisa esperando por você — e ela leva 1 minuto

O mapa está pronto, mas **ele só conta como entregue depois que você olhar**. O combinado do projeto é que um mapa que precisa de explicação não serve, porque no dia 07/08 quem estiver assistindo vai vê-lo pela primeira vez, exatamente como você agora. Então o teste é você mesmo:

1. Abrir o terminal na pasta do projeto e rodar:
   ```
   streamlit run app.py
   ```
2. Vai abrir uma página no navegador. Clicar na aba **Mapa**, no alto.
3. **Olhar por 1 minuto, sem ler nada em volta e sem me perguntar nada.** Depois me dizer, com suas palavras: **quais são as cidades que puxam pacientes de toda a Paraíba?**

Se as duas cidades principais saltarem aos olhos sozinhas, o mapa passou. Se você precisar procurar, ou ficar na dúvida, **o mapa é que está errado, não você** — e aí eu conserto antes da apresentação. Me responde por WhatsApp mesmo.

### Leitura importante: a narrativa do projeto está pronta

Quando tiver tempo — pode ser hoje ou amanhã — abra este arquivo e leia:
```
reports/narrativa-executiva.md
```

É o texto da aba "Achados & recomendações" do painel (a aba nova). Tem o achado central, os 5 achados principais com números, as 4 recomendações, e as limitações. **É a coisa mais importante que você pode estudar agora** — é exatamente o que você vai contar no dia 07/08, com números ao lado. Abre direto no GitHub ou em qualquer editor de texto. São umas 2–3 páginas.

Se em algum parágrafo você ficar confuso ("não entendo o que esse número quer dizer"), **fala pro Augusto** — se um texto que você lê confuso, quem estiver assistindo também vai ficar. Com 11 dias ainda dá tempo de reescrever.

### Já enquanto estiver no painel: dá uma olhada nas abas de Índice e Achados

Depois do teste do mapa, clique na aba **Índice de dependência** — ela mostra o número principal do projeto em forma de ranking das 16 regiões. Se o professor perguntar "o que é esse índice?", a resposta está ali em blocos que abrem e fecham.

E clique também na aba **Achados & recomendações** — é a mais nova e é a que você vai usar pra apresentar. **Ninguém olhou a tela ainda pra checar se está quebrada**, então se algo estiver visualmente errado, avisa pro Augusto. Mas os números já estão conferidos.

### O resto, quando você tiver tempo

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

**Atenção pra não confundir:** essa dispensa vale **só** para aquele texto do índice. Os testes de leitura do **mapa** (o de 1 minuto, lá em cima) e, mais pra frente, do **texto de recomendações**, continuam valendo como condição de entrega — ficou combinado assim no dia 25/07.

**Se ainda assim você quiser fazer (15 minutos, e continua valendo a pena):** o jeito mais fácil agora é **pelo painel** — abra a aba **Índice de dependência** e leia os blocos no fim da página. Ali as perguntas do teste não aparecem, então não tem risco de você topar com a resposta sem querer (no arquivo `docs/definicao-indice-dependencia.md` elas estão no final; se preferir ler por lá, pare na seção 5 e me chame). Qualquer trecho em que você travar é trecho pra reescrever antes de 07/08, porque quem estiver assistindo a apresentação vai estar exatamente na sua posição: vendo o número pela primeira vez.

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
