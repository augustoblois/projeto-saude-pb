# QA Report — Mapa de Evasão Assistencial da PB

> Fontes: briefing.md, prd.md, backlog.md, TASKS.md. Gerado pelo qa-agent.
> Auditoria independente da cadeia de governança antes do desenvolvimento.

## Veredito: APROVADO
Cadeia íntegra — zero bloqueios. Rastreabilidade fechada em todos os seams: 5 objetivos → 8 RFs → 7 épicos → 20 stories → TASKS.md espelhado. 3 avisos e 1 nota, nenhum impede o build.

## Resumo por seam
- **A · briefing → PRD:** OK (1 aviso)
- **B · PRD → backlog:** OK (1 aviso)
- **C · backlog → TASKS.md:** OK (1 nota)
- **Órfãos / invenções:** OK — nenhum órfão, nenhuma invenção

## Verificações que passaram
- **Seam A:** todos os objetivos (O1–O5) traçam a intenção explícita do briefing; todos têm métrica checável; escopo tem "em escopo" E "fora de escopo" explícitos; todo RF cita persona + objetivo; itens "A definir" do briefing viraram gap declarado (G-4) e verificação registrada (completude nov/dez confirmada 12/12 meses). As perguntas PA-1..5 são derivação legítima da intenção (análise consolidada + recomendações), não invenção.
- **Seam B:** todo épico EP-01..07 tem ≥ 1 story; toda story mapeia a exatamente um épico; estimativas Fibonacci, máx. 5 pts (nada ≥ 13); âncora declarada (US-19 = 1 pt); DoD única e compartilhada; Given/When/Then demonstráveis em todas as 20 stories; dependências explícitas e a ordem sugerida as respeita (incl. US-16→US-14 e US-18→US-17). Cobertura total: RF-01→US-11 · RF-02→US-09/13 · RF-03→US-12 · RF-04→US-14 · RF-05→US-14/16 · RF-06→US-18 · RF-07→US-19 · RF-08→US-11; PA-1→US-05 · PA-2→US-10 · PA-3→US-06 · PA-4→US-07 · PA-5→US-08. Soma de pontos confere (66 / 61 sem EP-07).
- **Seam C:** TASKS.md espelha o backlog — 7 seções de épico, 20 stories, todas as tasks como checkboxes, pontos, executores, dependências e decisões D-1/D-2/D-3 idênticos; G-4 presente. Reordenação US-03 antes de US-02 no EP-01 respeita dependências (legítima).

## Achados
1. **[AVISO · dono: PM]** seam A/B — A decisão D-1 (gate do backlog) estende o pipeline para baixar RD de PE/RN/CE 2025, mas a seção "Fontes de dados" do PRD ainda diz que a viabilidade está "já validada — dados baixados e congelados", o que só vale para a PB. O PRD ficou desatualizado em relação a uma decisão aprovada: ~36 arquivos novos a baixar de um FTP declaradamente instável, dentro de janela de 16 dias. Correção esperada: anotar no PRD (fontes + riscos) que PA-5 depende de congelamento adicional ainda não realizado.
2. **[AVISO · dono: scrum-master]** seam B — US-08 (5 pts) embute três entregas distintas: estender `src/congelar_sih.py`, congelar/validar 12 meses × 3 UFs em FTP instável, e a análise PA-5. É a story com maior risco de estouro do backlog e, ao contrário da US-12 (mapa), não tem guard-rail de degradação (ex.: "se o congelamento das UFs vizinhas não fechar até dia X, PA-5 reduz para nota metodológica"). Correção esperada: definir o guard-rail de corte da US-08.
3. **[AVISO · dono: PM]** seam A — G-4 (troca de projeto não formalizada com o professor) é o único evento capaz de invalidar toda a cadeia e segue aberto, com investimento pesado de horas começando já em 22/07. Não bloqueia a governança (é ação humana, corretamente registrada), mas a janela para formalizar antes do investimento é de dias, não de semanas.
4. **[NOTA · dono: scrum-master]** seam C — Na US-12, o guard-rail anti-sumidouro é critério de aceite no backlog, mas aparece como task/checkbox no TASKS.md. Drift benigno (a informação existe nos dois), só registrar que o checkbox não é uma entrega e sim uma regra de decisão.

## Análise crítica
**Riscos por épico**
- **EP-01:** técnico — a malha município→região de saúde é a fundação do produto-assinatura; fonte pública divergente/desatualizada distorce o índice inteiro. Mitigação já embutida (US-02 exige documentar fonte e data).
- **EP-02:** operacional — US-08/D-1 reabre dependência do FTP do DATASUS que o congelamento da PB tinha eliminado (ver achado 2).
- **EP-03:** negócio — a fórmula D-2 é simples por decisão; se a banca questionar ("dependência" vs. mera evasão), a defesa está na redação da US-09. O teste de leitura com o Pedro é o único QA da legibilidade.
- **EP-04:** técnico — mapa interativo offline no Streamlit é o sumidouro clássico de horas; o guard-rail de 1 dia na US-12 é a melhor defesa do backlog.
- **EP-05:** operacional — caminho crítico humano: US-16 depende de 4 stories técnicas E do Pedro (não-técnico, assíncrono). Se as PAs atrasarem, a narrativa espreme na janela 05–06/08.
- **EP-06:** técnico — "máquina limpa" testada em venv novo na mesma máquina pode esconder dependência de sistema (leitura de parquet, geopandas); a task já prevê "segunda máquina", manter.
- **EP-07:** nenhum risco relevante — corretamente isolado como válvula de escape.

**Devil's advocate**
- **Causa mais provável de fracasso:** compressão de prazo — 61 pts P0/P1 em ~60h de dupla com só metade técnica; um estouro em US-08 ou US-12 come a folga de ensaio (05–06/08), e a demo sem ensaio é onde P3 morre.
- **Requisito mais arriscado / mal definido:** RNF-02 (< 10s / < 3s) — metas fixadas "por bom senso, não por medição" (admitido no próprio PRD); só serão testadas de verdade na US-11, tarde no cronograma.
- **Suposição mais frágil do PRD:** o aceite formal do professor (G-4) — único ponto de falha total; segunda mais frágil: malha de regiões de saúde obtenível e não-ambígua.
- **Backlog resolve o problema certo?** Sim — cada story entrega um resultado analítico verificável que alimenta diretamente a rubrica P3 (viabilidade, análise consolidada, comunicação, reprodutibilidade); não há story de "feature pela feature".
- **Complexidade desnecessária a cortar antes do build?** Nenhuma estrutural. O único candidato a corte sob pressão já está identificado e ordenado: EP-07 primeiro, depois degradação do mapa (US-12), depois — se o achado 2 for acatado — degradação da PA-5.

## Próximo passo
**APROVADO** → governança fechada; projeto pronto para desenvolvimento (`/app-build`). Recomenda-se endereçar os avisos 1–3 (anotação no PRD, guard-rail da US-08, formalização com o professor) sem re-rodar nenhum gate — nenhum é bloqueante.
