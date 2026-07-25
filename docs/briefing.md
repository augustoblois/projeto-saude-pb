# Briefing — Mapa de Evasão Assistencial da PB

> Fonte de intenção (entrevista de discovery). Gerado por briefing-intake.
> Insumo do pm-agent (write-prd). Não contém metas medíveis nem épicos — isso é o PRD.

## Em uma frase
Um painel Streamlit que mostra de onde saem e pra onde vão os pacientes internados na Paraíba (SIH/DATASUS 2025), com índice de dependência por região de saúde — uma ferramenta que a SES-PB poderia usar de verdade em decisões de regionalização/PPI.

## Problema
Quase metade das internações da PB acontece fora do município de residência do paciente (49,8% em jan/2025), e nenhum painel público mostra esse fluxo origem→destino. O gestor estadual decide pactuação (PPI) e regionalização sem enxergar a evasão assistencial. No contexto acadêmico: o professor cobra explicitamente **viabilidade real** — um produto que *possa* ser usado no mundo real (governo, jornalistas, profissionais de saúde), não um exercício de sala.

## Público / personas
- **Professor da disciplina (avaliador real)** — quem dá a nota · job: verificar que o produto tem aplicação prática real, análise consolidada, comunicação executiva e reprodutibilidade (rubrica P3, 40% da média).
- **Gestor da SES-PB (usuário simbólico primário)** — decisor de regionalização/PPI · job: enxergar quais regiões dependem de quais para internação e dimensionar a pactuação.
- **Jornalista de dados / profissional de saúde (usuários simbólicos secundários)** — · job: encontrar e comunicar padrões de evasão assistencial que hoje não estão em nenhum painel público.

## O que o cliente quer (intenção, não requisito)
- Demo ao vivo do painel no dia da apresentação — abrir, navegar, mostrar o achado.
- Matriz origem→destino das internações + índice de dependência por região de saúde.
- Que o produto "prove" viabilidade: dá pra imaginar a SES-PB usando de verdade.
- Narrativa de atualização contínua: o pipeline (`src/congelar_sih.py`) baixa qualquer mês novo que o DATASUS publicar — dados congelados localmente são decisão de engenharia (servidor instável), não limitação. **"Tempo real" não existe para SIH**: o DATASUS publica lote mensal com ~2 meses de atraso; ritmo mensal é o máximo que qualquer produto real consegue.
- Visual caprichado *dentro* do Streamlit (mapa interativo, matriz com filtros) — sem virar projeto de frontend.

## Decisões de escopo (do fork)
- Tipo de produto: painel de dados (web-app Streamlit) — não é site institucional.
- Stack: **Streamlit** (Next.js considerado e descartado: consome horas que a rubrica não mede, sai da stack da disciplina, piora a reprodutibilidade).
- Dados: SIH-PB jan–dez/2025, congelados em parquet versionado no repositório.
- Prazo: **07/08/2026** (16 dias da data do briefing), escopo total ~60h.

## Restrições
- Idiomas: pt-BR. · Orçamento: não se aplica (projeto acadêmico).
- Dupla: Augusto (técnico, `src/` + `notebooks/01-*`) + Pedro (não-técnico, `notebooks/90-*` + `reports/`) — territórios separados, colaboração via GitHub com `STATUS.md` em linguagem leiga.
- Não pode faltar: demo funcionando offline (nada depende de fonte viva), reprodutibilidade (`streamlit run` + parquets no repo), recomendações práticas pra SES-PB.
- Evitar: escopo que não pontue na rubrica P3; qualquer coisa que exija linkage individual sensível; ângulo que já exista em painel público.
- P1 e P2 já foram apresentados (com o projeto antigo) — a única entrega restante é o P3.

## A definir
- ~~Conversa com o professor formalizando a troca de projeto~~ — **feito em 24/07/2026**: formalizada por e-mail e **aceita pelo professor**.
- Volume/completude dos meses finais de 2025 no DATASUS (nov/dez podem estar incompletos) — verificar no placar do congelamento.
