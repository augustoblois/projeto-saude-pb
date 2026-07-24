# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (24/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito, revisado e aprovado** — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação. Os documentos vivem na pasta `docs/` (você não precisa ler; sua referência é este arquivo).
- **Decisões já fechadas e registradas:** painel em **Streamlit** (ferramenta de Python que transforma análise em site interativo); os **paraibanos internados em outros estados** (PE/RN/CE) entram na análise; e o **índice de dependência** — o número principal do projeto — é a porcentagem dos moradores de cada região que precisou internar FORA da própria região.
- **A análise central do projeto está pronta:** cada internação sabe a qual "região de saúde" pertence (a divisão oficial do SUS — a PB tem 16), e já existe a **matriz origem→destino** — a tabela que diz, de cada cidade e de cada região, quantos pacientes foram internar em cada outra, mês a mês. É o coração do projeto: tudo daqui pra frente (análises, índice, painel) consome essa matriz.
- **O número principal do projeto mudou de 47,8% pra 49,8%** (internações de jan/2025 fora do município de residência). O 47,8% veio da fase de pesquisa e não tinha memória de cálculo; ao refazer a conta com a base congelada — de cinco jeitos diferentes — o resultado é 49,8%, sempre. Adotamos o número que conseguimos provar. No ano fechado: **50,5% das internações são fora do município onde o paciente mora**.
- **Também já sabemos quantos paraibanos internaram FORA do estado em 2025: 3.682** (a maioria em Pernambuco e no Rio Grande do Norte). Baixamos os dados dos 3 estados vizinhos e filtramos só quem mora na PB. É pouco perto das 258 mil internações internas — sinal de que o problema de "viajar pra internar" acontece quase todo DENTRO do estado.
- **As cinco análises principais do projeto estão prontas e conferidas** (fizemos todas nesta sessão — detalhe logo abaixo). Falta agora transformar isso no painel interativo e no texto de recomendações.
- **Prazo:** apresentação dia 07/08/2026 (14 dias).

## O que aconteceu na última sessão (24/07/2026)

Fizemos as cinco análises que sustentam o projeto. Cada uma responde uma pergunta, e cada uma foi conferida por uma segunda checagem independente — alguém que refaz as contas do zero, sem olhar como a primeira foi feita, e só dá o "ok" se os números baterem. Quatro delas voltaram com correção antes de serem aprovadas; contamos isso aqui embaixo porque é exatamente o que garante que os números do dia 07/08 estão certos.

**1. Pra onde vão os pacientes que saem da própria cidade?**
Dois municípios ficam com **58,6% de todo esse movimento**: João Pessoa (33,5%) e Campina Grande (25,2%). Somando Patos, chega a 67,2%. Sete cidades absorvem 80% do fluxo. E um número que ninguém esperava: **das 223 cidades da Paraíba, só 62 registraram alguma internação pelo SUS em 2025** — as outras 161 não internaram ninguém, nem os próprios moradores. Testamos se isso muda ao longo do ano: não muda, em nenhum mês a participação dessas duas cidades cai abaixo de 56%.

**2. Cidade pequena perde mais paciente que cidade grande?**
Muito mais, e de forma perfeitamente escalonada: nas cidades de até 10 mil habitantes, **98% dos moradores internam fora**; acima de 100 mil habitantes, só 9%. O dado mais forte: **133 das 140 cidades pequenas não internaram um único morador dentro de casa no ano inteiro** — quase sempre porque não têm hospital com leito do SUS. Isso muda o tom da conclusão do projeto: o problema não é prefeitura pequena administrando mal, é que cidade pequena não tem como sustentar hospital sozinha. A saída é as cidades se organizarem por região.

**3. Os caminhos dos pacientes mudam ao longo do ano?**
Não. Dos 20 trajetos mais usados no ano, **13 aparecem entre os mais usados em todos os 12 meses**. Isso importa para a recomendação final: como os caminhos são estáveis, dá para a Secretaria de Saúde planejar e reservar vagas fixas neles. Se mudassem todo mês, a recomendação teria que ser outra.

