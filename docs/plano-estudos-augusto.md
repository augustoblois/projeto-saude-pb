# Plano de estudos — Augusto

> **Roteiro de estudo da metade "como o número nasce"**, dia a dia, até 07/08/2026.
> **2h/dia, de 28/07 a 06/08.** Nos três últimos dias, em dupla com o Pedro.
> Autocontido: não depende do plano mestre.
>
> A trilha do Pedro é [`plano-estudos-pedro.md`](plano-estudos-pedro.md); o cronograma
> conjunto e o banco de perguntas estão em [`plano-estudos.md`](plano-estudos.md).

---

## O que esta metade cobre, e por que é ela

Você absorve as perguntas de **método**: *"como você calculou isso?"*, *"esse dado é
confiável?"*, *"e se eu quiser rodar com dados de agosto?"*. O Pedro absorve as de
**significado**: *"e daí?"*, *"esse número não prova o contrário?"*.

A divisão é por **exposição**, não por habilidade: você acompanhou este pipeline sendo
construído, então aprofundar essa metade custa menos tempo pra você do que pra ele. No
**04/08** vocês trocam — você dá 30 min de aula da sua metade, sem consultar arquivo.

**Duas formas de rodar cada dia. Escolha por dia, não de uma vez:**

- **Modo solo:** abrir o arquivo, rodar, responder as âncoras de cabeça, conferir.
- **Modo pair:** me chamar, eu explico o arquivo do dia passo a passo e **você me
  interroga** até não sobrar buraco. Mesmo resultado, e mais rápido em dia denso (D3 e D5
  são os candidatos naturais).

O que **não** funciona é ler o notebook de cima a baixo achando que entendeu. O teste é
sempre o mesmo: fechar tudo e explicar em voz alta.

---

## Ritual de abertura (uma vez, antes do D1)

```powershell
cd C:\Users\augus\workspace\faculdade\analise-de-dados\projetos\projeto-saude
.venv\Scripts\Activate.ps1
jupyter notebook
```

Se o `.venv` não existir: `python -m venv .venv`, ativar, `pip install -r requirements.txt`.

---

## D1 · 28/07 — O chão comum (2h)

Os **7 fatos** que os dois precisam saber de cor. Não é resumo do projeto: é o mínimo
abaixo do qual nenhuma outra frase se sustenta.

1. **O que é o SIH.** Sistema de Informações Hospitalares do SUS — registra toda internação
   paga pelo SUS. Cada linha é **uma internação (uma AIH)**, não uma pessoa.
2. **O recorte.** 12 meses fechados de 2025, hospitais da PB. **258.125 internações.**
3. **As duas colunas que fazem o projeto existir.** `MUNIC_RES` (onde o paciente mora) e
   `MUNIC_MOV` (onde internou). Diferentes = evadiu.
4. **O achado central.** **50,5%** das internações acontecem fora do município de moradia.
5. **A unidade de planejamento.** 16 regiões de saúde na PB. Fora da **região** de
   residência: **67.633 = 26,4%**.
6. **O produto.** Matriz origem→destino + índice de dependência por região, em Streamlit.
   Não existe em painel público.
7. **O decisor.** Secretaria Estadual de Saúde da PB — regionalização e PPI (Programação
   Pactuada e Integrada: o instrumento formal de quem atende quem, e com que dinheiro).

**Depois (~1h):** abrir o painel (`streamlit run app.py`) e percorrer as 5 abas **como
avaliador**, não como autor. Anote tudo que você não saberia explicar se perguntassem ali
na hora — essa lista vira sua pauta pessoal para D5 e D6.

**Fecho (~15 min):** cobrança mútua dos 7 fatos com o Pedro, por chamada.

---

## D2 · 29/07 — De onde vêm os dados (congelamento e tratamento)

**Abrir:** `src/congelar_sih.py` (74 linhas) · `src/congelar_sih_vizinhos.py` ·
`notebooks/01-tratamento-base.ipynb` (§1 a §8) · `docs/dicionario-dados.md`

### O que entender

