"""Camada de apresentação do painel — tokens, tipografia e componentes visuais.

Existe separado do `app.py` por um motivo prático: `app.py` já carrega, filtra e agrega
dados; se ele também carregasse o HTML de cada bloco, cada aba viraria uma mistura de
`groupby` com `<div>`. Aqui ficam só as peças de tela, e as abas passam a montar a
interface chamando funções com nome de coisa ("faixa de indicadores", "achado central")
em vez de repetir marcação.

A direção visual: relatório de campo, não dashboard
---------------------------------------------------
Este painel é a peça pública de um trabalho acadêmico sobre saúde pública, e a linguagem
visual é deliberadamente a de um **documento técnico impresso** — papel, tinta, réguas,
seções numeradas, números em monoespaçada — e não a de um painel de BI.

A escolha não é decorativa. Um mapa temático de secretaria de saúde é lido em papel há
décadas, e essa é a convenção visual que o destinatário do trabalho já sabe ler. Além
disso, o repertório oposto (fundo escuro azul-marinho, acento ciano, cartões arredondados
com sombra, degradê ciano→roxo nos números) é hoje o visual padrão de qualquer interface
gerada automaticamente — usá-lo faria um trabalho autoral parecer um template.

Daí as regras que valem para todo este arquivo:

- **Uma cor de acento, e só uma.** O óxido `#A8341E` marca o que exige atenção. Quando
  tudo é colorido, nada é destaque, e a cor deixa de significar.
- **Cantos vivos, zero sombra.** Régua de 1px separa; caixa flutuante com sombra é
  vocabulário de aplicativo, não de documento.
- **Hierarquia por tamanho e peso, nunca por CAIXA-ALTA.** Rótulo em versalete espalhado
  pela tela é muleta: se o texto precisa gritar para ser encontrado, a escala está errada.
- **Número é dado, e dado se lê em monoespaçada.** Além do ar de instrumento de medição,
  a largura fixa impede que a linha "pule" quando o filtro muda o valor.

Duas restrições técnicas que valem para tudo:

1. **Nada é buscado na rede.** As fontes IBM Plex (licença OFL) estão dentro do projeto,
   em `static/fontes/`, servidas pelo próprio Streamlit — nada de Google Fonts, nada de
   CDN. O painel precisa abrir com a internet desligada (regra nº 1 do projeto).
2. **Nenhum número é escrito à mão.** Este módulo só sabe *desenhar* — quem calcula é o
   `app.py`, a partir das pré-agregações.
"""

from __future__ import annotations

import re

import streamlit as st

# --------------------------------------------------------------------------- #
# Tokens — a paleta inteira do painel em um lugar só.
#
# Está duplicada com `.streamlit/config.toml` de propósito: o config é lido pelo
# Streamlit para pintar os widgets nativos (input, tabela, slider), e este módulo é
# lido pelo nosso CSS e pelos gráficos Plotly. São dois consumidores diferentes do mesmo
# valor — mudar a cor exige tocar nos dois, e o comentário no config avisa disso.
#
# Os neutros têm temperatura: nenhum é cinza puro (saturação zero é o cinza de sistema,
# que não pertence a lugar nenhum). Todos puxam levemente para o quente, como papel.
# --------------------------------------------------------------------------- #
PAPEL = "#F4F3EE"          # fundo da página: papel, não branco de tela
PAPEL_FUNDO = "#EAE8E0"    # faixa recuada — mais ESCURA que o fundo, como no impresso
PAPEL_ALTO = "#FBFAF7"     # única superfície mais clara que o papel: a tabela

TINTA = "#14140F"          # texto principal — quase preto, levemente quente
TINTA_SUAVE = "#4A4A42"    # texto corrido secundário
TINTA_FRACA = "#6E6D63"    # notas, legendas, eixo de gráfico

REGUA = "#D4D1C6"          # a linha de 1px que separa tudo neste painel
REGUA_FORTE = "#A8A497"    # régua de ênfase e contorno de gráfico

OXIDO = "#A8341E"          # O acento. Único. Marca o que exige atenção.
OXIDO_FRACO = "#EFE0DA"    # fundo translúcido do óxido, para faixas de destaque

# Faixas do índice de dependência. Terrosas de propósito: é a convenção de mapa temático
# impresso, e o vermelho da faixa "alta" é o MESMO óxido do acento — quem depende demais
# é exatamente o que o painel quer que o gestor veja primeiro.
# O ocre é o mais escuro que um amarelo-terra pode ser sem virar marrom: em #A87A22, a
# tonalidade "certa" para a faixa média, o contraste sobre o papel dava 3,45:1 e reprovava
# em WCAG AA para texto. Escurecido até 4,67:1.
VERDE = "#4C6B47"
OCRE = "#8F651B"

