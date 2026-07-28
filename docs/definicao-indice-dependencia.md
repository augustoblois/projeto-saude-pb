# Índice de dependência por região de saúde — definição oficial

> **Story:** US-09 (EP-03) · **Decisão de origem:** D-2 do gate do backlog (fórmula fechada, não reaberta).
> **Este texto é o que aparece no painel** (RF-02): ele precisa ser entendido por um gestor
> não-técnico em **uma leitura**, sem ajuda de ninguém.
> **Cálculo e validação:** `notebooks/01-indice-dependencia.ipynb` · **Tabela:** `data/processed/indice_dependencia_regional.csv`

---

## 1. O que o índice mede (em uma frase)

> **O índice de dependência de uma região de saúde é a porcentagem das internações dos
> moradores daquela região que aconteceram em hospitais fora dela.**

Ou seja: de cada 100 vezes que um morador da região precisou de internação em 2025,
quantas dessas vezes ele teve que ser internado em outra região.

Quanto **maior** o índice, mais aquela região precisa de fora para cuidar da própria
gente. Quanto **menor**, mais ela resolve dentro de casa.

## 2. A fórmula

Em notação simples, para uma região **R**:

```
                internações de moradores de R realizadas FORA de R
índice(R) = 100 × ──────────────────────────────────────────────────
                    total de internações de moradores de R
```

Em português, campo a campo:

- **Numerador** (o de cima) — quantas internações de pessoas que **moram** na região R
  aconteceram em hospitais **de outra região** de saúde.
- **Denominador** (o de baixo) — quantas internações de pessoas que **moram** na região R
  aconteceram no total, somando as de dentro e as de fora.
- **× 100** só converte a proporção em porcentagem.

O resultado é sempre um número entre 0 e 100:

- **0%** = a região interna 100% dos seus moradores dentro dela (autossuficiência total);
- **100%** = nenhum morador da região se interna nela (dependência total de fora).

**Unidade de contagem:** cada internação é uma **AIH** — a Autorização de Internação
Hospitalar, o documento que o SUS emite a cada internação paga. É o registro oficial do
sistema; ver limitação (d) sobre o que isso implica.

**Regra de "dentro" e "fora":** comparamos a **região de saúde onde a pessoa mora** com a
**região de saúde onde fica o hospital**. Se forem diferentes, aquela internação conta como
"fora". Município vizinho, mas da mesma região de saúde, conta como **dentro** — o índice é
regional, não municipal (essa é justamente a diferença dele para a taxa de evasão municipal
de 50,5% do projeto).

## 3. Exemplo real, passo a passo — a 3ª Região de Saúde

A 3ª Região reúne municípios do brejo/agreste paraibano como Esperança, Lagoa Seca,
Alagoa Grande, Alagoa Nova, Areia e Remígio. Números de 2025, todos derivados da base
congelada do SIH (nenhum digitado à mão):

| Passo | O que é | Número |
|---|---|---|
| 1 | Internações de moradores da 3ª Região (o denominador) | **10.815** |
| 2 | Dessas, quantas aconteceram em hospitais da própria 3ª Região | 1.672 |
| 3 | Dessas, quantas aconteceram em hospitais de outra região (o numerador) | **9.143** |
| 4 | Conta: 100 × 9.143 ÷ 10.815 | **84,5%** |

Confere: 1.672 + 9.143 = 10.815 (todas as internações estão em um dos dois grupos).

**Para onde vão essas 9.143?** A maior parte tem um destino só: **7.639 foram para a 16ª
Região**, cujo polo é Campina Grande — sozinha, Campina Grande recebeu 7.407 internações
de moradores da 3ª Região no ano. Outras 693 foram para a 1ª Região (João Pessoa) e o
restante se espalha.

**Leitura em uma frase:** *de cada 100 internações de moradores da 3ª Região, cerca de 85
acontecem fora dela — e a maioria em Campina Grande. Na prática, a 3ª Região funciona como
área de captação do polo vizinho, não como uma região que interna a própria população.*

## 4. Como interpretar o número (linguagem do dia a dia)