**A cadeia de formatos: FTP → `.dbc` → `.dbf` → DataFrame → parquet.** O DATASUS publica em
`.dbc`, um formato comprimido antigo que o pandas não lê. `dbc2dbf` descomprime para `.dbf`
(formato de tabela dos anos 80), aí `read_dbf_fast` vira DataFrame, e aí salva em
**parquet** — formato colunar, comprimido, que preserva os tipos. O `.dbc`/`.dbf` fica fora
do git; o parquet entra. Nome do arquivo no FTP: `RDPB2501.dbc` = **R**eduzida **D**a AIH,
**PB**, ano **25**, mês **01**.

**Idempotência (linha 21).** `faltantes = [m for m in MESES if not (...).exists()]` — mês
que já tem parquet é pulado. Rodar de novo não rebaixa nada, só completa buraco. É por isso
que o README pode dizer "opcional, pode rodar à vontade".

**A validação na porta de entrada (linhas 52-56).** Antes de salvar, o script confere que
`MUNIC_RES` e `MUNIC_MOV` existem e não têm nulo. Se falhar, **retorna erro em vez de
salvar**. O ponto: essas duas colunas são o projeto inteiro — um parquet salvo com nulo ali
contaminaria tudo a jusante silenciosamente.

**Falha isolada (linha 68).** O `try/except` dentro do loop faz o erro de um mês não
derrubar os outros 11. No fim sai um placar mês a mês.

**Por que FTP direto e não a API de conveniência do PySUS:** instabilidade. Registrado na
wiki; o `src/congelar_sih.py` é o fluxo que ficou validado.

**A pegadinha dos 6 vs 7 dígitos** (`01-tratamento-base` §5): o código IBGE de município tem
7 dígitos, mas o SIH grava só 6 — o último é dígito verificador e foi cortado. Sem tratar,
o join com a tabela do IBGE dá **zero** correspondência. A solução da §5 é reaproveitada
depois na PA-3 (populações).

**O dicionário de dados:** 118 colunas auditadas, ~46 usáveis / ~72 descartadas. A maioria
das descartadas é campo do layout **nacional** que vem vazio no recorte da PB. A lição:
documentação oficial ≠ realidade do dado. Usar coluna sem checar conteúdo real é o jeito
clássico de construir análise sobre areia.

**Os arquivos do SIH são organizados pela UF do hospital** — paraibano internado em Recife
está no arquivo de **PE**. É por isso que existe o `congelar_sih_vizinhos.py`: baixa PE/RN/CE
(~1,9 mi de internações), filtra residentes da PB, congela **3.682**.

### Âncoras (responder de cabeça, depois conferir)
1. Por que os `.dbc` não estão no git e os parquets estão?
2. O que garante que a base tratada é fiel à congelada? (duas validações)
3. Por que o join com a tabela do IBGE quebraria sem a §5?
4. Se o DATASUS republicar março corrigido, o que preciso fazer para reprocessar?

---

## D3 · 30/07 — Região de saúde e a matriz O-D (o dia mais importante)

**Abrir:** `notebooks/01-regiao-saude.ipynb` (§1 a §7) · `notebooks/01-matriz-od.ipynb`
(**§4 é obrigatória**) · `src/baixar_base_territorial.py`

### O que entender

**De onde vem a relação município→região.** Base territorial oficial do DATASUS
(`base_territorial_out25.zip`, congelada em `data/raw/`) — a mesma que o TabWin do
Ministério usa. Não é lista que a gente montou: é a divisão oficial. As validações do §3 e
§6: 223 municípios cobertos, **1 região cada** (nenhum em duas), zero linha perdida, zero
nulo. Residentes de outros estados (1.502 internações) marcados "Fora da PB".

**O que a matriz O-D é, concretamente.** Duas tabelas agregadas:
`(município_res × município_int × mês)` e `(região_res × região_int × mês)`, com contagem,
flag de evasão e taxas. **Agregar** aqui significa: trocar 258 mil linhas por algumas
milhares de linhas somadas. Tudo a jusante — as 6 análises, o índice, o painel — consome
essa matriz, **nunca** a base linha a linha. É essa decisão que faz o painel abrir em 6,4s.

