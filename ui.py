"""Camada de apresentação do painel — tokens, ícones e componentes visuais.

Existe separado do `app.py` por um motivo prático: `app.py` já carrega, filtra e agrega
dados; se ele também carregasse o HTML de cada cartão, cada aba viraria uma mistura de
`groupby` com `<div>`. Aqui ficam só as peças de tela, e as abas passam a montar a
interface chamando funções com nome de coisa ("cartão de número", "cartão de achado")
em vez de repetir marcação.

Duas restrições que valem para tudo neste arquivo:

1. **Nada é buscado na rede.** Sem Google Fonts, sem CDN de ícone. A fonte é a do
   sistema e os ícones são SVG do Lucide colados no próprio código. O painel precisa
   abrir com a internet desligada (regra nº 1 do projeto).
2. **Nenhum número é escrito à mão.** Este módulo só sabe *desenhar* — quem calcula é
   o `app.py`, a partir das pré-agregações.
"""

from __future__ import annotations

import re

import streamlit as st

# --------------------------------------------------------------------------- #
# Tokens — a paleta inteira do painel em um lugar só.
#
# Está duplicada com `.streamlit/config.toml` de propósito: o config é lido pelo
# Streamlit para pintar os widgets nativos (input, tabela, slider), e este dicionário é
# lido pelo nosso CSS e pelos gráficos Plotly. São dois consumidores diferentes do mesmo
# valor — mudar a cor exige tocar nos dois, e o comentário no config avisa disso.
# --------------------------------------------------------------------------- #
FUNDO = "#0B0F1A"
SUPERFICIE = "#131A2B"
SUPERFICIE_ALTA = "#1A2438"
BORDA = "#22304A"
BORDA_FORTE = "#2E3D5C"

TEXTO = "#E8EDF7"
TEXTO_SUAVE = "#A3B0C6"
TEXTO_FRACO = "#7C8AA3"

ACENTO = "#38BDF8"          # ciano — deslocamento, fluxo, destaque
ACENTO_FORTE = "#0EA5E9"
ALERTA = "#F59E0B"          # âmbar — dependência alta / atenção
CRITICO = "#F87171"         # vermelho suave — o caso mais grave
OK = "#34D399"              # verde — dependência baixa / resolvido em casa
ROXO = "#A78BFA"            # categoria auxiliar

# Sequência usada quando um gráfico precisa de cores categóricas sem significado fixo.
# Ordenada por contraste sobre o fundo escuro: a primeira é a mais legível.
PALETA_CATEGORICA = [
    "#38BDF8", "#F59E0B", "#34D399", "#A78BFA", "#F87171",
    "#22D3EE", "#FBBF24", "#4ADE80", "#C084FC", "#FB7185",
]


