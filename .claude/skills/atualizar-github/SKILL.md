---
name: atualizar-github
description: Ritual de fim de sessão do projeto-saude — atualiza o STATUS.md em linguagem leiga pro Pedro, commita e dá push. Use ao encerrar qualquer sessão de trabalho, quando o usuário pedir pra "atualizar o GitHub", "fechar a sessão", "dar push", ou quando houver trabalho feito ainda não commitado.
---

# Atualizar GitHub — ritual de fim de sessão

Regra do projeto: **sessão sem push = sessão que não existiu.** Esta skill executa o fechamento no padrão combinado.

## Passos

### 1. Levantar o que mudou
- `git status` + `git diff --stat` para ver o estado.
- Recapitular da conversa o que foi feito NESTA sessão e por quê (é o insumo do STATUS.md).

### 2. Atualizar `STATUS.md` (o coração do ritual)
O STATUS.md é a **referência do Pedro** — ele não é técnico, não participa das conversas com agentes, e lê isso como única fonte do estado do projeto. Regras invioláveis:

- **Linguagem leiga, sempre.** Zero jargão interno (smoke test, parquet, EDA, pipeline, O-D, PRD, backlog…) sem explicação em UMA frase no próprio texto, na primeira ocorrência. Ex.: "parquet (um formato de arquivo que guarda os dados prontos pra análise)".
- Explicar cada passo em linguagem natural, como se contasse pra alguém de fora **o que** foi feito e **por quê**. Compreensível na primeira leitura.
- Estrutura existente do arquivo (manter):
  - Cabeçalho com instrução de Pull → ler.
  - **"Onde estamos (DD/MM/AAAA)"** — atualizar a data e o retrato do projeto.
  - **"O que aconteceu na última sessão (DD/MM/AAAA)"** — substituir pelo desta sessão.
  - **"Pra você, Pedro"** — SEMPRE atualizar: o que ele pode/deve fazer agora, com passos concretos (comandos prontos pra copiar, nomes de arquivo exatos). Se nada mudou pra ele, dizer isso explicitamente.
  - **"Combinados"** — só mexer se um combinado mudou.
- Decisão importante tomada na sessão → registrar no STATUS.md (combinado do projeto).

### 3. Conferir o que entra no git
- Parquets congelados (`data/raw/*.parquet`) **são versionados** — Pedro clona e já tem os dados.
- `.dbc`/`.dbf` ficam **fora** do git (conferir que não estão staged; se aparecerem, checar o `.gitignore`).
- Nunca commitar rascunho/temporário de agente.

### 4. Commit
Mensagens de commit **também são interface com o Pedro** — ele lê o histórico:
- Descrever só O QUE mudou no projeto, tom neutro, pt-BR.
- **Nunca** meta-comentário sobre linguagem/didática ("linguagem leiga"), IA, agentes, skills, ou decisões internas das conversas.
- **Nunca** adicionar co-autoria de IA (sem `Co-Authored-By`).
- Uma sessão = um commit (ou poucos, por tema), não um commit por arquivo.

### 5. Push e verificação
- `git push` para `main` (Pedro não usa branch).
- Confirmar que o push subiu (`git status` limpo e à frente de nada).
- Reportar ao usuário: o que foi commitado + confirmação do push.

## Checklist final (antes de encerrar)
- [ ] STATUS.md com data de hoje e seção "Pra você, Pedro" atualizada
- [ ] STATUS.md sem jargão não explicado (reler com olhos de leigo)
- [ ] Nada de `.dbc`/`.dbf` no commit
- [ ] Mensagem de commit neutra, sem meta-comentário, sem co-autoria
- [ ] Push confirmado em `main`