# Sequência para gráficos categóricos sem significado fixo (áreas de captação, polos).
# Montada à mão a partir da convenção de atlas temático: terras, minerais e tintas, todas
# escuras o bastante para ler sobre papel e distinguíveis entre si sem depender de matiz
# pura — o daltonismo de vermelho/verde não colapsa esta sequência.
PALETA_CATEGORICA = [
    "#A8341E",  # óxido
    "#2F5D6B",  # azul-petróleo
    "#6B7A34",  # oliva
    "#8F651B",  # ocre
    "#7A3550",  # vinho
    "#37614B",  # verde-mata
    "#C4703F",  # terracota
    "#3F4A78",  # índigo
    "#7A6A55",  # barro
    "#5E6B72",  # ardósia
]


# --------------------------------------------------------------------------- #
# Utilitário de render
# --------------------------------------------------------------------------- #
def _limpar(html: str) -> str:
    """Colapsa a indentação do HTML antes de mandar para o Streamlit.

    Necessário, não cosmético: o Streamlit passa a string por um parser de Markdown
    antes de renderizar, e Markdown trata linha indentada com 4 espaços como bloco de
    código. Sem esta limpeza, um `<div>` bonitinho no editor vira código literal na tela.
    """
    return re.sub(r"\n\s*", "", html).strip()