# --------------------------------------------------------------------------- #
# Ícones — Lucide (lucide.dev), licença ISC, colados como SVG inline.
#
# Inline em vez de <img src="..."> ou pacote de ícones: um `src` externo dependeria de
# rede, e um pacote traria dependência nova só para desenhar traço. Assim o ícone herda
# a cor do texto (`currentColor`) e acompanha qualquer mudança de paleta sozinho.
# --------------------------------------------------------------------------- #
_TRACOS = {
    "map-pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "trending-up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "triangle-alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "lightbulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "table": '<path d="M12 3v18"/><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/>',
    "chart-bar": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "map": '<path d="M14.1 5.55a2 2 0 0 0 1.79 0l3.66-1.83A1 1 0 0 1 21 4.62v12.76a1 1 0 0 1-.55.9l-4.56 2.27a2 2 0 0 1-1.78 0l-4.22-2.1a2 2 0 0 0-1.78 0l-3.66 1.83A1 1 0 0 1 3 19.38V6.62a1 1 0 0 1 .55-.9l4.56-2.27a2 2 0 0 1 1.78 0Z"/><path d="M15 5.76v15"/><path d="M9 3.24v15"/>',
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "cross": '<path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2c0 1.1.9 2 2 2h5v5c0 1.1.9 2 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/>',
    "stethoscope": '<path d="M11 2v2"/><path d="M5 2v2"/><path d="M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1"/><path d="M8 15a6 6 0 0 0 12 0v-3"/><circle cx="20" cy="10" r="2"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "sliders": '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/><line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="12" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
    "circle-check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>',
    "layers": '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "plane": '<path d="M2 22h20"/><path d="m6.36 17.4-2.36-.4-2-4 1.1-.55a2 2 0 0 1 1.8 0l.17.1a2 2 0 0 0 1.8 0L8 12 5 6l.9-.45a2 2 0 0 1 2.09.2l4.02 3a2 2 0 0 0 2.1.2l4.19-2.06a2.4 2.4 0 0 1 1.73-.17L21 7a1.4 1.4 0 0 1 .87 1.99l-.38.76c-.23.46-.6.84-1.07 1.08L7.58 17.2a2 2 0 0 1-1.22.2Z"/>',
    "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "hourglass": '<path d="M5 22h14"/><path d="M5 2h14"/><path d="M17 22v-4.2a2 2 0 0 0-.6-1.4L12 12l-4.4 4.4a2 2 0 0 0-.6 1.4V22"/><path d="M7 2v4.2a2 2 0 0 0 .6 1.4L12 12l4.4-4.4a2 2 0 0 0 .6-1.4V2"/>',
    "scissors": '<circle cx="6" cy="6" r="3"/><path d="M8.12 8.12 12 12"/><path d="M20 4 8.12 15.88"/><circle cx="6" cy="18" r="3"/><path d="M14.8 14.8 20 20"/>',
    "compass": '<path d="m16.24 7.76-1.8 5.39a2 2 0 0 1-1.29 1.29l-5.39 1.8 1.8-5.39a2 2 0 0 1 1.29-1.29Z"/><circle cx="12" cy="12" r="10"/>',
}


def icone(nome: str, tamanho: int = 20, cor: str = "currentColor", traco: float = 1.75) -> str:
    """Devolve o SVG do ícone como string, pronto para entrar num f-string de HTML.

    `currentColor` por padrão: o ícone herda a cor do texto ao redor, então um cartão
    que muda de cor leva o ícone junto sem precisar passar cor de novo.
    """
    if nome not in _TRACOS:
        raise KeyError(f"Ícone '{nome}' não existe. Disponíveis: {', '.join(sorted(_TRACOS))}")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{traco}" '
        f'stroke-linecap="round" stroke-linejoin="round" class="lucide">{_TRACOS[nome]}</svg>'
    )


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

    Faz duas coisas diferentes:
    1. Corrige os widgets NATIVOS do Streamlit (abas, inputs, tabela, expander), que vêm
       com uma hierarquia visual muito plana por padrão.
    2. Define as classes dos componentes próprios deste módulo (`ui-cartao`, `ui-achado`…).
    """
    st.markdown(
        f"""<style>
/* ---------- Base ---------- */
/* Escala tipográfica declarada como variável: os componentes referenciam `--passo-N`
   em vez de cravar px, então mudar a escala inteira é mudar estas seis linhas. */
:root {{
  --passo-0: 0.8125rem;  /* 13px — rótulo, legenda */
  --passo-1: 0.9375rem;  /* 15px — corpo */
  --passo-2: 1.25rem;    /* 20px — título de cartão */
  --passo-3: 1.75rem;    /* 28px — título de seção */
  --passo-4: 2.75rem;    /* 44px — número de destaque */
  --passo-5: 4rem;       /* 64px — número de capa */
  --raio: 14px;
  --raio-g: 18px;
}}

html, body, .stApp, [class*="st-"] {{
  -webkit-font-smoothing: antialiased;   /* traço mais fino e nítido em tela Retina */
  -moz-osx-font-smoothing: grayscale;
}}

.stApp {{ background: {FUNDO}; }}