**§3 — a validação que prova que a agregação não mentiu:** a soma das contagens da matriz
tem que bater com o total de internações. Se a matriz perdesse ou duplicasse linha, ela
bate aqui e em nenhum outro lugar.

**§4 — a investigação do 47,8% vs 49,8%. Estude esta seção como se fosse prova.**
O PRD nasceu citando 47,8% de evasão em jan/2025, número herdado da fase de pesquisa, sem
memória de cálculo. Ao refazer com a base congelada: **49,8%**. Foram testadas **cinco
variantes** de cálculo, incluindo a pegadinha do **`UF_ZI`** — coluna que parece ser "UF do
paciente" mas é a **UF gestora da AIH** (quem administra o recurso), o que muda o
denominador se usada por engano. Nenhuma variante reproduz 47,8%. Decisão: **adotar o
número que se consegue provar** e corrigir PRD, briefing e backlog.

Por que isso é a sua melhor arma no dia 07/08: se perguntarem *"como sei que seu número
está certo?"*, a resposta não é "conferi" — é *"o número que herdamos não sobreviveu à
verificação, e trocamos por um que sobrevive a cinco caminhos independentes"*. Isso é a
diferença entre confiar num número e ter direito a ele.

**Números que saem daqui:** ano fechado, evasão municipal **50,5%**; extremos regionais
1,8% (região de JP) e 84,5% (3ª Região); maior fluxo **Santa Rita→João Pessoa, 5.645**.

### Âncoras
1. O que é `UF_ZI` e por que ela é armadilha?
2. Por que o número do PRD mudou — e por que isso é força, não fraqueza?
3. O que a validação da §3 pegaria que a §4 não pega?
4. Por que a matriz é agregada e não a base inteira?

---

## D4 · 31/07 — O índice de dependência

**Abrir:** `docs/definicao-indice-dependencia.md` (198 linhas, inteiro) ·
`notebooks/01-indice-dependencia.ipynb` (§2 a §5 e §8)

### O que entender

**A definição:** para cada região, o **percentual das internações dos moradores daquela
região que aconteceu fora dela**. Simples de dizer, e a simplicidade é proposital — é o
número-assinatura do projeto e precisa caber numa frase dita a um gestor.

**As 3 validações independentes** (§2, §3, §4 — respectivamente Caminhos A, B e C):
- **A** — a partir da matriz regional já pronta;
- **B** — a partir da matriz **municipal**, remapeando município→região **do zero**;
- **C** — direto da base, **AIH por AIH**, sem nenhuma agregação intermediária.

§5 compara os três entre si e contra o CSV pré-existente: **delta 0,0** nos três pares, com
`assert` (instrução que **derruba a execução** se a condição falhar — é validação que não
dá para ignorar sem querer).

**Por que 3 caminhos e não 1:** um número que ninguém mais publica não tem comparação
externa possível. Não dá para conferir contra o TabNet, porque o TabNet não tem esse
número. A única defesa disponível é **consistência interna por caminhos que não
compartilham etapa** — se os três erram igual, o erro está na base, não no cálculo.

**§8 — o veredito da hipótese PA-2.** A hipótese ("pelo menos ⅓ das regiões acima de 50%")
foi **registrada no PRD antes do cálculo**. Resultado: 8 de 16. Isso é o que separa
hipótese testada de garimpo de resultado — e é defensável exatamente porque a ordem está
documentada.

**Extremos:** 3ª Região 84,5%; 1ª (JP) 1,8%; 16ª (CG) 4,1%. Taxa do estado: 26,4%.

**Limitação (c), que você precisa saber dizer antes de perguntarem:** região com pouco
volume tem índice instável — por isso o painel **nunca** mostra o índice sem o volume ao
lado.

### Âncoras
1. Explique o índice para alguém de fora, em 2 frases, sem usar "percentual".
2. Por que três caminhos, e o que um erro comum aos três significaria?
3. Por que a 1ª Região tem 1,8%?
4. O que é um `assert` e por que ele é melhor que um `print` de conferência?

---