**4. Quem sai da Paraíba, sai por quê?**
São 3.682 pessoas no ano (1,41% do total). Recife recebe 41% delas. A resposta tem duas partes: quem mora **na divisa** com outro estado normalmente atravessa para pegar um hospital de rotina que fica perto; quem sai **do interior** vai atrás de tratamento grave — o perfil desses casos é de 1,7 a 2,8 vezes mais complexo, e o custo médio da internação é o dobro. Uma surpresa: o segundo destino mais procurado não é Natal, é **Alexandria, no Rio Grande do Norte** — cidade pequena, mas com hospital que atende todo o sertão paraibano da divisa. Conferimos se não era erro de cadastro: não é, é real.

**5. O número principal do projeto: o índice de dependência.**
Ele mede, para cada uma das 16 regiões de saúde, quanto dos seus moradores precisa internar fora da própria região. **Oito das 16 regiões passam de 50%** — ou seja, em metade do estado, a maioria dos moradores interna fora de casa. A 3ª Região é a mais dependente (84,5%); as regiões de João Pessoa (1,8%) e Campina Grande (4,1%) são as que resolvem quase tudo em casa. Esse número foi calculado por três caminhos diferentes, propositalmente, para ver se davam o mesmo resultado — deram, idênticos.

**O que a conferência pegou, e por que isso é boa notícia:** em quatro das cinco análises, a segunda checagem encontrou problema e mandou corrigir antes de aprovar. Nenhum era erro de conta — em todos, o número calculado estava certo, mas o **texto escrito ao redor dele** tinha ficado desatualizado ou dizia mais do que o dado permitia. Dois exemplos: um gráfico afirmava "sete regiões" no título enquanto a própria imagem mostrava oito barras; e uma conclusão dizia que "em nenhum cenário a divisa explica a maior parte dos casos", quando a tabela logo acima mostrava dois cenários em que explicava. São exatamente os erros que alguém da banca encontra em dez segundos olhando o slide. Todos corrigidos.

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

### ⚠️ Tem uma tarefa esperando por você (e ela trava uma parte do projeto)

O **índice de dependência** é o número principal do projeto — o diferencial que não existe em nenhum painel público. Ele já está calculado e conferido, mas falta uma coisa que só você pode fazer, e o projeto não considera essa etapa concluída sem ela.

**A tarefa:** ler a explicação do índice e tentar contar, com suas próprias palavras, o que aquele número significa. Se você travar em algum ponto, o texto é que está mal escrito — não você. É exatamente isso que queremos descobrir antes da apresentação, porque quem vai ouvir a gente no dia 07/08 vai estar na mesma posição que você: vendo o número pela primeira vez.

**Como fazer — e tem um detalhe importante na ordem:**
1. Abrir o arquivo `docs/definicao-indice-dependencia.md` (dá pra abrir no GitHub direto pelo navegador, ou no VS Code).
2. Ler **só até a seção 5**, e **uma vez só** — sem voltar, sem reler.
3. **Parar de ler ali e chamar o Augusto** (WhatsApp já serve). Ele vai te fazer 7 perguntas sobre o que você leu.

**Por que parar na seção 5:** o final do arquivo tem justamente as perguntas que ele vai te fazer — e uma delas até entrega a resposta. Se você ler antes, a gente perde a única chance de saber se o texto se explica sozinho. É o mesmo motivo pelo qual não se lê o gabarito antes da prova: aqui quem está sendo testado é o texto, não você.

Não precisa estudar nem se preparar. Quanto mais crua a sua reação, mais útil ela é. Se você entender de primeira, o texto está pronto; se travar em alguma parte, a gente reescreve antes da apresentação — que é justamente o ponto. Responder "não entendi essa parte" é o resultado mais útil que você pode dar.

### Novas tabelas prontas pra abrir no Excel

Ficaram na pasta `outputs/tables/` (nomes começando com `pa1_`, `pa3_`, `pa4_`, `pa5_`) e em `data/processed/indice_dependencia_regional.csv`. Todas abrem direto no Excel, sem precisar escrever código. As mais interessantes pra dar uma olhada:
- `pa3_saldo_municipios.csv` — mostra, por cidade, quantos pacientes ela **recebe** de fora menos quantos ela **manda** pra fora. Número positivo = a cidade atrai pacientes; negativo = perde.
- `indice_dependencia_regional.csv` — o índice das 16 regiões, do mais dependente ao mais autossuficiente.

Os gráficos que geramos estão em `outputs/figures/` (arquivos de imagem, é só abrir).

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