Imagine uma região de saúde como um bairro que tem posto de saúde e hospital próprios.
O índice responde: **quantas vezes o morador precisou pegar a estrada e se internar no
"bairro do vizinho"?**

- Índice **baixo**: o hospital de casa dá conta. O morador se interna perto de onde vive.
- Índice **alto**: na maior parte das vezes, o morador precisa sair da sua região para ser
  internado — desloca família, gasta transporte, e o planejamento de leitos daquela região
  não está sustentando a própria população.

O índice **não é uma nota de qualidade** e **não diz que alguém fez algo errado**: parte do
deslocamento é esperada e até desejável (cirurgia complexa deve mesmo se concentrar em
hospital de referência). O que o índice mostra é **o tamanho e a direção do deslocamento** —
que é exatamente a informação que falta hoje para pactuar leitos entre regiões.

## 5. Faixas de interpretação (com corte justificado)

Os cortes **não são redondos por gosto** — cada um tem uma razão:

| Faixa | Intervalo | Por que este corte | O que significa |
|---|---|---|---|
| **Dependência baixa** | índice **< 26,4%** | 26,4% é a **média da própria Paraíba**: das 256.623 internações de moradores do estado, 67.633 (26,4%) aconteceram fora da região de residência. É a régua interna do dado, não um número inventado. | A região perde menos gente do que o estado perde em média. Tem capacidade instalada compatível com sua população, ou é ela própria um polo receptor. |
| **Dependência média** | **26,4% a 50%** | Fica entre a média estadual e a maioria simples. | A região resolve a maior parte dos casos, mas já exporta acima da média do estado — vale olhar para quais casos estão saindo. |
| **Dependência alta** | índice **> 50%** | 50% é o ponto em que **a maioria** das internações dos moradores acontece fora. É também o limiar da pergunta analítica PA-2 do projeto, definida antes de olhar os resultados (não foi escolhido depois para favorecer a conclusão). | A região **não** interna a maioria da própria população. Na prática, ela depende estruturalmente de outra região — é onde a pactuação (PPI) precisa ser explícita. |

Os dois cortes têm naturezas diferentes, e isso é proposital: um é **empírico** (a média do
próprio estado) e outro é **conceitual** (a fronteira da maioria). Nenhum depende de opinião
sobre "o que é muito".

## 6. Limitações — o que este número NÃO consegue dizer

**(a) A base só enxerga hospitais da Paraíba.**
Os arquivos do SIH são organizados pelo estado **do hospital**. Então um paraibano internado
em Recife ou Natal **não aparece** nesta base — ele está no arquivo de Pernambuco ou do Rio
Grande do Norte. **Como o índice trata isso:** essas internações ficam **fora da conta
inteira** — não entram no numerador nem no denominador. Consequência: **o índice publicado é
um piso**, ou seja, a dependência real é igual ou maior do que a mostrada, nunca menor.

**Qual é o tamanho desse efeito — o projeto mediu.** Baixamos também os registros de
Pernambuco, Rio Grande do Norte e Ceará de 2025 e separamos quem mora na Paraíba:
**3.682 internações**. Isso é **1,41%** de todas as internações de paraibanos no ano
(3.682 de 260.305, somando as de dentro e as de fora do estado). Ou seja: **a evasão da
Paraíba é quase toda dentro da própria Paraíba** — o buraco desta base é pequeno, e o
"piso" descrito acima está perto do número real.

Uma ressalva sobre *onde* esse 1,41% cai: parte dele é gente da divisa pegando o hospital
mais perto, que por acaso fica do outro lado da fronteira, e parte é gente que atravessou
o estado atrás de tratamento de alta complexidade. Os dois motivos existem — o principal
destino é Recife, mas o segundo é um hospital regional em Alexandria/RN, que atende o
sertão da divisa. **O projeto não crava a divisão entre esses dois grupos**, porque ela se
mostrou instável: dependendo da distância que se use para definir "fronteira", a proporção
muda muito. O que é estável, e sustenta a leitura, é que o grupo que viajou longe interna
por casos bem mais complexos e caros do que o grupo da divisa.