## D5 · 01/08 — O painel, parte 1 (arquitetura + Matriz + Mapa)

**Abrir:** `app.py` — linhas 95-230 (carga e helpers), `aba_matriz()` (233), e o bloco do
mapa (308-660). **1.202 linhas no total; não leia tudo.** Leia essas faixas entendendo, e
passe o olho no resto.

### O que entender

**A arquitetura que garante a demo: notebook calcula, painel só exibe.** O app lê tabelas
já somadas e **nunca** recalcula as 258 mil linhas durante a interação. Qualquer conta
pesada feita ao vivo seria risco na apresentação. Abre em 6,4s, filtro responde em
milissegundos.

**`@st.cache_data`.** O Streamlit reexecuta o script inteiro a cada clique — é o modelo de
execução dele. Sem cache, cada clique releria o parquet do disco. O decorador guarda o
resultado da primeira chamada e devolve o mesmo objeto nas seguintes. É por isso que quase
toda função `carregar_*` tem ele.

**`filtrar()` é função pura** (linha 206): não lê arquivo, não desenha nada — recebe
DataFrame e devolve DataFrame. Por isso o script de verificação consegue exercitar
exatamente o mesmo código que o painel usa. Função pura é a que dá para testar.

**`mil()` e `pct()` (215, 221)** existem por causa de um bug real: em Python, **literais de
string adjacentes viram um objeto só** antes de qualquer método. Um `.replace(".", ",")`
escrito para formatar decimal comeu o **ponto final da frase anterior**. A correção foi
isolar formatação em dois helpers que nunca encostam em texto.

**O bug do mapa — a melhor história técnica do projeto (Etapa 16).** O mapa passou em
**todos** os testes automáticos (números certos, coordenadas certas, tempo ótimo, zero
exceção) e renderizava um bloco sólido na tela. Causa: o GeoJSON do IBGE lista os pontos de
cada polígono no sentido **anti-horário** (o padrão do formato), mas o Plotly interpreta
polígonos **sobre a esfera**, onde esse sentido significa "todo o globo **menos** este
município". Corrigido no congelamento do arquivo, com validação automática que reprova se
alguém regravar no sentido errado.
**A lição, que vale como frase de apresentação:** teste automático confirma que o código
roda, não que o desenho está certo. Só abrir no navegador pega isso.

**A decisão de cor do mapa.** O plano era colorir por taxa de evasão. O dado matou a ideia:
a **mediana da evasão municipal é 100%** e 173 dos 223 municípios passam de 90% — o mapa
virava um bloco de uma cor só. Trocamos para **destino principal de cada município**, e
apareceram os **territórios**: Campina Grande 62 municípios, João Pessoa 48, Patos 30.
Continua sendo coroplético (mapa colorido por área), então o guard-rail do backlog foi
respeitado.

### Âncoras
1. Por que o painel não recalcula nada ao vivo?
2. O que acontece se eu tirar `@st.cache_data` de `carregar_matriz_municipal`?
3. Por que a cor do mapa mudou de evasão para destino principal?
4. Como um mapa errado passa em todos os testes?

---

## D6 · 02/08 — O painel, parte 2 (Índice, Achados, Sobre os dados)

**Abrir:** `app.py` — 663-826 (índice), 829-1056 (achados), e o bloco final.

### O que entender

**Texto lido do `.md` em runtime, não copiado para o código.** `carregar_definicao()` lê
`docs/definicao-indice-dependencia.md`; `carregar_narrativa()` lê
`reports/narrativa-executiva.md`. Duas cópias divergiriam no primeiro ajuste de redação — e
o texto vai ser revisado até 06/08. Consequência prática que você precisa saber dizer: **se
corrigirmos a narrativa 1h antes de apresentar, o painel já mostra a correção.**

**Nenhum número da tela é digitado.** A média estadual (26,4%) vem da soma das colunas; o
"8 das 16" vem da contagem da coluna de faixa; o destino principal é agregado da matriz na
hora da consulta. Prova de que fecha: para a 3ª Região o painel devolve *16ª Região / 7.639*
— exatamente o número que o texto da definição traz no exemplo.

