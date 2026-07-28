# Plano de estudos E2E — Mapa de Evasão Assistencial da PB

> **Para que serve.** Levar Augusto e Pedro de "o projeto está pronto" para "os dois dominam
> o projeto inteiro" até 07/08/2026. Este é o plano mestre (as duas trilhas + cronograma
> conjunto + banco de perguntas). A trilha do Pedro, autocontida, está em
> [`plano-estudos-pedro.md`](plano-estudos-pedro.md).
>
> **Carga:** 2h/dia por pessoa, 28/07 a 06/08 (10 dias) = ~20h cada. Apresentação 07/08.

---

## 1. O princípio: cobertura igual, trilhas diferentes

O objetivo não é que os dois leiam as mesmas coisas — é que, no dia 07/08, **qualquer
pergunta da banca sobre qualquer parte do projeto tenha dois donos possíveis na sala.**

Os dois são iniciantes em análise de dados; a única assimetria real é de **exposição**:
o Augusto acompanhou a construção do pipeline de perto, o Pedro não. Se ambos estudassem
tudo em paralelo, os dois gastariam 20h cobrindo o mesmo terreno e sobraria buraco nos
dois lados. Então o projeto foi partido em duas metades de dificuldade equivalente — cada
um se aprofunda numa e a devolve ensinada para o outro no D8.

| | Augusto | Pedro |
|---|---|---|
| **Metade** | Como o número **nasce** | O que o número **quer dizer** |
| **Aprofunda** | Congelamento, tratamento, região de saúde, matriz O-D, índice, `app.py` | 7 achados, 5 recomendações, 9 limitações, sumário de evidências, painel na visão do gestor |
| **Pergunta da banca que ele absorve** | *"Como você calculou isso?"* / *"Esse dado é confiável?"* | *"E daí?"* / *"Esse número não prova o contrário?"* |
| **Risco se falhar** | O projeto parece mágica | O projeto parece planilha sem tese |
| **Por que essa metade** | Já viu esse terreno sendo construído — parte com contexto, não com vantagem técnica | Chega sem viés de quem construiu, que é justamente o que a leitura executiva exige |

Nenhuma das duas é a metade leve. As limitações e as armadilhas de número — a metade do
Pedro — são exatamente onde uma apresentação de dados costuma morrer.

**O mecanismo que iguala:** no **D8**, cada um dá uma aula de 30 minutos da própria metade
para o outro, **sem consultar arquivo**. Ensinar é o teste de domínio mais duro que existe;
o que você não conseguir explicar de cabeça é exatamente o que você ainda não sabe.

---

## 2. Cronograma conjunto

| Dia | Data | Augusto (2h) | Pedro (2h) | Junto? |
|---|---|---|---|---|
| D1 | 28/07 | Camada 0 — o chão comum | Camada 0 — o chão comum + **teste do mapa (US-12)** | Última meia hora, por chamada |
| D2 | 29/07 | Congelamento + tratamento da base | Achado central + Achados 1 e 2 | não |
| D3 | 30/07 | Região de saúde + matriz O-D | Achados 3 e 4 | não |
| D4 | 31/07 | Índice de dependência (3 validações) | Achado 5 (interestadual) | não |
| D5 | 01/08 | `app.py` — abas Matriz e Mapa | Achados 6 e 7 (PA-6, a régua) | não |
| D6 | 02/08 | `app.py` — Índice, Achados, Sobre os dados | As 5 recomendações + o enquadramento | não |
| D7 | 03/08 | Armadilhas de número + reprodutibilidade | As 9 limitações + sumário de evidências | não |
| D8 | 04/08 | **Handoff cruzado** — 30 min de aula cada + 60 min de perguntas mútuas | **sim** |
| D9 | 05/08 | **Ensaio 1 da demo (US-17)** — corrido, sem interromper, cronometrado | **sim** |
| D10 | 06/08 | **Ensaio 2** — só o que saiu torto no D9 + banco de perguntas | **sim** |
| — | 07/08 | **Apresentação** | | |

Os três últimos dias são conjuntos de propósito: estudo isolado não pega o que trava numa
apresentação a dois (quem fala qual parte, o que fazer quando a pergunta é da metade do
outro, quanto tempo cada bloco leva).

