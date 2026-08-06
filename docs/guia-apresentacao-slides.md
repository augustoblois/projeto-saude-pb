# Guia de apresentação — roteiro slide a slide (07/08/2026)

> Este guia acompanha o deck publicado (16 slides, navegação por seta/teclado). Ele não
> substitui os planos de estudo — `plano-estudos-augusto.md` e `plano-estudos-pedro.md`
> ensinam o **conteúdo**; este arquivo ensina **o que dizer em cada slide, quanto tempo
> gastar, e quem fala**. Uma coisa é saber o índice de dependência de cabeça; outra é saber
> em que slide ele aparece e a deixa para passar a palavra ao outro.
>
> Tempo total estimado: **~13 min de fala corrida + 3–5 min de demo ao vivo = ~17 min.**
> Ajustem o tempo por slide no ensaio — os números aqui são ponto de partida, não regra.

---

## Divisão de fala

Segue a mesma lógica do `plano-estudos.md`: Augusto fala a metade "como o número nasce"
(slides 2–5 e 12–14), Pedro fala a metade "o que o número quer dizer" (slides 6–11 e 15).
Capa, demo e encerramento são dos dois.

| Slides | Bloco | Quem fala |
|---|---|---|
| 1 | Capa | Augusto abre |
| 2–5 | Contexto, dados, tratamento, produto | **Augusto** |
| 6–11 | Achados e recomendações | **Pedro** |
| 12 | O painel | **Augusto** |
| 13 | Demo ao vivo | os dois — Augusto navega, Pedro comenta o que aparece |
| 14 | Como mantemos atualizado | **Augusto** |
| 15 | Limitações | **Pedro** |
| 16 | Encerramento | os dois |

Duas trocas de bastão (slide 5→6 e slide 11→12): combinar a deixa exata no ensaio para não
ficar um segurando o notebook sem saber se já é a vez do outro.

---

## Slide 1 — Capa (~20s)

Só ler o título e situar: quem são vocês, a disciplina, a data. Não entrar em número
nenhum ainda — a capa é para a banca se situar, não para começar a argumentar.

---

## Slide 2 — O problema (~45s) · Augusto

**Dizer:** metade das internações da PB não acontece no município do paciente — isso
sozinho não é problema, o que importa é para onde, quem, e se é estável. Fechar com o
critério anti-genérico: essa matriz não existe em painel público nenhum, e quem decide
regionalização (Secretaria Estadual de Saúde) não tem essa ferramenta hoje.

**Não fazer:** não citar 50,5% ainda — esse número é o clímax do slide 6, gasto aqui perde
o efeito.

---

## Slide 3 — A fonte dos dados (~45s) · Augusto

**Dizer:** SIH/DATASUS, 12 meses de 2025, 258.125 internações, tudo congelado localmente —
regra nº 1 do projeto é que nada na apresentação depende de internet.

**Se perguntarem "por que não usar a API do PySUS":** ela se mostrou instável; o FTP direto
é mais lento mas confiável — está documentado em `src/congelar_sih.py`.

---

## Slide 4 — Do bruto ao confiável (~45s) · Augusto

**Dizer:** 118 colunas auditadas, 46 usáveis; 223 municípios atribuídos à região de saúde
correta, zero perdas; e o padrão de rigor do projeto — 4 das 7 análises voltaram
reprovadas na primeira revisão, sempre por texto que dizia mais do que o dado sustentava,
nunca por conta errada.

**Por que contar isso:** é a frase que compra credibilidade antes de qualquer número
aparecer — mostra que o projeto foi auditado, não só calculado.

---

## Slide 5 — O coração do produto (~45s) · Augusto

**Dizer:** duas peças. A matriz origem→destino (quem sai de onde, vai para onde, quando) e
o índice de dependência (% das internações de cada região que acontecem fora dela) — o
diferencial do projeto, validado por 3 caminhos de cálculo independentes com diferença
zero entre eles.

**Deixa para o Pedro:** "e o que essa matriz e esse índice mostraram, o Pedro conta."

---

## Slide 6 — Achado central (~30s) · Pedro

Slide do número gigante — deixar o silêncio trabalhar. Ler a frase do funil, dizer
**50,5%**, e parar um segundo antes de seguir para o slide 7.

---

## Slide 7 — Funil, não malha (~45s) · Pedro

**Dizer:** João Pessoa + Campina Grande = 58,6% de todo o deslocamento; 7 municípios
explicam 80%; e o dado mais forte — só 62 dos 223 municípios da PB internaram alguém em
2025. Fechar com: mais de 7 em cada 10 cidades não têm onde internar, não é falta de
paciente.

---

## Slide 8 — Dependência de um endereço só (~45s) · Pedro

**Dizer:** 8 das 16 regiões passam de 50% — a 3ª Região chega a 84,5%. E o detalhe que
muda a ação: em 7 dessas 8, a maioria vai para **um único destino** (92,3% da 14ª para
JP). Fechar com a frase: pactuar com muitos é política complicada, pactuar com um é
contrato.

---

## Slide 9 — Porte e estabilidade (~45s) · Pedro

**Dizer:** a tabela por porte (98,1% nas cidades pequenas → 9,3% nas grandes, sem
inversão), e que 133 das 140 cidades pequenas não internaram ninguém em casa no ano
inteiro — não é gestão municipal ruim, é impossibilidade estrutural. Fechar com
estabilidade: 13 dos 20 maiores fluxos se repetem nos 12 meses — é demanda a contratar,
não emergência a socorrer.

---

## Slide 10 — Diagnóstico por região (~45s) · Pedro