**O índice nunca aparece sem o volume ao lado** — imposto pela limitação (c). Comparar
índices sem o tamanho leva a conclusão injusta com região pequena.

**O segundo bug da Etapa 17:** uma variável local chamada `pct` **sombreou** a função `pct`
→ `UnboundLocalError`. Só aparecia depois de trocar a região no seletor, então a primeira
execução passava limpa. Em Python, o nome dentro da função vence o de fora — e o erro só
estoura no caminho que usa a função depois de a variável ter sido criada.
**Lição irmã da do mapa:** conferir número não é conferir frase. Os dois defeitos só
apareceram porque alguém **leu a tela renderizada**.

**Aba "Sobre os dados"** (Etapa 23): proveniência, por que funciona offline, a ressalva de
dezembro, tempo de atualização. Ela existe para responder *"de onde saiu esse dado?"* sem o
Pedro precisar decorar nada — é só ler do painel. Saiba que ela está lá e o que tem nela.

### Âncoras
1. Por que os textos são lidos em runtime em vez de copiados?
2. Como o painel garante que nenhum número foi digitado à mão?
3. Por que o `UnboundLocalError` não aparecia na primeira execução?
4. Onde no painel eu mando o avaliador olhar se ele questionar a fonte?

---

## D7 · 03/08 — Reprodutibilidade e as armadilhas de número

**Abrir:** `docs/atualizacao-mensal.md` · `README.md` · `requirements.txt` ·
`src/conferir_narrativa.py`

### O que entender

**A ordem dos notebooks importa e é silenciosa.** `01-pa6-perfil-demanda` consome o
resultado de `01-indice-dependencia`. Rodar fora de ordem **não dá erro** — dá resultado
errado. Esse é o tipo de bug que ninguém vê, e é por isso que a ordem está escrita em
`docs/atualizacao-mensal.md` em vez de ficar na cabeça de alguém.

**Retificações de dezembro:** o DATASUS corrige competências passadas retroativamente.
Reprocessar em 2027 pode dar números levemente diferentes. Isso é característica da fonte,
não defeito do projeto — mas precisa ser dito antes de perguntarem.

**`requirements.txt` com `==`:** versão fixada, não faixa. Instalar daqui a 6 meses entrega
exatamente o que foi testado.

**`src/conferir_narrativa.py`** recalcula da base os 3 blocos de números que não têm
notebook próprio (evasão só de residentes PB, taxa estadual, destinos das 8 regiões mais
dependentes). Existe porque **nenhum número da apresentação pode estar digitado à mão**.

**A história da US-18, que vale contar no dia (Etapa 22).** A story foi **reprovada na
primeira revisão**: um notebook buscava a base territorial no site do Ministério em vez de
usar cópia local. São 1,6 MB, tudo funcionava — e violava a regra nº 1 do projeto (nada
depende de fonte viva). Correção: arquivo congelado no repo e **os 9 notebooks reexecutados
com a internet desligada de propósito**. Todos rodaram até o fim.

### As armadilhas de número — os dois decoram

| Armadilha | A verdade |
|---|---|
| **50,5% vs 50,2%** | Ambos certos. 50,5% = todas as internações na PB (inclui não-residentes). 50,2% = só residentes PB. Falou "paraibanos"? É 50,2%. |
| **26,4% é taxa estadual, não média das 16** | Pesa pelo volume; não é a soma dos índices dividida por 16. |
| **47,8% vs 49,8%** | 47,8% veio da pesquisa, sem memória de cálculo. 5 caminhos dão 49,8%. Adotamos o que se prova. |
| **161 cidades com 100% de evasão** | 223 − 62. Não perdem pacientes: **não têm leito SUS**. Ali "evasão" mede se a cidade tem hospital. |
| **A fração fronteira × interior** | **Frágil** — varia de 11,5% a 58,5% conforme o corte e chega a inverter. Nunca cravar. Estável é a **razão** de alta complexidade: 1,7× a 2,8×, em todos os cortes. |
| **Mortalidade 29,4% vs 24,7%** | Não prova nada. Só é transferido quem está estável o bastante para o transporte. Observacional, confundido por gravidade. |
| **14,7% "não classificado"** | Declarado de propósito, não forçado numa caixa para melhorar o resultado. |
| **Trocar de município ≠ distância** | Bayeux e Santa Rita evadem muito porque são coladas em JP — atravessa-se uma avenida. |