---

## 3. Camada 0 — o chão comum (D1, ambos)

Sete fatos que **os dois** precisam saber de cor, sem consultar nada. Não é o resumo do
projeto: é o mínimo abaixo do qual nenhuma outra frase faz sentido.

1. **O que é o SIH.** Sistema de Informações Hospitalares do SUS: registra toda internação
   paga pelo SUS. Cada linha da base é **uma internação** (uma AIH), não uma pessoa.
2. **O recorte.** 12 meses fechados de 2025, hospitais da Paraíba. **258.125 internações.**
3. **As duas colunas que fazem o projeto existir.** Município de **residência** do paciente
   e município de **internação**. Diferentes = evadiu.
4. **O achado central.** **50,5%** das internações acontecem fora do município de moradia.
5. **A unidade de planejamento.** A PB tem **16 regiões de saúde** (divisão oficial do SUS).
   Fora da **região** de residência: **67.633 internações = 26,4%**.
6. **O produto.** Matriz origem→destino + índice de dependência por região, num painel
   Streamlit. Nenhum painel público tem isso.
7. **O decisor.** Secretaria Estadual de Saúde da PB, área de regionalização e PPI
   (Programação Pactuada e Integrada — o instrumento formal de quem atende quem, e com
   que dinheiro).

**Checagem do D1 (um pergunta, o outro responde, por chamada):** os 7 acima, de cabeça.

**Pedro faz também no D1 — pendência aberta (US-12):** `streamlit run app.py` → aba
**Mapa** → olhar 1 minuto sem ajuda → nomear os polos. É critério de aceite de uma story
ainda em aberto; está travando desde a Etapa 16.

---

## 4. Trilha do Augusto — como o número nasce

Detalhada e autocontida em [`plano-estudos-augusto.md`](plano-estudos-augusto.md) — ela não
depende deste arquivo. Resumo para o Pedro acompanhar:

| Dia | Conteúdo | Arquivos |
|---|---|---|
| D1 | Camada 0 + percorrer o painel como avaliador | `app.py` |
| D2 | De onde vêm os dados: FTP → `.dbc` → parquet, tratamento, dicionário | `src/congelar_sih*.py`, `01-tratamento-base`, `dicionario-dados.md` |
| D3 | Região de saúde + matriz O-D + **a investigação do 47,8% → 49,8%** | `01-regiao-saude`, `01-matriz-od` (§4) |
| D4 | Índice de dependência e as 3 validações independentes | `definicao-indice-dependencia.md`, `01-indice-dependencia` |
| D5 | Painel: arquitetura, cache, abas Matriz e Mapa (+ o bug do GeoJSON) | `app.py` 95–660 |
| D6 | Painel: Índice, Achados, Sobre os dados (+ o bug do `UnboundLocalError`) | `app.py` 663–1202 |
| D7 | Reprodutibilidade, ordem dos notebooks, armadilhas de número | `atualizacao-mensal.md`, `conferir_narrativa.py`, `requirements.txt` |

---

## 5. Trilha do Pedro — o que o número quer dizer

Detalhada e autocontida em [`plano-estudos-pedro.md`](plano-estudos-pedro.md) — ela não
depende deste arquivo. Resumo para o Augusto acompanhar:

| Dia | Conteúdo | Fonte principal |
|---|---|---|
| D1 | Camada 0 + teste do mapa (US-12) | painel |
| D2 | Achado central + Achados 1 e 2 (funil; dependência de um endereço só) | narrativa §1–3 |
| D3 | Achados 3 e 4 (porte da cidade; estabilidade no ano) | narrativa §4–5 |
| D4 | Achado 5 (interestadual: 3.682, e por que a **razão** e não a fração) | narrativa §6 |
| D5 | Achados 6 e 7 (o que falta em cada região; a régua das 6 situações) | narrativa §7–8 |
| D6 | As 5 recomendações + o enquadramento (§14) | narrativa §9–14 |
| D7 | As 9 limitações + como usar o sumário de evidências ao vivo | narrativa §15, `sumario-evidencias.md` |