**(b) O índice mede deslocamento, não qualidade nem adequação clínica.**
Ele conta *quantas* internações saíram da região, não se elas *deveriam* ter saído. Um
transplante feito no hospital de referência conta igual a um parto que poderia ter sido
resolvido a 10 km de casa. Índice alto sinaliza **onde olhar**, não **quem errou**.

**(c) Região pequena tem número mais instável.**
As regiões variam muito de tamanho: a maior tem 81.574 internações no ano e a menor 4.277.
Onde o volume é pequeno, poucas dezenas de internações a mais ou a menos mexem no índice —
e um único hospital que fecha, abre ou fica meses sem faturar AIH pode deslocar o número.
Por isso a tabela sempre mostra o **volume ao lado do índice**: índice sem volume ao lado
convida a comparação injusta.

**(d) Cada linha é uma AIH, não uma pessoa.**
O SIH conta autorizações de internação, não pacientes únicos. Quem interna quatro vezes no
ano aparece quatro vezes; transferências entre hospitais podem gerar mais de uma AIH para
o mesmo episódio. O índice, portanto, mede **fluxo de internações**, não "% de moradores que
se deslocam". Corrigir isso exigiria ligar registros de um mesmo paciente — o que este
projeto decidiu não fazer, por ser dado sensível.

**(e) O local do hospital é o "município de movimentação" (MUNIC_MOV) do SIH.**
É o município do estabelecimento que registrou a internação. É a melhor aproximação
disponível do destino do paciente, mas é uma aproximação.

**(f) O recorte é o ano de 2025 inteiro.**
Sazonalidade e retificações de dezembro (o DATASUS ainda pode receber AIH atrasada) podem
mexer marginalmente nos números; nenhum mês foi excluído.

## 7. Fronteira do cálculo: quem tem índice e quem não tem

O índice é calculado para as **16 regiões de saúde da Paraíba** — 100% delas.

A matriz de fluxos do projeto tem ainda uma origem chamada **"Fora da PB"** (pessoas de
outros estados que vieram se internar na Paraíba). Essa origem **não recebe índice**, de
propósito: "quanto quem mora fora da Paraíba depende de fora da sua região" é uma pergunta
sem sentido nesta base, que não enxerga a rede de saúde dos outros estados. Ela continua
aparecendo na matriz O-D (é informação real e útil: mostra a PB como receptora), mas fica de
fora da tabela do índice.

---

## Roteiro de teste de leitura (opcional — não bloqueia mais)

> **Status:** a definição foi lida e aprovada pelo Augusto, e é com base nisso que a US-09
> está fechada. O teste formal com o Pedro **deixou de ser condição** para o fechamento
> (decisão de 24/07/2026, registrada em `docs/backlog.md`): o texto foi julgado legível
> como está, e segurar a story numa etapa humana assíncrona custava mais do que rendia.
>
> O roteiro abaixo continua aqui porque **continua útil** — se em algum momento o Pedro ler
> isto antes da apresentação, as respostas dele apontam exatamente onde o texto trava. Não é
> pendência; é ferramenta disponível.

Peça ao Pedro para ler as seções 1 a 5 **uma vez só** e então responder, sem consultar:

1. Com suas palavras, o que o número "84,5% na 3ª Região" quer dizer?
2. Se uma região tivesse índice **0%**, o que estaria acontecendo lá?
3. Índice alto significa que o hospital daquela região é ruim? (resposta esperada: não)
4. Por que o corte de "dependência alta" é 50% e não outro número qualquer?
5. Apontando a tabela do exemplo: de onde saiu o 9.143 e de onde saiu o 10.815?
6. Teve alguma palavra ou frase que você teve que reler para entender? Qual?
7. Se você fosse explicar isso para a sua mãe em 20 segundos, o que diria?

**Como usar o resultado:** qualquer pergunta em que ele hesitar aponta para um trecho a
reescrever — o alvo é entendimento em **uma leitura**, então "entendi depois de reler" conta
como falha do texto, não do leitor. Registrar aqui a data do teste e os ajustes feitos.

**Resultado do teste:** _não aplicado — ver status no topo desta seção._
