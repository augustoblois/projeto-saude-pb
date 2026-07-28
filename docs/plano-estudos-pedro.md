# Plano de estudos — Pedro

> **Pedro, este arquivo é seu.** É o roteiro do que estudar, dia a dia, até a apresentação
> do dia 07/08. São **2 horas por dia, de 28/07 a 06/08**. Nos três últimos dias vocês
> estudam juntos.

---

## Como o trabalho foi dividido entre vocês

O projeto foi partido em duas metades do mesmo tamanho e da mesma dificuldade:

- **Augusto: como o número nasce.** De onde vieram os dados, como foram limpos, como as
  contas foram feitas e conferidas, como o painel foi montado.
- **Você: o que o número quer dizer.** O que cada achado significa, que recomendação sai
  dele, e — principalmente — **o que os números NÃO dizem**.

A divisão não é por habilidade: os dois são iniciantes em análise de dados. É por
**exposição** — o Augusto acompanhou a construção do pipeline de perto, então aprofundar
essa metade custa menos tempo pra ele. E tem uma vantagem sua nisso: quem construiu uma
análise fica viciado nela. Você chega na leitura executiva sem esse viés, que é exatamente
o que ela exige.

A sua metade não é a mais leve. Explicar o significado e defender os limites do trabalho é
onde uma apresentação de dados costuma quebrar. Pergunta de método tem resposta pronta num
arquivo; pergunta de "e daí?" não tem.

No **dia 04/08** vocês trocam: cada um dá uma aula de 30 minutos da sua metade para o outro,
**sem olhar arquivo nenhum**. É assim que os dois terminam sabendo o projeto inteiro. Se
você não conseguir explicar de cabeça, é exatamente ali que você ainda não sabe.

---

## O que você precisa saber de cor (os 7 fatos)

Isto é a base de tudo. Sem isso, nenhuma outra frase da apresentação se sustenta. Decore
até responder sem pensar:

1. **De onde vêm os dados:** SIH — o sistema do Ministério da Saúde que registra toda
   internação paga pelo SUS. **Cada linha é uma internação, não uma pessoa** (quem internou
   três vezes conta três vezes).
2. **O recorte:** o ano de 2025 inteiro, hospitais da Paraíba. **258.125 internações.**
3. **As duas informações que fazem o projeto existir:** a cidade onde a pessoa **mora** e a
   cidade onde ela **internou**. Diferentes = ela viajou.
4. **O número principal:** **50,5%** das internações acontecem fora da cidade onde a pessoa
   mora. Metade.
5. **As regiões:** a Paraíba é dividida oficialmente em **16 regiões de saúde**. Saindo da
   própria **região**: **67.633 internações, ou 26,4%**.
6. **O que a gente entregou:** a tabela de quem vai de onde pra onde + o índice de
   dependência das 16 regiões, num painel. **Isso não existe em nenhum painel público.**
7. **Pra quem serve:** a Secretaria Estadual de Saúde da PB — a área que decide quem atende
   quem, e com que dinheiro (isso se chama PPI, Programação Pactuada e Integrada).

---

## Dia 28/07 — o chão comum + uma pendência sua

**1. Decorar os 7 fatos acima** (~40 min). Escreva à mão, ajuda.

**2. O teste do mapa** (~5 min) — isto está travado esperando você desde a semana passada:

- Terminal na pasta do projeto → `streamlit run app.py`
- Abre no navegador. Clique na aba **Mapa**.
- Olhe por **1 minuto, sem ajuda de ninguém**.
- Responda ao Augusto: **quais cidades puxam pacientes de toda a Paraíba?**

Se as duas saltarem aos olhos, o mapa passou. Se você precisar procurar, o mapa está errado
e o Augusto conserta antes do dia 07/08. **Responda com sinceridade** — este teste só vale
alguma coisa se for honesto.

**3. Passeie pelas 5 abas do painel** (~30 min), sem estudar nada ainda. Só se familiarize
com onde cada coisa mora. Depois, no dia, você não pode procurar botão na frente da banca.

**4. Cobrança mútua** (~15 min, por chamada): um pergunta os 7 fatos, o outro responde.

---

## Dias 29/07 a 03/08 — os achados, um bloco por dia

Sua leitura principal é **`reports/narrativa-executiva.md`**. É o texto da apresentação
inteiro, ~5 páginas. Você vai lê-lo em pedaços, e não de uma vez.

**Método de todo dia (2h):**
1. Ler a seção do dia (~30 min).
2. Rodar o pedaço do dia do notebook de estudo `notebooks/90-eda-guiada.ipynb` (~40 min) —
   ele foi feito sob medida pra você, cada trecho tem explicação em português antes, e tem
   3 momentos onde você coloca a sua cidade e a sua região e roda.
3. **Fechar tudo e escrever de cabeça** (~30 min): o achado do dia em 3 frases + o número
   que o sustenta + o que fazer a respeito.