Ele roda `notebooks/90-eda-guiada.ipynb` (9 seções, feito sob medida, com 3 momentos de
entrada dele) ao longo de D2–D5, uma parte por dia.

---

## 6. As armadilhas de número (os dois decoram — não negociável)

Estas derrubam apresentação. Toda vez que um número for dito no dia 07/08, um dos dois
precisa saber qual armadilha está por perto.

| Armadilha | A verdade |
|---|---|
| **50,5% vs 50,2%** | Ambos certos, medem coisas diferentes. 50,5% = todas as internações na PB (inclui gente de outros estados que veio se internar aqui). 50,2% = só residentes da PB. Falou "paraibanos"? É 50,2%. |
| **26,4% é taxa estadual, não média das 16 regiões** | Pesa pelo volume. Não é a soma dos 16 índices dividida por 16. |
| **47,8% vs 49,8%** | 47,8% veio da fase de pesquisa, sem memória de cálculo. Refeito por 5 caminhos: 49,8%, sempre. Adotamos o que se prova. |
| **161 cidades com 100% de evasão** | 223 − 62 = 161. Elas não "perdem" pacientes: **não têm leito SUS**. Ranking de evasão ali mede se a cidade tem hospital, não acesso à saúde. |
| **A fração fronteira × interior (42%/58%)** | **Frágil** — varia de 11,5% a 58,5% conforme o corte de distância e chega a inverter. Nunca cravar. O que é estável é a **razão** de alta complexidade: interior 1,7× a 2,8× a fronteira, em todos os cortes. |
| **Mortalidade 29,4% vs 24,7%** | **Não prova nada.** Observacional, confundido por gravidade: só é transferido quem está estável o bastante para o transporte. Não sustenta leitura causal. |
| **14,7% "não classificado"** | Declarado de propósito, não forçado dentro de uma caixa para melhorar o resultado. |
| **Trocar de município ≠ percorrer distância** | Bayeux e Santa Rita evadem muito porque são coladas em João Pessoa — atravessa-se uma avenida, não o sertão. |

---

## 7. Banco de perguntas da banca

Treinar no D8 e D10. O **dono** responde; o outro precisa conseguir cobrir se travar.

**Método (dono: Augusto)**
1. De onde vêm os dados e por que a gente confia neles?
2. Como sei que sua base tratada não perdeu nada da original?
3. Por que o número mudou de 47,8% para 49,8%?
4. Você validou o índice contra o quê? (→ as 3 validações independentes)
5. Se eu quiser rodar isso com dados de agosto, o que acontece?
6. Por que região de saúde e não município?
7. O painel funciona sem internet?

**Significado (dono: Pedro)**
8. Metade das pessoas viajando é ruim? Não é assim que o SUS deve funcionar mesmo?
9. Se só 3,7% é referência legítima, o resto todo é falha do sistema?
10. Viajar para internar piora o desfecho do paciente?
11. Por que recomendar coisas diferentes para regiões com o mesmo índice?
12. Qual a limitação mais séria do trabalho de vocês?
13. Isso já não existe no DATASUS/TabNet?
14. A rede privada não muda esse retrato?
15. O que a Secretaria faz na segunda-feira com isso?

**Regra de ouro para o dia:** número que não está no `reports/sumario-evidencias.md` não se
diz. Se perguntarem de onde saiu, a resposta é uma linha da tabela apontando o arquivo.

---

## 8. Critério de aprovação do plano (o teste final, D10)

O plano funcionou se, no fim do D10, **cada um** conseguir:

1. Recitar os 7 fatos da Camada 0 sem consultar nada.
2. Explicar o índice de dependência para alguém de fora, em 2 frases.
3. Dizer, para cada um dos 7 achados, o número que o sustenta **e** a recomendação que sai dele.
4. Citar 3 das armadilhas da seção 6 e por que cada uma derruba uma frase errada.
5. Rodar o painel do zero e navegar as 5 abas sem hesitar.
6. Responder 3 perguntas sorteadas da **metade do outro**.

O item 6 é o que prova que a cobertura ficou igual. Se falhar, o handoff do D8 não pegou —
repetir a aula do tópico que falhou.