**Dizer:** cada uma das 8 regiões críticas falta uma coisa diferente — maternidade na 11ª
(92,5% dos partos fora), pediatria na 12ª/2ª/4ª, cirurgia na 3ª/15ª. E o número que separa
o que é urgente do que é aceitável: 13,0% do deslocamento é urgência cirúrgica sem
retaguarda (8.768 casos/ano), contra só 3,7% de referência legítima.

---

## Slide 11 — Recomendações (~60s) · Pedro

**Dizer as 5, rápido, uma frase cada:** formalizar os polos na PPI · priorizar as 8
regiões críticas uma a uma, cada uma com o destino nominal · usar a matriz O-D como base
de cálculo da PPI · separar fronteira (acordo) de interior (serviço novo) no fluxo
interestadual · dar a cada região o instrumento certo, não "pactuar" para todas.

**Deixa para o Augusto:** "e tudo isso está no painel que a Secretaria pode abrir agora —
o Augusto mostra."

---

## Slide 12 — O painel (~45s) · Augusto

**Dizer:** por que o visual é de documento técnico e não de dashboard (decisão deliberada,
não falta de tempo), as 5 abas em uma frase cada, e por que é rápido — nunca recalcula a
base ao vivo, só lê tabelas já prontas.

**Deixa direto para a demo:** "vamos abrir de verdade."

---

## Slide 13 — Demo ao vivo (~3–5 min) · os dois

Este é o slide que importa mais amanhã. Roteiro sugerido de navegação real no painel:

1. Abrir a URL (ou já estar aberta numa aba, com o slide só como pano de fundo).
2. **Aba Matriz O-D** — trocar o filtro de origem ao vivo, mostrar a resposta instantânea.
3. **Aba Mapa** — apontar os dois territórios (JP e CG) e contar rapidamente a história do
   bug do sentido anti-horário do GeoJSON, se der tempo (é a melhor história técnica do
   projeto e mostra rigor de QA).
4. **Aba Índice de dependência** — clicar na 3ª Região, mostrar o cartão de detalhe batendo
   com o número do slide 8.
5. **Aba Achados & recomendações** — rolar rápido, mostrar que é o mesmo texto do slide 11.
6. **Aba Sobre os dados** — apontar que ela existe e responde sozinha "de onde vêm esses
   números", sem ninguém precisar decorar.

**Se algo travar:** o painel funciona offline — não é dependência de rede que pode falhar,
é só reabrir a aba. Não perder tempo depurando ao vivo; seguir para o próximo ponto do
roteiro e voltar depois se sobrar tempo.

---

## Slide 14 — Como mantemos atualizado (~60s) · Augusto

**Esta é a pergunta mais provável da banca — a resposta precisa sair pronta, sem hesitar.**

**Dizer, nesta ordem:**
1. "O DATASUS publica cada mês com cerca de dois meses de atraso."
2. "Quando publica, um comando — `python src/congelar_sih.py` — baixa e valida esse mês.
   Ele é idempotente: rodar de novo nunca refaz o que já está pronto, só completa o que
   falta."
3. "Três notebooks reprocessam a cadeia — tratamento, região de saúde, matriz — e as
   análises e o índice atualizam atrás, na ordem documentada."
4. "O painel não muda uma linha de código: ele só lê as tabelas regeneradas."
5. **Fechar com a trava de qualidade:** "os notebooks têm verificações automáticas com os
   totais de 2025 — quando um mês novo entra, elas *têm* que falhar, de propósito, e isso é
   o sinal para conferir se o número novo faz sentido antes de aceitar."

**Se perguntarem "e se quiserem outro estado, ou outro ano":** ampliar dentro do mesmo ano
é uma linha de código; trocar de ano é um trabalho consciente de ~30 minutos em 4 pontos
documentados — nunca surpresa, está tudo escrito em `docs/dados/atualizacao-mensal.md`.

**Não dizer:** não prometer atualização automática/agendada — o projeto foi desenhado para
ser **deliberadamente offline**; atualizar é um ato consciente, não um cron job. Se
perguntarem por que não é automático, a resposta é a regra nº 1: nada na apresentação (nem
na operação real da Secretaria) deve depender de uma fonte viva que pode falhar sem
aviso.

---

## Slide 15 — Limitações (~45s) · Pedro

**Dizer as 4 mais fortes, rápido:** só o SUS (rede privada não aparece) · um ano só (ainda
não é série histórica) · dezembro pode subir um pouco (retificação do DATASUS, declarada,
não escondida) · a régua mede necessidade, não desfecho (nenhuma taxa de óbito aqui prova
causa).

**Se perguntarem sobre a mortalidade (29,4% vs 24,7%):** não é vitória nem derrota da
tese — é observacional e confundido por gravidade: só é transferido quem está estável o
bastante para o transporte.

---

## Slide 16 — Encerramento (~20s) · os dois

Agradecer, repetir a URL do painel uma última vez, abrir para perguntas.

---

## Referência rápida — se travar em algum número

Regra vale para os dois: **número que não está em `reports/sumario-evidencias.md` não se
diz.** Se bater um branco no meio da fala, é melhor dizer "esse número está rastreado no
sumário de evidências, posso confirmar depois" do que arriscar um valor de cabeça.

As armadilhas de número mais prováveis de confundir vocês dois no calor da hora — tabela
completa em `plano-estudos-augusto.md` (D7) e `plano-estudos-pedro.md` (03/08):

- **50,5% vs 50,2%** — geral (inclui não-residentes) vs só residentes da PB.
- **26,4%** é a taxa do estado (ponderada por volume), não a média simples das 16 regiões.
- **47,8% → 49,8%** — o número antigo não sobreviveu à reconferência; adotamos o que se
  prova por 5 caminhos.
- **A fração fronteira × interior nunca se crava** — é frágil (11,5% a 58,5% conforme o
  corte). O que é sólido é a razão de complexidade (1,7× a 2,8×).