/* O container principal do Streamlit vem com padding-top generoso que empurra o título
   para o meio da tela. Reduzido para o topo respirar sem desperdiçar dobra. */
.stMainBlockContainer, [data-testid="stMainBlockContainer"] {{
  padding-top: 2.25rem;
  padding-bottom: 5rem;
  max-width: 1180px;   /* linha de leitura: texto corrido em 1900px vira faixa ilegível */
}}

[data-testid="stHeader"] {{ background: transparent; }}

/* `balance` distribui as palavras entre as linhas de um título para não sobrar uma
   palavra órfã na última linha; `pretty` faz o mesmo, mais suave, no texto corrido. */
h1, h2, h3, h4 {{ text-wrap: balance; letter-spacing: -0.02em; }}
p, li {{ text-wrap: pretty; }}

/* ---------- Abas ---------- */
.stTabs [data-baseweb="tab-list"] {{
  gap: 0.25rem;
  border-bottom: 1px solid {BORDA};
  background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
  height: 46px;                 /* acima do mínimo de 40px de área de toque */
  padding: 0 1rem;
  color: {TEXTO_FRACO};
  font-size: var(--passo-1);
  font-weight: 500;
  border-radius: var(--raio) var(--raio) 0 0;
  /* propriedades nomeadas uma a uma: `transition: all` obrigaria o navegador a vigiar
     todas as propriedades e engasga no hover */
  transition-property: color, background-color;
  transition-duration: 160ms;
  transition-timing-function: cubic-bezier(0.2, 0, 0, 1);
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {TEXTO}; background: {SUPERFICIE}; }}
.stTabs [aria-selected="true"] {{ color: {ACENTO} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {ACENTO}; height: 2px; }}
.stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* ---------- Inputs ---------- */
.stSelectbox label, .stRadio label, .stSlider label, .stMultiSelect label {{
  font-size: var(--passo-0) !important;
  font-weight: 600 !important;
  color: {TEXTO_SUAVE} !important;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
[data-baseweb="select"] > div {{
  background: {SUPERFICIE} !important;
  border-color: {BORDA} !important;
  border-radius: var(--raio) !important;
  transition-property: border-color;
  transition-duration: 160ms;
}}
[data-baseweb="select"] > div:hover {{ border-color: {BORDA_FORTE} !important; }}

/* ---------- Tabela ---------- */
[data-testid="stDataFrame"] {{
  border-radius: var(--raio);
  overflow: hidden;
  /* sombra em camadas no lugar de borda dura: a borda sólida marca um contorno seco,
     enquanto as três sombras translúcidas dão profundidade e funcionam sobre qualquer
     fundo */
  box-shadow: 0 0 0 1px {BORDA}, 0 1px 2px rgba(0,0,0,0.4), 0 8px 24px -12px rgba(0,0,0,0.6);
}}

/* ---------- Expander ---------- */
[data-testid="stExpander"] {{
  border: 1px solid {BORDA};
  border-radius: var(--raio);
  background: {SUPERFICIE};
  overflow: hidden;
}}
[data-testid="stExpander"] summary {{
  font-size: var(--passo-1);
  font-weight: 500;
  transition-property: background-color;
  transition-duration: 160ms;
}}
[data-testid="stExpander"] summary:hover {{ background: {SUPERFICIE_ALTA}; }}

/* Régua: a `---` do Streamlit vem como linha cinza sólida de ponta a ponta. Vira um
   degradê que some nas bordas — separa sem cortar a página em dois. */
hr {{
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, {BORDA} 15%, {BORDA} 85%, transparent);
  margin: 2.5rem 0;
}}

/* ================= Componentes próprios ================= */

/* ---------- Capa ---------- */
.ui-capa {{ text-align: center; padding: 1rem 0 2rem; }}
.ui-capa-etiqueta {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.375rem 0.875rem;
  border-radius: 999px;
  background: rgba(56,189,248,0.1);
  border: 1px solid rgba(56,189,248,0.25);
  color: {ACENTO};
  font-size: var(--passo-0); font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase;
}}
.ui-capa h1 {{
  font-size: clamp(2.25rem, 5vw, 3.75rem);  /* acompanha a largura da janela */
  font-weight: 800;
  line-height: 1.05;
  margin: 1.25rem 0 0.875rem;
  color: {TEXTO};
}}
.ui-capa h1 em {{
  font-style: normal;
  /* degradê no texto: o Streamlit não tem "cor de destaque em parte do título", e
     pintar só a palavra que importa é o que cria hierarquia DENTRO do título */
  background: linear-gradient(135deg, {ACENTO} 0%, {ROXO} 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.ui-capa p {{
  font-size: 1.0625rem;
  color: {TEXTO_SUAVE};
  max-width: 640px;
  margin: 0 auto;
  line-height: 1.6;
}}

/* ---------- Cabeçalho de seção ---------- */
.ui-secao {{ display: flex; align-items: flex-start; gap: 0.875rem; margin: 0 0 0.5rem; }}
.ui-secao-icone {{
  flex: 0 0 auto;
  width: 40px; height: 40px;           /* alinhado ao mínimo de área de toque */
  display: grid; place-items: center;
  border-radius: 11px;                  /* concêntrico: 14px do pai menos ~3px de folga */
  background: rgba(56,189,248,0.1);
  border: 1px solid rgba(56,189,248,0.22);
  color: {ACENTO};
}}
.ui-secao h2 {{
  font-size: var(--passo-3); font-weight: 700;
  margin: 0; padding: 0; line-height: 1.25; color: {TEXTO};
}}
.ui-secao p {{
  font-size: var(--passo-1); color: {TEXTO_SUAVE};
  margin: 0.375rem 0 0; line-height: 1.55; max-width: 70ch;
}}

/* ---------- Cartão de número ---------- */
.ui-numeros {{ display: grid; gap: 0.75rem; margin: 1.25rem 0; }}
.ui-cartao {{
  background: {SUPERFICIE};
  border: 1px solid {BORDA};
  border-radius: var(--raio-g);
  padding: 1.125rem 1.25rem;
  display: flex; flex-direction: column; gap: 0.5rem;
  transition-property: border-color, transform;
  transition-duration: 180ms;
  transition-timing-function: cubic-bezier(0.2, 0, 0, 1);
}}
.ui-cartao:hover {{ border-color: {BORDA_FORTE}; transform: translateY(-2px); }}
.ui-cartao-topo {{
  display: flex; align-items: center; gap: 0.5rem;
  color: {TEXTO_FRACO};
  font-size: var(--passo-0); font-weight: 600;
  letter-spacing: 0.04em; text-transform: uppercase;
}}
.ui-cartao-valor {{
  font-size: var(--passo-4); font-weight: 800; line-height: 1;
  /* dígitos de largura fixa: sem isso, trocar o filtro de mês faz o número mudar de
     largura e a linha inteira de cartões "pula" */
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.03em;
}}
.ui-cartao-nota {{ font-size: var(--passo-0); color: {TEXTO_FRACO}; line-height: 1.45; }}

/* ---------- Bloco de instrução ---------- */
.ui-dica {{
  display: flex; gap: 0.75rem; align-items: flex-start;
  background: rgba(56,189,248,0.06);
  border: 1px solid rgba(56,189,248,0.18);
  border-left: 3px solid {ACENTO};
  border-radius: var(--raio);
  padding: 0.875rem 1rem;
  margin: 1rem 0;
}}
.ui-dica-icone {{ flex: 0 0 auto; color: {ACENTO}; margin-top: 1px; }}
.ui-dica-corpo {{ font-size: var(--passo-1); color: {TEXTO_SUAVE}; line-height: 1.6; }}
.ui-dica-corpo strong {{ color: {TEXTO}; font-weight: 600; }}
.ui-dica-titulo {{
  font-size: var(--passo-0); font-weight: 700; color: {TEXTO};
  letter-spacing: 0.04em; text-transform: uppercase;
  margin-bottom: 0.25rem;
}}

/* ---------- Achado central ---------- */
.ui-central {{
  position: relative;
  border-radius: 24px;
  border: 1px solid rgba(56,189,248,0.28);
  /* o degradê radial faz o canto superior esquerdo "acender": dá foco sem precisar de
     uma cor de fundo chapada, que competiria com os cartões vizinhos */
  background:
    radial-gradient(120% 140% at 0% 0%, rgba(56,189,248,0.14) 0%, transparent 55%),
    {SUPERFICIE};
  padding: 2.5rem;
  margin: 1rem 0 2rem;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 24px 48px -24px rgba(56,189,248,0.25);
}}
.ui-central-etiqueta {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  color: {ACENTO}; font-size: var(--passo-0); font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase;
}}
.ui-central-grade {{
  display: grid; grid-template-columns: minmax(0,1fr) auto;
  gap: 2.5rem; align-items: center; margin-top: 1.25rem;
}}
.ui-central-frase {{
  font-size: clamp(1.5rem, 2.6vw, 2.125rem);
  font-weight: 750; line-height: 1.22; color: {TEXTO};
  letter-spacing: -0.02em; margin: 0;
}}
.ui-central-numero {{
  font-size: var(--passo-5); font-weight: 850; line-height: 0.9;
  font-variant-numeric: tabular-nums; letter-spacing: -0.045em;
  background: linear-gradient(135deg, {ACENTO} 0%, {ROXO} 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: right; white-space: nowrap;
}}
.ui-central-legenda {{
  font-size: var(--passo-0); color: {TEXTO_FRACO}; text-align: right;
  margin-top: 0.5rem; max-width: 15ch; margin-left: auto; line-height: 1.4;
}}
/* Abaixo de ~900px o número não cabe ao lado da frase sem espremer as duas colunas. */
@media (max-width: 900px) {{
  .ui-central-grade {{ grid-template-columns: 1fr; gap: 1.5rem; }}
  .ui-central-numero, .ui-central-legenda {{ text-align: left; margin-left: 0; }}
}}

/* ---------- Cartão de achado / ação ---------- */
.ui-achado {{
  display: grid; grid-template-columns: auto minmax(0,1fr);
  gap: 1.25rem;
  background: {SUPERFICIE};
  border: 1px solid {BORDA};
  border-radius: var(--raio-g);
  padding: 1.5rem;
  margin-bottom: 0.875rem;
  transition-property: border-color, transform;
  transition-duration: 180ms;
  transition-timing-function: cubic-bezier(0.2, 0, 0, 1);
}}
.ui-achado:hover {{ border-color: {BORDA_FORTE}; transform: translateY(-2px); }}
.ui-achado-selo {{
  width: 46px; height: 46px;
  display: grid; place-items: center;
  border-radius: 13px;              /* concêntrico com o raio 18px do cartão */
  font-size: 1rem; font-weight: 800;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}}
.ui-achado h3 {{
  font-size: var(--passo-2); font-weight: 700; color: {TEXTO};
  margin: 0 0 0.625rem; line-height: 1.3; padding: 0;
  /* o selo tem 46px; 0.5rem de deslocamento alinha o eixo óptico do texto com o do
     número dentro do selo, em vez de alinhar as caixas geométricas */
  padding-top: 0.5rem;
}}
.ui-achado-corpo {{ font-size: var(--passo-1); color: {TEXTO_SUAVE}; line-height: 1.65; }}
.ui-achado-corpo p {{ margin: 0 0 0.75rem; }}
.ui-achado-corpo p:last-child {{ margin-bottom: 0; }}
.ui-achado-corpo strong {{ color: {TEXTO}; font-weight: 650; }}
.ui-achado-corpo ul {{ margin: 0 0 0.75rem; padding-left: 1.125rem; }}
.ui-achado-corpo li {{ margin-bottom: 0.3rem; }}
.ui-achado-corpo code {{
  background: {SUPERFICIE_ALTA}; padding: 0.1rem 0.35rem;
  border-radius: 5px; font-size: 0.875em; color: {ACENTO};
}}

/* ---------- Cartões de categoria ---------- */
.ui-categorias {{
  display: grid;
  /* auto-fit + minmax: as colunas se reorganizam sozinhas conforme a largura, sem
     precisar declarar quantas cabem em cada faixa de tela */
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0 1.5rem;
}}
.ui-categoria {{
  position: relative;
  background: {SUPERFICIE};
  border: 1px solid {BORDA};
  border-radius: var(--raio-g);
  padding: 1.125rem 1.25rem 1rem;
  overflow: hidden;
  transition-property: border-color, transform;
  transition-duration: 180ms;
  transition-timing-function: cubic-bezier(0.2, 0, 0, 1);
}}
.ui-categoria:hover {{ border-color: var(--cor); transform: translateY(-2px); }}
.ui-categoria-barra {{
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--cor);
}}
.ui-categoria-topo {{
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 0.75rem; margin-bottom: 0.625rem;
}}
.ui-categoria-titulo {{
  font-size: var(--passo-1); font-weight: 650; color: {TEXTO}; line-height: 1.25;
}}
.ui-categoria-valor {{
  font-size: 1.5rem; font-weight: 800; color: var(--cor);
  font-variant-numeric: tabular-nums; letter-spacing: -0.02em;
  white-space: nowrap;
}}
.ui-categoria-texto {{
  font-size: var(--passo-0); color: {TEXTO_SUAVE}; line-height: 1.5; margin: 0 0 0.75rem;
}}
.ui-categoria-acao {{
  display: flex; gap: 0.45rem; align-items: flex-start;
  font-size: var(--passo-0); color: {TEXTO_FRACO}; line-height: 1.45;
  margin: 0; padding-top: 0.75rem;
  border-top: 1px solid {BORDA};
}}
.ui-categoria-acao svg {{ flex-shrink: 0; margin-top: 3px; color: var(--cor); }}

/* ---------- Municípios de uma região ---------- */
.ui-municipios {{
  background: {SUPERFICIE};
  border: 1px solid {BORDA};
  border-radius: var(--raio-g);
  padding: 1.125rem 1.25rem;
  margin: 0.75rem 0 1.25rem;
}}
.ui-municipios-topo {{
  display: flex; align-items: center; gap: 0.5rem;
  color: {TEXTO_FRACO}; font-size: var(--passo-0); font-weight: 600;
  letter-spacing: 0.04em; text-transform: uppercase;
  margin-bottom: 0.875rem;
}}
.ui-fichas {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.ui-ficha {{
  padding: 0.3rem 0.7rem;
  border-radius: 8px;          /* concêntrico: 18px do cartão menos os ~10px de folga */
  background: {SUPERFICIE_ALTA};
  border: 1px solid {BORDA};
  color: {TEXTO_SUAVE};
  font-size: var(--passo-0);
  white-space: nowrap;
}}
</style>""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Componentes
# --------------------------------------------------------------------------- #
def capa(etiqueta: str, titulo: str, destaque: str, subtitulo: str, icone_etiqueta: str = "map-pin") -> None:
    """Cabeçalho da página: etiqueta, título grande centralizado e uma linha de contexto.

    `destaque` é a parte do título que recebe o degradê — é o que dá hierarquia dentro
    do próprio título, em vez de deixar as sete palavras com o mesmo peso.
    """
    escrever(
        f"""
        <div class="ui-capa">
          <span class="ui-capa-etiqueta">{icone(icone_etiqueta, 14)}{etiqueta}</span>
          <h1>{titulo} <em>{destaque}</em></h1>
          <p>{subtitulo}</p>
        </div>
        """
    )


def cabecalho_secao(icone_nome: str, titulo: str, descricao: str = "") -> None:
    """Título de seção com ícone — substitui o `st.subheader`, que não tem hierarquia."""
    corpo = f"<p>{descricao}</p>" if descricao else ""
    escrever(
        f"""
        <div class="ui-secao">
          <div class="ui-secao-icone">{icone(icone_nome, 20)}</div>
          <div><h2>{titulo}</h2>{corpo}</div>
        </div>
        """
    )


def cartoes_numero(itens: list[dict]) -> None:
    """Fileira de cartões de número.

    Cada item aceita: `rotulo`, `valor`, `icone`, `nota` (opcional) e `cor` (opcional).
    Renderizados num `grid` de uma peça só, e não em `st.columns`, porque colunas do
    Streamlit deixam os cartões com alturas diferentes quando um rótulo quebra em duas
    linhas — o grid iguala a altura de todos automaticamente.
    """
    cartoes = "".join(
        f"""
        <div class="ui-cartao">
          <div class="ui-cartao-topo">{icone(item.get("icone", "activity"), 15)}{item["rotulo"]}</div>
          <div class="ui-cartao-valor" style="color:{item.get("cor", TEXTO)}">{item["valor"]}</div>
          {f'<div class="ui-cartao-nota">{item["nota"]}</div>' if item.get("nota") else ""}
        </div>
        """
        for item in itens
    )
    escrever(
        f'<div class="ui-numeros" style="grid-template-columns:repeat({len(itens)},minmax(0,1fr))">{cartoes}</div>'
    )


def dica(texto: str, titulo: str = "Como ler", icone_nome: str = "info") -> None:
    """Bloco de instrução — o "o que estou olhando" que faltava em cada seção."""
    cabeca = f'<div class="ui-dica-titulo">{titulo}</div>' if titulo else ""
    escrever(
        f"""
        <div class="ui-dica">
          <div class="ui-dica-icone">{icone(icone_nome, 18)}</div>
          <div class="ui-dica-corpo">{cabeca}{texto}</div>
        </div>
        """
    )


def markdown_para_html(texto: str) -> str:
    """Converte o Markdown da narrativa para HTML, para caber dentro dos nossos cartões.

    Por que não usar `st.markdown` direto: um cartão é uma `<div>` que abre, recebe
    conteúdo e fecha. O Streamlit renderiza cada chamada em um bloco isolado, então não
    dá para abrir a `<div>` numa chamada e fechar em outra — o conteúdo precisa vir já
    como HTML dentro da mesma string.

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

    O Plotly desenha em fundo branco por padrão. Dentro de um painel escuro, cada gráfico
    virava um retângulo claro no meio da página — o mesmo problema que o mapa tinha. Esta
    função é chamada por todos os gráficos para que a correção viva num lugar só.

    Devolve a própria figura para poder ser usada em cadeia: `tema_grafico(px.bar(...))`.
    """
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",   # transparente: o fundo é o da página
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXTO_SUAVE, size=12),
        # rótulo de hover escuro: o balão claro padrão pisca em branco a cada passada
        # do mouse, que é o efeito mais desagradável possível num painel escuro
        hoverlabel=dict(
            bgcolor=SUPERFICIE_ALTA, bordercolor=BORDA_FORTE, font=dict(color=TEXTO, size=12)
        ),
        legend=dict(font=dict(color=TEXTO_SUAVE, size=11)),
    )
    # grade discreta: serve para o olho medir a barra, não para ser vista. Linha de eixo
    # desligada porque a própria grade já ancora a leitura.
    fig.update_xaxes(
        gridcolor=BORDA, zerolinecolor=BORDA, linecolor=BORDA,
        tickfont=dict(color=TEXTO_FRACO, size=11),
        title_font=dict(color=TEXTO_FRACO, size=12),
    )
    fig.update_yaxes(
        gridcolor=BORDA, zerolinecolor=BORDA, linecolor=BORDA,
        tickfont=dict(color=TEXTO_SUAVE, size=11),
        title_font=dict(color=TEXTO_FRACO, size=12),
    )
    if altura:
        fig.update_layout(height=altura)
    return fig


def cartoes_categoria(itens: list[dict]) -> None:
    """Grade de categorias: percentual, o que a categoria significa e o que ela pede.

    Cada item aceita `titulo`, `valor`, `cor`, `significado` e `acao`. A barrinha colorida
    no topo do cartão repete a cor da fatia correspondente no gráfico logo acima — é o que
    liga as duas leituras sem precisar de legenda escrita.
    """
    cartoes = "".join(
        f"""
        <div class="ui-categoria" style="--cor:{item["cor"]}">
          <div class="ui-categoria-barra"></div>
          <div class="ui-categoria-topo">
            <span class="ui-categoria-titulo">{item["titulo"]}</span>
            <span class="ui-categoria-valor">{item["valor"]}</span>
          </div>
          <p class="ui-categoria-texto">{item["significado"]}</p>
          <p class="ui-categoria-acao">{icone("arrow-right", 13)}<span>{item["acao"]}</span></p>
        </div>
        """
        for item in itens
    )
    escrever(f'<div class="ui-categorias">{cartoes}</div>')


def lista_municipios(regiao: str, municipios: list[str]) -> None:
    """Mostra, em fichas, os municípios que formam uma região de saúde.

    Existe porque "3ª Região - PB" não significa nada para quem não trabalha na
    Secretaria: o nome é um código administrativo. Ler "Esperança, Areia, Remígio…"
    localiza a região na hora, e é a diferença entre o painel ser consultável por
    qualquer pessoa ou só por quem já conhece a divisão regional.
    """
    fichas = "".join(f'<span class="ui-ficha">{m}</span>' for m in municipios)
    escrever(
        f"""
        <div class="ui-municipios">
          <div class="ui-municipios-topo">{icone("building", 15)}
            Os {len(municipios)} municípios da {regiao}</div>
          <div class="ui-fichas">{fichas}</div>
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
          <span class="ui-central-etiqueta">{icone("target", 15)}{etiqueta}</span>
          <div class="ui-central-grade">
            <p class="ui-central-frase">{frase}</p>
            <div>
              <div class="ui-central-numero">{numero}</div>
              <div class="ui-central-legenda">{legenda}</div>
            </div>
          </div>
        </div>
        """
    )


def cartao_achado(indice: int, titulo: str, corpo_md: str, cor: str = ACENTO) -> None:
    """Um achado, aberto na tela.

    Aberto, e não dentro de um `st.expander`: um achado que exige clique para aparecer
    compete em destaque com o rodapé da página. O selo numerado à esquerda dá a ordem de
    leitura sem precisar de "Achado 1 —" escrito no título — e o número é mais útil ali
    que um ícone, porque a numeração é o que liga o cartão ao texto do relatório.
    """
    # a mesma cor serve de fundo (bem translúcido), borda e texto do selo: uma cor só,
    # três opacidades, em vez de três valores para manter em sincronia
    escrever(
        f"""
        <div class="ui-achado">
          <div class="ui-achado-selo"
               style="background:{cor}1A;border:1px solid {cor}40;color:{cor}">{indice:02d}</div>
          <div>
            <h3>{titulo}</h3>
            <div class="ui-achado-corpo">{markdown_para_html(corpo_md)}</div>
          </div>
        </div>
        """
    )


def cartao_acao(indice: int, titulo: str, corpo_md: str) -> None:
    """Uma recomendação. Mesma anatomia do achado, com o selo em âmbar e um ícone de
    ação — a diferença de cor é o que separa "o que descobrimos" de "o que fazer"."""
    escrever(
        f"""
        <div class="ui-achado">
          <div class="ui-achado-selo"
               style="background:{ALERTA}1A;border:1px solid {ALERTA}40;color:{ALERTA}">
            {icone("lightbulb", 20)}
          </div>
          <div>
            <h3>{titulo}</h3>
            <div class="ui-achado-corpo">{markdown_para_html(corpo_md)}</div>
          </div>
        </div>
        """
    )