4. Conferir o que você escreveu contra o texto (~20 min).

O passo 3 é o que faz o estudo grudar. Ler de novo não é estudar — tentar lembrar é.

### 29/07 — O achado central + Achados 1 e 2 (seções 1, 2 e 3 da narrativa)
- Metade das internações acontece fora da cidade de moradia.
- **João Pessoa 33,5% + Campina Grande 25,2% = 58,6%** de todo o deslocamento. Com Patos,
  67,2%. Bastam 7 cidades pra explicar 80%.
- **Só 62 das 223 cidades da PB** tiveram alguma internação SUS no ano.
- A frase que resume o projeto: **a rede não é uma malha de cidades que se apoiam — é um
  funil que despeja quase todo mundo em dois endereços, sempre os mesmos, o ano inteiro.**
- 8 das 16 regiões passam de 50% de dependência. E em 7 dessas 8, a maioria de quem sai vai
  para **um único destino** (92,3% da 14ª vai pra João Pessoa). Isso importa porque
  **pactuar com muitos é política complicada; pactuar com um é contrato.**

### 30/07 — Achados 3 e 4 (seções 4 e 5)
- **O tamanho da cidade decide quase tudo:** até 10 mil habitantes, 98,1% dos moradores
  internam fora; acima de 100 mil, 9,3%. Sem uma única inversão na escada.
- **133 das 140 cidades pequenas não internaram nenhum morador em casa no ano inteiro.**
- Por que isso muda a conclusão política: **não é má gestão da prefeitura, é impossibilidade
  estrutural.** Cidade de 8 mil habitantes não sustenta hospital, e nunca vai. Cobrar de
  cada prefeito que resolva o seu é cobrar o impossível de 140 cidades ao mesmo tempo.
- **O padrão não muda no ano:** 13 dos 20 maiores caminhos aparecem nos 12 meses. Isso
  importa porque **o que é previsível pode ser orçado** — não é emergência a socorrer, é
  demanda a contratar com número fixo no começo do ano.

### 31/07 — Achado 5, o fluxo pra fora do estado (seção 6)
- **3.682 paraibanos internaram em PE, RN ou CE** — 1,4%. Pouco, e isso já é informação: o
  problema é quase todo **dentro** da Paraíba.
- Mas o perfil é diferente: 41% vai pra Recife, e quem sai do interior tem internação bem
  mais grave que quem sai da divisa.
- **Convivem dois fenômenos:** quem mora na divisa e usa o hospital do vizinho por estar
  perto (o 2º maior destino é Alexandria/RN, cidade pequena de fronteira, não um polo), e
  quem atravessa o estado porque o serviço não existe perto de casa.
- **CUIDADO AO FALAR:** nunca crave a divisão "42% fronteira / 58% interior". Esse número é
  frágil — muda conforme onde a gente corta a distância, e chega a inverter. O que é
  sólido é a **comparação**: quem vem do interior tem de 1,7 a 2,8 vezes mais casos de alta
  complexidade que quem vem da fronteira, **em todos os cortes testados**. Fale a
  comparação, nunca a fração.

### 01/08 — Achados 6 e 7 (seções 7 e 8) — o dia mais denso
- **Cada região depende de fora por um motivo diferente.** A conta: comparar a evasão de
  cada especialidade com a evasão geral daquela região. O **excesso** é o que falta ali.
- **11ª Região: 92,5% dos partos das moradoras acontecem fora** — 38 pontos acima da média
  dela. É uma região que consegue tratar, mas não consegue parir. E parto é a internação
  mais previsível que existe: dá pra planejar com nove meses de antecedência.
- **Pediatria é o maior buraco em três regiões** (12ª, 2ª e 4ª). Cirurgia na 3ª e na 15ª.
- **A régua:** cada uma das 67.633 internações que saem da região foi classificada em 6
  situações. Evasão evitável 38,8% · demanda represada 20,2% · não classificado 14,7% ·
  **urgência cirúrgica sem retaguarda 13,0%** · alta complexidade eletiva 9,8% ·
  referência legítima 3,7%.
- **As duas linhas que você precisa saber dizer:** 8.768 cirurgias de urgência por ano
  atravessaram região sem retaguarda (numa fila eletiva a espera custa qualidade de vida;
  numa urgência, custa tempo que não volta). E só **3,7%** é o sistema funcionando como
  projetado — ou seja, **a maior parte do deslocamento não é o SUS operando certo.**