---

## D8 · 04/08 — Handoff cruzado (junto, 2h)

- **30 min:** você dá aula da sua metade — de onde vêm os dados, como as contas foram
  feitas e conferidas, como o painel funciona. **Sem consultar arquivo.**
- **30 min:** o Pedro dá aula da metade dele — 7 achados, 5 recomendações, 9 limitações.
- **60 min:** perguntas cruzadas do banco (`plano-estudos.md` §7). Cada um responde 3
  perguntas **da metade do outro**.

O que você não conseguir explicar aqui é exatamente o que você ainda não sabe. Ainda dá
tempo de voltar no arquivo; em 06/08 não dá.

---

## D9 · 05/08 — Ensaio 1 (junto, ~1h)

Apresentação inteira, corrida, cronometrada. O Pedro apresenta; **você assiste sem
interromper** e anota. Só no fim vocês conversam.

Combinar antes: quem fala qual parte, e a regra para pergunta que cai na metade do outro —
**o dono responde, o outro completa se travar**. Sem atropelo.

---

## D10 · 06/08 — Ensaio 2 e fechamento (junto, ~1h)

Só o que saiu torto no D9 + banco de perguntas. **Não estude nada novo neste dia.**

**Você está pronto se conseguir, sem consultar nada:**
1. Recitar os 7 fatos da Camada 0.
2. Explicar o índice de dependência para alguém de fora, em 2 frases.
3. Contar a cadeia completa do dado: FTP → `.dbc` → parquet → base tratada → região →
   matriz O-D → índice → painel, dizendo o que cada etapa valida.
4. Contar a investigação do 47,8% → 49,8% de cabeça.
5. Citar 3 armadilhas de número e a frase errada que cada uma derruba.
6. Responder 3 perguntas da metade do Pedro.

O item 6 é o que prova que a cobertura ficou igual. Se falhar, o handoff do D8 não pegou —
repetir a aula do tópico que falhou.

---

## Glossário mínimo (para responder sem hesitar se a banca perguntar o termo)

| Termo | Em uma frase |
|---|---|
| **AIH** | Autorização de Internação Hospitalar — o documento que registra uma internação no SUS. Uma linha da base = uma AIH. |
| **SIH** | Sistema de Informações Hospitalares do SUS, onde as AIH ficam. |
| **`.dbc` / `.dbf`** | Formatos legados do DATASUS: `.dbc` é comprimido, `.dbf` é a tabela descomprimida. |
| **parquet** | Formato de arquivo colunar e comprimido; guarda os tipos das colunas e lê rápido. |
| **FTP** | Protocolo de transferência de arquivos — como o DATASUS publica os dados. |
| **agregação** | Trocar linhas individuais por linhas somadas por grupo (ex.: 258 mil internações → contagem por origem×destino×mês). |
| **join** | Casar duas tabelas por uma coluna em comum (ex.: código IBGE → nome do município). |
| **função pura** | Função que só depende dos argumentos e não mexe em nada fora — por isso é testável. |
| **`assert`** | Instrução que derruba a execução se a condição for falsa; validação que não dá para ignorar sem querer. |
| **idempotente** | Rodar de novo não muda o resultado nem refaz o que já está pronto. |
| **cache** | Guardar o resultado de uma operação cara para não repetir (`@st.cache_data`). |
| **GeoJSON** | Formato que descreve fronteiras geográficas como listas de pontos. |
| **coroplético** | Mapa que colore áreas inteiras conforme um valor. |
| **PPI** | Programação Pactuada e Integrada — o instrumento formal de quem atende quem no SUS, e com que dinheiro. |
| **PySUS** | Biblioteca Python de acesso a dados do DATASUS; usamos o cliente FTP dela, não a API de conveniência. |