def escrever(html: str) -> None:
    """Renderiza um bloco de HTML já montado pelos componentes deste módulo."""
    st.markdown(_limpar(html), unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# CSS global
# --------------------------------------------------------------------------- #
def injetar_estilo() -> None:
    """Injeta a folha de estilo do painel. Chamar uma vez, no início do `main()`.

    Faz três coisas diferentes:
    1. Carrega as fontes do próprio projeto (`static/fontes/`, servidas pelo Streamlit
       com `enableStaticServing`), sem tocar na rede.
    2. Corrige os widgets NATIVOS do Streamlit (abas, inputs, tabela, expander), que vêm
       com uma hierarquia visual muito plana por padrão.
    3. Define as classes dos componentes próprios deste módulo (`ui-faixa`, `ui-nota`…).

    Sobre a especificidade dos seletores: as classes deste módulo são sempre escritas
    aninhadas (`.ui-central .ui-central-frase`) e não soltas. O Streamlit estiliza o
    texto dentro do container de markdown com seletores de dois níveis, que venceriam
    uma classe única — foi por isso que a frase do achado central aparecia em corpo de
    texto normal apesar de ter tamanho declarado. Aninhar resolve pela raiz.
    """
    st.markdown(
        f"""<style>
/* ---------- Fontes do projeto (nada vem da rede) ---------- */
/* IBM Plex Sans é fonte VARIÁVEL: um arquivo só cobre de 100 a 700, então declarar a
   faixa em `font-weight` evita baixar um arquivo por peso. */
@font-face {{
  font-family: 'Plex Sans';
  src: url('app/static/fontes/ibm-plex-sans-latin.woff2') format('woff2');
  font-weight: 100 700;
  font-style: normal;
  font-display: swap;
}}
@font-face {{
  font-family: 'Plex Mono';
  src: url('app/static/fontes/ibm-plex-mono-400-latin.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}}
@font-face {{
  font-family: 'Plex Mono';
  src: url('app/static/fontes/ibm-plex-mono-500-latin.woff2') format('woff2');
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}}

/* ---------- Base ---------- */
/* Escala tipográfica com SALTO, não progressão suave: 13 → 15 → 19 → 27 → 46 → 76.
   Uma escala linear (o padrão) produz títulos que mal se distinguem do corpo, e é o que
   obriga a recorrer a CAIXA-ALTA para criar hierarquia. Com salto, o tamanho basta. */
:root {{
  --passo-0: 0.8125rem;  /* 13px — nota, legenda, rótulo de eixo */
  --passo-1: 0.9375rem;  /* 15px — corpo */
  --passo-2: 1.1875rem;  /* 19px — título de bloco */
  --passo-3: 1.6875rem;  /* 27px — título de seção */
  --passo-4: 2.875rem;   /* 46px — indicador */
  --passo-5: 4.75rem;    /* 76px — o número do achado central */
  --sans: 'Plex Sans', 'Segoe UI', system-ui, sans-serif;
  --mono: 'Plex Mono', 'Cascadia Mono', Consolas, monospace;
}}

html, body, .stApp, [class*="st-"], button, input, select, textarea {{
  font-family: var(--sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

.stApp {{ background: {PAPEL}; }}

.stMainBlockContainer, [data-testid="stMainBlockContainer"] {{
  padding-top: 2rem;
  padding-bottom: 6rem;
  /* 1100px em vez dos 1180 de antes: a diferença é pequena no olho e grande na intenção
     — largura de coluna de relatório, escolhida, não o container padrão. */
  max-width: 1100px;
}}

[data-testid="stHeader"] {{ background: transparent; }}

/* A família precisa ser repetida nos títulos, e com o container no seletor: o Streamlit
   declara a fonte dele em `[data-testid="stMarkdownContainer"] h1`, que tem
   especificidade maior que um `h1` solto e vence mesmo vindo antes. Sem isto, o título
   da capa sai em Source Sans (a fonte do Streamlit) e o resto da página em Plex — o que
   é pior do que não ter trocado fonte nenhuma. */
.stApp :is(h1, h2, h3, h4),
[data-testid="stMarkdownContainer"] :is(h1, h2, h3, h4) {{
  font-family: var(--sans);
  text-wrap: balance; letter-spacing: -0.015em; color: {TINTA};
}}
p, li {{ text-wrap: pretty; }}

/* Todo número do painel é monoespaçado e de largura fixa. `tabular-nums` impede que a
   linha mude de largura quando o filtro troca o valor exibido. */
.ui-num {{ font-family: var(--mono); font-variant-numeric: tabular-nums; }}

/* ---------- Abas ---------- */
/* Sem pílula, sem fundo, sem raio: as abas viram os separadores de um sumário, marcados
   por uma régua contínua. A aba ativa é a única com tinta cheia e régua grossa. */
.stTabs [data-baseweb="tab-list"] {{
  gap: 1.75rem;
  border-bottom: 1px solid {REGUA};
  background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
  height: 44px;
  padding: 0;
  color: {TINTA_FRACA};
  font-size: var(--passo-1);
  font-weight: 400;
  border-radius: 0;
  transition-property: color;
  transition-duration: 120ms;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {TINTA}; background: transparent; }}
.stTabs [aria-selected="true"] {{ color: {TINTA} !important; font-weight: 600; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {OXIDO}; height: 2px; }}
.stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* ---------- Inputs ---------- */
/* Rótulo em monoespaçada minúscula no lugar do versalete espalhado: continua distinto do
   corpo do texto, mas por FAMÍLIA, não por caixa. */
.stSelectbox label, .stRadio label, .stSlider label, .stMultiSelect label {{
  font-family: var(--mono) !important;
  font-size: var(--passo-0) !important;
  font-weight: 400 !important;
  color: {TINTA_FRACA} !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
}}
[data-baseweb="select"] > div {{
  background: {PAPEL_ALTO} !important;
  border-color: {REGUA_FORTE} !important;
  border-radius: 0 !important;
  transition-property: border-color;
  transition-duration: 120ms;
}}
[data-baseweb="select"] > div:hover {{ border-color: {TINTA} !important; }}
.stRadio [role="radiogroup"] label p {{ font-family: var(--sans); font-size: var(--passo-1); }}

/* O valor que flutua sobre o cursor do slider e os limites nas pontas: em monoespaçada,
   porque são números, e `nowrap` porque a caixa que o Streamlit reserva foi dimensionada
   para a fonte dele — mais estreita — e "25" quebrava em duas linhas, virando um "2"
   sobre um "5". */
[data-testid="stThumbValue"],
[data-testid="stSliderTickBarMin"],
[data-testid="stSliderTickBarMax"] {{
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  color: {TINTA_FRACA};
}}
[data-testid="stThumbValue"] {{ color: {OXIDO}; }}

/* ---------- Tabela ---------- */
/* Régua seca no lugar das três sombras empilhadas: em papel, uma tabela é delimitada por
   um fio, não por profundidade. */
[data-testid="stDataFrame"] {{
  border-radius: 0;
  border: 1px solid {REGUA_FORTE};
  box-shadow: none;
}}

/* ---------- Expander ---------- */
[data-testid="stExpander"] {{
  border: none;
  border-top: 1px solid {REGUA};
  border-radius: 0;
  background: transparent;
}}
[data-testid="stExpander"] summary {{
  font-size: var(--passo-1);
  font-weight: 500;
  padding-left: 0;
  transition-property: color;
  transition-duration: 120ms;
}}
[data-testid="stExpander"] summary:hover {{ background: transparent; color: {OXIDO}; }}

/* Régua: a `---` do Streamlit vem como linha cinza de ponta a ponta. Aqui ela é o
   elemento estrutural do documento, então fica seca e some — sem degradê. */
hr {{
  border: none;
  height: 1px;
  background: {REGUA};
  margin: 3.5rem 0 2.25rem;
}}

/* ================= Componentes próprios ================= */

/* ---------- Capa ---------- */
/* Alinhada à ESQUERDA, não centralizada: um documento começa na margem. O bloco de
   procedência vai para a direita, criando a única assimetria fixa da página. */
.ui-capa {{
  border-top: 3px solid {TINTA};
  padding: 1.5rem 0 2rem;
  margin-bottom: 0.5rem;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 2rem;
  align-items: start;
}}
.ui-capa h1 {{
  font-size: clamp(2rem, 4.4vw, 3.25rem);
  font-weight: 600;
  line-height: 1.06;
  margin: 0 0 1rem;
  max-width: 24ch;
}}
/* O destaque do título é COR SÓLIDA, não degradê. Degradê em texto é a assinatura mais
   reconhecível de interface gerada automaticamente, e uma cor chapada destaca igual.
   `block` força a quebra ANTES do destaque: deixar o navegador escolher onde quebrar
   partia a frase no meio ("…vai quando / precisa internar"), e as duas metades do título
   são duas ideias — para onde, e quando. */
.ui-capa h1 em {{ font-style: normal; color: {OXIDO}; display: block; }}
.ui-capa p {{
  font-size: 1.0625rem;
  color: {TINTA_SUAVE};
  max-width: 58ch;
  margin: 0;
  line-height: 1.6;
}}
.ui-capa-procedencia {{
  font-family: var(--mono);
  font-size: var(--passo-0);
  color: {TINTA_FRACA};
  line-height: 1.7;
  text-align: right;
  border-right: 2px solid {OXIDO};
  padding-right: 0.875rem;
  white-space: nowrap;
}}
@media (max-width: 820px) {{
  .ui-capa {{ grid-template-columns: 1fr; }}
  .ui-capa-procedencia {{
    text-align: left; border-right: none;
    border-left: 2px solid {OXIDO}; padding: 0 0 0 0.875rem;
  }}
}}

/* ---------- Cabeçalho de seção ---------- */
/* Sem ícone dentro de quadradinho arredondado: o número da seção faz o mesmo trabalho de
   ancorar o olho, e ainda diz em que ponto do documento a pessoa está. */
.ui-secao {{ margin: 0 0 1.25rem; }}
.ui-secao-topo {{
  display: flex; align-items: baseline; gap: 0.875rem;
  border-bottom: 1px solid {REGUA};
  padding-bottom: 0.5rem;
  margin-bottom: 0.875rem;
}}
.ui-secao-numero {{
  font-family: var(--mono);
  font-size: var(--passo-2);
  font-weight: 500;
  color: {OXIDO};
  flex: 0 0 auto;
}}
.ui-secao h2 {{
  font-size: var(--passo-3); font-weight: 600;
  margin: 0; padding: 0; line-height: 1.2;
}}
.ui-secao p {{
  font-size: var(--passo-1); color: {TINTA_SUAVE};
  margin: 0; line-height: 1.6; max-width: 72ch;
}}

/* ---------- Faixa de indicadores ---------- */
/* Era uma fileira de cartões com borda, raio e sombra, cada um subindo 2px no hover.
   Virou uma faixa única dividida por fios verticais — a leitura passa a ser "uma linha
   de indicadores do mesmo recorte", que é o que eles são, em vez de peças soltas. */
.ui-faixa {{
  display: grid;
  border-top: 1px solid {TINTA};
  border-bottom: 1px solid {REGUA};
  margin: 1.5rem 0;
}}
.ui-faixa-item {{
  padding: 0.875rem 1.25rem 1rem 0;
  border-left: 1px solid {REGUA};
  padding-left: 1.25rem;
}}
.ui-faixa-item:first-child {{ border-left: none; padding-left: 0; }}
.ui-faixa-rotulo {{
  font-family: var(--mono);
  font-size: var(--passo-0);
  color: {TINTA_FRACA};
  line-height: 1.35;
  margin-bottom: 0.625rem;
  min-height: 2.7em;   /* iguala a linha de base dos valores quando um rótulo quebra */
}}
.ui-faixa-valor {{
  font-family: var(--mono);
  font-size: var(--passo-4);
  font-weight: 500;
  line-height: 0.95;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.03em;
  margin-bottom: 0.5rem;
}}
.ui-faixa-nota {{ font-size: var(--passo-0); color: {TINTA_FRACA}; line-height: 1.45; }}
@media (max-width: 820px) {{
  .ui-faixa {{ grid-template-columns: 1fr !important; }}
  .ui-faixa-item {{ border-left: none; border-top: 1px solid {REGUA}; padding-left: 0; }}
  .ui-faixa-item:first-child {{ border-top: none; }}
  .ui-faixa-rotulo {{ min-height: 0; }}
}}

/* ---------- Nota de leitura ---------- */
/* Era um bloco com fundo azul translúcido e título em versalete — o "callout" padrão de
   dashboard, repetido em toda aba. Virou marginália: régua de 2px na esquerda, sem
   fundo, com o rótulo em monoespaçada. Informa sem disputar com o dado. */
.ui-nota {{
  border-left: 2px solid {REGUA_FORTE};
  padding: 0.125rem 0 0.125rem 1.125rem;
  margin: 1.25rem 0;
  max-width: 76ch;
}}
.ui-nota-titulo {{
  font-family: var(--mono);
  font-size: var(--passo-0);
  color: {OXIDO};
  margin-bottom: 0.375rem;
}}
.ui-nota-corpo {{ font-size: var(--passo-1); color: {TINTA_SUAVE}; line-height: 1.65; }}
.ui-nota-corpo strong {{ color: {TINTA}; font-weight: 600; }}

/* ---------- Achado central ---------- */
/* O único bloco da página com fundo próprio, e o único que sangra para fora da coluna de
   texto: é a conclusão do trabalho, e precisa quebrar o ritmo do documento em vez de ser
   mais uma seção bem-comportada. A régua superior grossa em óxido é a marca d'água do
   projeto. */
.ui-central {{
  background: {PAPEL_FUNDO};
  border-top: 4px solid {OXIDO};
  padding: 2rem 2.25rem 2.25rem;
  margin: 1.5rem -2.25rem 2.5rem;   /* o sangramento */
}}
.ui-central .ui-central-etiqueta {{
  font-family: var(--mono);
  font-size: var(--passo-0);
  color: {OXIDO};
  display: block;
  margin-bottom: 1.25rem;
}}
.ui-central .ui-central-frase {{
  font-size: clamp(1.5rem, 2.9vw, 2.25rem);
  font-weight: 500;
  line-height: 1.22;
  color: {TINTA};
  letter-spacing: -0.02em;
  margin: 0 0 1.75rem;
  max-width: 30ch;
}}
.ui-central-grade {{
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1.5rem;
  align-items: end;
}}
.ui-central .ui-central-numero {{
  font-family: var(--mono);
  font-size: var(--passo-5);
  font-weight: 500;
  line-height: 0.85;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.05em;
  color: {OXIDO};
  border-bottom: 2px solid {OXIDO};
  padding-bottom: 0.5rem;
  white-space: nowrap;
}}
.ui-central .ui-central-legenda {{
  font-size: var(--passo-1);
  color: {TINTA_SUAVE};
  line-height: 1.5;
  max-width: 34ch;
  padding-bottom: 0.75rem;
}}
@media (max-width: 820px) {{
  .ui-central {{ margin-left: -1rem; margin-right: -1rem; padding: 1.5rem 1rem; }}
  .ui-central-grade {{ grid-template-columns: 1fr; gap: 1rem; align-items: start; }}
  .ui-central .ui-central-legenda {{ padding-bottom: 0; }}
}}

/* ---------- Achado / recomendação ---------- */
/* Sem caixa, sem selo colorido, sem hover que levanta: o número da entrada fica na
   margem, como a numeração de um relatório, e uma régua separa uma da outra. */
.ui-achado {{
  display: grid;
  grid-template-columns: 3.5rem minmax(0, 1fr);
  gap: 1rem;
  border-top: 1px solid {REGUA};
  padding: 1.5rem 0;
}}
.ui-achado-selo {{
  font-family: var(--mono);
  font-size: var(--passo-1);
  color: {OXIDO};
  padding-top: 0.3rem;
}}
.ui-achado h3 {{
  font-size: var(--passo-2); font-weight: 600; color: {TINTA};
  margin: 0 0 0.625rem; line-height: 1.3; padding: 0;
}}
.ui-achado-corpo {{
  font-size: var(--passo-1); color: {TINTA_SUAVE}; line-height: 1.7; max-width: 74ch;
}}
.ui-achado-corpo p {{ margin: 0 0 0.75rem; }}
.ui-achado-corpo p:last-child {{ margin-bottom: 0; }}
.ui-achado-corpo strong {{ color: {TINTA}; font-weight: 600; }}
.ui-achado-corpo ul {{ margin: 0 0 0.75rem; padding-left: 1.125rem; }}
.ui-achado-corpo li {{ margin-bottom: 0.3rem; }}
.ui-achado-corpo code {{
  font-family: var(--mono);
  background: {PAPEL_FUNDO}; padding: 0.1rem 0.35rem;
  border-radius: 0; font-size: 0.875em; color: {TINTA};
}}

/* ---------- Categorias ---------- */
/* A régua superior de 3px repete a cor da fatia no gráfico logo acima — é o que liga as
   duas leituras sem legenda escrita. Fora ela, nenhuma borda: as colunas se separam pelo
   espaço, não por moldura. */
.ui-categorias {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.75rem 1.5rem;
  margin: 1.5rem 0 2rem;
}}
.ui-categoria {{ border-top: 3px solid var(--cor); padding-top: 0.875rem; }}
.ui-categoria-topo {{ margin-bottom: 0.625rem; }}
.ui-categoria-valor {{
  font-family: var(--mono);
  font-size: 1.75rem; font-weight: 500; color: {TINTA};
  font-variant-numeric: tabular-nums; letter-spacing: -0.03em;
  display: block; line-height: 1; margin-bottom: 0.375rem;
}}
.ui-categoria-titulo {{
  font-size: var(--passo-1); font-weight: 600; color: {TINTA}; line-height: 1.3;
  display: block;
}}
.ui-categoria-texto {{
  font-size: var(--passo-0); color: {TINTA_SUAVE}; line-height: 1.55; margin: 0 0 0.75rem;
}}
.ui-categoria-acao {{
  font-size: var(--passo-0); color: {TINTA_FRACA}; line-height: 1.5;
  margin: 0; padding-top: 0.625rem;
  border-top: 1px solid {REGUA};
}}
.ui-categoria-acao b {{ font-family: var(--mono); font-weight: 400; color: {OXIDO}; }}

/* ---------- Municípios de uma região ---------- */
/* Eram fichas arredondadas, uma por município — 20 pílulas cinzas ocupando meia tela.
   Viraram uma linha corrida separada por interpontos, que é como um documento lista
   nomes: ocupa um quinto do espaço e lê-se mais rápido. */
.ui-municipios {{
  border-left: 2px solid {REGUA_FORTE};
  padding: 0.125rem 0 0.125rem 1.125rem;
  margin: 0.75rem 0 1.5rem;
}}
.ui-municipios-topo {{
  font-family: var(--mono);
  font-size: var(--passo-0);
  color: {TINTA_FRACA};
  margin-bottom: 0.375rem;
}}
.ui-municipios-lista {{
  font-size: var(--passo-1); color: {TINTA}; line-height: 1.7; max-width: 76ch;
}}
.ui-municipios-lista span:not(:last-child)::after {{
  content: " · ";
  color: {REGUA_FORTE};
}}
</style>""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Componentes
# --------------------------------------------------------------------------- #
def capa(titulo: str, destaque: str, subtitulo: str, procedencia: list[str]) -> None:
    """Cabeçalho da página: título à esquerda, procedência do dado à direita.

    `destaque` é a parte do título que recebe a cor de acento — é o que dá hierarquia
    dentro do próprio título, em vez de deixar as sete palavras com o mesmo peso. Ele é
    colado ao título sem espaço no HTML de propósito: como o `<em>` é `display:block`
    (para quebrar a linha), um espaço entre os dois viraria uma caixa de linha vazia de
    55px — um vão no meio da capa que ninguém pediu.
    `procedencia` são as linhas do bloco técnico (fonte, período, unidade), que num
    relatório impresso ficam no alto da folha de rosto.
    """
    linhas = "<br>".join(procedencia)
    escrever(
        f"""
        <div class="ui-capa">
          <div>
            <h1>{titulo}<em>{destaque}</em></h1>
            <p>{subtitulo}</p>
          </div>
          <div class="ui-capa-procedencia">{linhas}</div>
        </div>
        """
    )


def cabecalho_secao(numero: str, titulo: str, descricao: str = "") -> None:
    """Título de seção numerado — substitui o `st.subheader`, que não tem hierarquia.

    O número não é enfeite: com cinco abas e várias seções em cada uma, ele é o que
    permite dizer "está na 3.2" em voz alta durante a apresentação.
    """
    corpo = f"<p>{descricao}</p>" if descricao else ""
    escrever(
        f"""
        <div class="ui-secao">
          <div class="ui-secao-topo">
            <span class="ui-secao-numero">{numero}</span>
            <h2>{titulo}</h2>
          </div>
          {corpo}
        </div>
        """
    )


def faixa_indicadores(itens: list[dict]) -> None:
    """Faixa horizontal de indicadores do mesmo recorte.

    Cada item aceita: `rotulo`, `valor`, `nota` (opcional) e `cor` (opcional, para o
    valor). Renderizada num `grid` de uma peça só, e não em `st.columns`, porque colunas
    do Streamlit deixam as células com alturas diferentes quando um rótulo quebra em duas
    linhas — o grid iguala a altura de todas automaticamente.
    """
    celulas = "".join(
        f"""
        <div class="ui-faixa-item">
          <div class="ui-faixa-rotulo">{item["rotulo"]}</div>
          <div class="ui-faixa-valor" style="color:{item.get("cor", TINTA)}">{item["valor"]}</div>
          {f'<div class="ui-faixa-nota">{item["nota"]}</div>' if item.get("nota") else ""}
        </div>
        """
        for item in itens
    )
    escrever(
        f'<div class="ui-faixa" style="grid-template-columns:repeat({len(itens)},minmax(0,1fr))">'
        f"{celulas}</div>"
    )


def nota(texto: str, titulo: str = "Como ler") -> None:
    """Marginália de leitura — o "o que estou olhando" de cada seção."""
    cabeca = f'<div class="ui-nota-titulo">{titulo}</div>' if titulo else ""
    escrever(
        f"""
        <div class="ui-nota">
          {cabeca}
          <div class="ui-nota-corpo">{texto}</div>
        </div>
        """
    )


def markdown_para_html(texto: str) -> str:
    """Converte o Markdown da narrativa para HTML, para caber dentro dos nossos blocos.

    Por que não usar `st.markdown` direto: um bloco é uma `<div>` que abre, recebe
    conteúdo e fecha. O Streamlit renderiza cada chamada em um elemento isolado, então
    não dá para abrir a `<div>` numa chamada e fechar em outra — o conteúdo precisa vir
    já como HTML dentro da mesma string.

    É um conversor mínimo de propósito, não uma biblioteca: cobre exatamente o que a
    narrativa usa (negrito, itálico, código, lista e parágrafo). Se o documento passar a
    usar tabela ou título, isto aqui precisa crescer junto — e é melhor que falhe visível
    do que puxar uma dependência nova para o painel.
    """
    partes = []
    for bloco in texto.strip().split("\n\n"):
        bloco = bloco.strip()
        if not bloco:
            continue
        # inline: negrito antes de itálico, senão `**x**` seria lido como dois itálicos
        bloco = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", bloco, flags=re.S)
        bloco = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", bloco, flags=re.S)
        bloco = re.sub(r"`([^`]+?)`", r"<code>\1</code>", bloco)

        linhas = bloco.split("\n")
        if all(l.lstrip().startswith(("- ", "* ")) for l in linhas):
            itens = "".join(f"<li>{l.lstrip()[2:].strip()}</li>" for l in linhas)
            partes.append(f"<ul>{itens}</ul>")
        else:
            partes.append(f"<p>{' '.join(l.strip() for l in linhas)}</p>")
    return "".join(partes)


def tema_grafico(fig, altura: int | None = None):
    """Encaixa um gráfico Plotly no tema do painel.

    O Plotly desenha em fundo branco puro com grade cinza-azulada e fonte própria. Dentro
    de um documento em papel, isso aparece como um retângulo mais claro que a página, com
    tipografia estranha ao resto. Esta função é chamada por todos os gráficos para que a
    correção viva num lugar só.

    Devolve a própria figura para poder ser usada em cadeia: `tema_grafico(px.bar(...))`.
    """
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",   # transparente: o fundo é o papel da página
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TINTA_SUAVE, size=12, family="Plex Sans, Segoe UI, sans-serif"),
        hoverlabel=dict(
            bgcolor=PAPEL_ALTO,
            bordercolor=TINTA,
            font=dict(color=TINTA, size=12, family="Plex Sans, Segoe UI, sans-serif"),
        ),
        legend=dict(font=dict(color=TINTA_SUAVE, size=11)),
    )
    # Grade discreta: serve para o olho medir a barra, não para ser vista. A linha do eixo
    # fica visível (ao contrário da versão anterior) porque em papel é a régua que ancora
    # a leitura — é a mesma lógica do resto do painel.
    fig.update_xaxes(
        gridcolor=REGUA, zerolinecolor=REGUA_FORTE, linecolor=REGUA_FORTE,
        tickfont=dict(color=TINTA_FRACA, size=11),
        title_font=dict(color=TINTA_FRACA, size=12),
    )
    fig.update_yaxes(
        gridcolor=REGUA, zerolinecolor=REGUA_FORTE, linecolor=REGUA_FORTE,
        tickfont=dict(color=TINTA_SUAVE, size=11),
        title_font=dict(color=TINTA_FRACA, size=12),
    )
    if altura:
        fig.update_layout(height=altura)
    return fig


def cartoes_categoria(itens: list[dict]) -> None:
    """Grade de categorias: percentual, o que a categoria significa e o que ela pede.

    Cada item aceita `titulo`, `valor`, `cor`, `significado` e `acao`. A régua colorida no
    topo repete a cor da fatia correspondente no gráfico logo acima — é o que liga as duas
    leituras sem precisar de legenda escrita.
    """
    blocos = "".join(
        f"""
        <div class="ui-categoria" style="--cor:{item["cor"]}">
          <div class="ui-categoria-topo">
            <span class="ui-categoria-valor">{item["valor"]}</span>
            <span class="ui-categoria-titulo">{item["titulo"]}</span>
          </div>
          <p class="ui-categoria-texto">{item["significado"]}</p>
          <p class="ui-categoria-acao"><b>o que fazer</b> — {item["acao"]}</p>
        </div>
        """
        for item in itens
    )
    escrever(f'<div class="ui-categorias">{blocos}</div>')


def lista_municipios(regiao: str, municipios: list[str]) -> None:
    """Lista corrida dos municípios que formam uma região de saúde.

    Existe porque "3ª Região - PB" não significa nada para quem não trabalha na
    Secretaria: o nome é um código administrativo. Ler "Esperança, Areia, Remígio…"
    localiza a região na hora, e é a diferença entre o painel ser consultável por
    qualquer pessoa ou só por quem já conhece a divisão regional.
    """
    nomes = "".join(f"<span>{m}</span>" for m in municipios)
    escrever(
        f"""
        <div class="ui-municipios">
          <div class="ui-municipios-topo">os {len(municipios)} municípios da {regiao}</div>
          <div class="ui-municipios-lista">{nomes}</div>
        </div>
        """
    )


def achado_central(etiqueta: str, frase: str, numero: str, legenda: str) -> None:
    """O bloco de abertura da aba de achados — a conclusão do projeto em uma frase.

    `numero` é passado calculado pelo `app.py`: é o mesmo valor que aparece na capa e na
    matriz, e não uma cópia digitada aqui.
    """
    escrever(
        f"""
        <div class="ui-central">
          <span class="ui-central-etiqueta">{etiqueta}</span>
          <div class="ui-central-frase">{frase}</div>
          <div class="ui-central-grade">
            <div class="ui-central-numero">{numero}</div>
            <div class="ui-central-legenda">{legenda}</div>
          </div>
        </div>
        """
    )


def cartao_achado(indice: int, titulo: str, corpo_md: str) -> None:
    """Um achado, aberto na tela.

    Aberto, e não dentro de um `st.expander`: um achado que exige clique para aparecer
    compete em destaque com o rodapé da página. O número na margem dá a ordem de leitura
    sem precisar de "Achado 1 —" escrito no título — e é o que liga a entrada da tela ao
    texto do relatório.
    """
    escrever(
        f"""
        <div class="ui-achado">
          <div class="ui-achado-selo">{indice:02d}</div>
          <div>
            <h3>{titulo}</h3>
            <div class="ui-achado-corpo">{markdown_para_html(corpo_md)}</div>
          </div>
        </div>
        """
    )


def cartao_acao(indice: int, titulo: str, corpo_md: str) -> None:
    """Uma recomendação. Mesma anatomia do achado, com a marca da margem em "R1", "R2"…
    — a diferença de rótulo é o que separa "o que descobrimos" de "o que fazer"."""
    escrever(
        f"""
        <div class="ui-achado">
          <div class="ui-achado-selo">R{indice}</div>
          <div>
            <h3>{titulo}</h3>
            <div class="ui-achado-corpo">{markdown_para_html(corpo_md)}</div>
          </div>
        </div>
        """
    )