### 02/08 — As 5 recomendações e o enquadramento (seções 9 a 14)
Para cada uma, saiba dizer **o que fazer** e **por causa de qual número**:
1. Reconhecer e financiar formalmente os polos (58,6%; JP recebe 41.761 a mais do que envia).
2. Priorizar as 8 regiões críticas uma a uma, cada uma com o destino que já a absorve.
3. Usar a matriz origem→destino como base de cálculo da PPI (o fluxo é estável, dá pra orçar).
4. Separar os dois problemas do fluxo interestadual (acordo de fronteira ≠ serviço novo).
5. Dar a cada região o instrumento que o caso dela pede, em vez de "pactuar" pra todas.
- **O enquadramento que sustenta tudo (seção 14), decore a frase:** a unidade de
  planejamento hospitalar na Paraíba precisa ser a **região de saúde, não o município**.
- **A frase de fecho da Recomendação 5:** recomendar pactuação para tudo é aplicar a
  solução de 3,7% ao problema de 52%.

### 03/08 — As limitações (seção 15) + o sumário de evidências
Este é o **seu dia mais importante**. Banca gosta de atacar o limite, e quem já declarou o
limite antes de ser perguntado ganha credibilidade em vez de perder.

Saiba dizer todas as 9, e principalmente estas quatro:
- **Cada linha é uma internação, não uma pessoa.**
- **Só o SUS** — a rede privada não aparece.
- **Todos os índices são um piso**: paraibano internado em outro estado não entra na base
  principal, então a dependência real é igual ou maior, nunca menor.
- **Viajar não piora o desfecho — e o dado também não prova o contrário.** No caso mais
  grave, quem ficou teve 29,4% de óbito e quem foi transferido, 24,7%. Parece que viajar
  ajuda, mas **não prova nada**: só é transferido quem está estável o bastante pro
  transporte; quem morre antes da remoção conta como "não viajou". **Se perguntarem isso,
  esta é a resposta — não caia na tentação de usar esse número como vitória.**

**Depois, aprenda a usar `reports/sumario-evidencias.md`** (~30 min): é a tabela que diz, de
cada número do projeto, o arquivo exato de onde ele saiu. **Regra do dia 07/08:** se
perguntarem "de onde saiu esse número?", você não precisa lembrar — você abre essa tabela e
lê a linha. Treine achar 3 números nela.

**Duas confusões de número que você precisa saber desfazer:**
- **50,5% e 50,2% são ambos certos.** 50,5% = todas as internações feitas na PB (inclui
  gente de outro estado que veio internar aqui). 50,2% = só quem mora na PB. Se a frase
  fala de "paraibanos", o número é 50,2%.
- **26,4% é a taxa do estado, não a média das 16 regiões.** Ela pesa pelo volume — não é a
  soma dos 16 índices dividida por 16.
- Bônus: **161 cidades aparecem com 100% de evasão** (223 − 62). Não é que elas percam
  pacientes: **elas não têm leito SUS**. Ali, "evasão" mede se a cidade tem hospital, não
  acesso à saúde.

---

## 04/08 — Troca de aulas (junto, 2h)

- **30 min:** você dá aula da sua metade pro Augusto — os 7 achados, as recomendações, as
  limitações. **Sem olhar arquivo.**
- **30 min:** ele dá aula da metade dele pra você — de onde vieram os dados, como as contas
  foram feitas e conferidas, como o painel foi montado.
- **60 min:** perguntas cruzadas, usando o banco de perguntas que está no plano do Augusto
  (`docs/plano-estudos.md`, seção 7). Cada um responde 3 perguntas **da metade do outro**.

O que você não conseguir responder aqui ainda dá tempo de estudar. Em 06/08 não dá mais.

---

## 05/08 — Ensaio 1 (junto, ~1h)

A apresentação inteira, do começo ao fim, cronometrada. Você apresenta; o Augusto assiste
**sem interromper** e anota. Só no fim vocês conversam.

Combinem antes: quem fala qual parte, e o que fazer quando a pergunta cai na metade do
outro (a regra simples: o dono responde, o outro completa se travar).

---

## 06/08 — Ensaio 2 e fechamento (junto, ~1h)

Só o que saiu torto no dia anterior + o banco de perguntas de novo. Não estude coisa nova
neste dia — véspera é pra consolidar, não pra abrir frente.

**Você está pronto se conseguir, sem consultar nada:**
1. Recitar os 7 fatos.
2. Explicar o índice de dependência pra alguém de fora, em 2 frases.
3. Dizer, de cada um dos 7 achados, o número que o sustenta e a recomendação que sai dele.
4. Citar 3 das confusões de número e por que cada uma derruba uma frase errada.
5. Navegar as 5 abas do painel sem hesitar.
6. Responder 3 perguntas da metade do Augusto.

---

## Uma regra pro dia 07/08

**Número que não está no `reports/sumario-evidencias.md` não se diz.** Tudo que está lá tem
origem rastreável num arquivo. Chutar um número que soa bem é o único jeito de perder uma
apresentação que está tecnicamente correta.

E se algum parágrafo da narrativa ficar confuso **pra você**, fala pro Augusto. Se você lê
confuso, quem assiste também fica — e ainda dá tempo de reescrever.
