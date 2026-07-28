# Comece aqui — como rodar o painel na sua máquina

Este guia é para quem nunca rodou o projeto. Ele vai do zero (máquina limpa) até o painel aberto no navegador.

**Tempo:** ~15 minutos na primeira vez. Depois, 10 segundos toda vez.

Você não precisa saber programar para seguir isto. É copiar comando, colar, apertar Enter e conferir se apareceu o que está escrito em "**Você deve ver**". Se aparecer outra coisa, pule para [Deu erro?](#deu-erro) no fim — os cinco erros possíveis estão lá com a solução.

---

## Antes de tudo: o que é cada coisa

Três nomes aparecem o tempo todo aqui. Em uma frase cada:

- **Terminal** (ou PowerShell): a janela preta onde você digita comandos. É por ela que o projeto é ligado.
- **Python**: a linguagem em que o projeto foi escrito. Precisa estar instalada na máquina para o projeto rodar.
- **Streamlit**: a ferramenta que transforma a análise em um site. O "painel" é isso — um site que roda **na sua própria máquina**, não na internet.

---

## Passo 1 — Ter o Python instalado

**Só na primeira vez.** Se você já usou Python nessa máquina, pule para o passo 2.

Abra o **PowerShell**: tecla Windows → digite `powershell` → Enter.

Cole isto e aperte Enter:

```powershell
python --version
```

**Você deve ver:** `Python 3.13.3` (ou qualquer número a partir de `3.11`).

**Se apareceu outra coisa** (erro, ou abriu a Microsoft Store): você não tem Python. Instale:

1. Vá em <https://www.python.org/downloads/>
2. Clique no botão amarelo grande (baixa a versão mais nova).
3. Rode o instalador. **Na primeira tela, marque a caixinha `Add python.exe to PATH`** antes de clicar em Install. Essa caixinha é a diferença entre funcionar e não funcionar — se esquecer, o terminal não acha o Python depois.
4. Terminado, **feche o PowerShell e abra de novo** (ele só enxerga o Python novo em uma janela nova) e repita o `python --version`.

---

## Passo 2 — Ter o projeto na máquina, atualizado

No **GitHub Desktop**, com o repositório `projeto-saude` selecionado:

- Se é a primeira vez: **File → Clone repository** e escolha o projeto.
- Se já está clonado: clique em **Fetch origin** e depois em **Pull origin** (se aparecer).

Isso garante que você tem a versão mais recente — inclusive os dados, que vêm junto no projeto.

**Anote onde a pasta ficou.** O GitHub Desktop mostra o caminho em **Repository → Show in Explorer**. Normalmente é algo como `C:\Users\SEU-NOME\Documents\GitHub\projeto-saude-pb`.

> **Existe um segundo repositório**, o `projeto-saude-pb-workspace`, com o cronograma de estudo e a lista de tarefas. Ele não é necessário para rodar o painel — mas você vai precisar dele para estudar. Veja [Os dois repositórios](#os-dois-repositórios) mais abaixo.

---

## Passo 3 — Abrir o terminal *dentro da pasta do projeto*

Este é o passo que mais dá errado, e por um motivo bobo: o terminal abre por padrão em outra pasta, e aí nenhum comando acha os arquivos do projeto.

**Jeito mais fácil (recomendado):** no GitHub Desktop, menu **Repository → Open in PowerShell** (dependendo da versão, aparece como *Open in Command Prompt* ou *Open in Terminal* — serve igual). Ele abre a janela já na pasta certa.

**Se esse menu não existir:** abra a pasta do projeto no Explorador de Arquivos, clique na barra de endereço no topo, apague o que está escrito, digite `powershell` e aperte Enter.

**Para conferir que está no lugar certo**, cole:

```powershell
dir app.py
```

**Você deve ver:** uma linha com `app.py` e o tamanho do arquivo.
**Se disser que não encontrou:** o terminal está na pasta errada. Volte e refaça este passo.

---

## Passo 4 — Preparar o ambiente

**Só na primeira vez.** São três comandos, um de cada vez, na ordem.

O que estamos fazendo aqui: criando uma "caixa" só deste projeto (chamada `.venv`) e instalando dentro dela as ferramentas que o projeto usa. A caixa existe para que o projeto não bagunce nada mais da sua máquina, e para que a versão instalada seja exatamente a mesma testada — hoje e daqui a seis meses.

**4.1 — Criar a caixa:**

```powershell
python -m venv .venv
```

**Você deve ver:** nada. Alguns segundos parado e o cursor volta. Nenhuma mensagem = deu certo.

**4.2 — Entrar na caixa:**

```powershell
.venv\Scripts\Activate.ps1
```

**Você deve ver:** `(.venv)` apareceu no começo da linha do terminal, assim:

```
(.venv) PS C:\Users\pedro\Documents\GitHub\projeto-saude>
```

Esse `(.venv)` é o sinal de que você está dentro da caixa. **Sem ele, os comandos seguintes não funcionam.**

> **Se deu erro vermelho falando em `execution policy` / "não é possível carregar o arquivo":** é uma trava padrão do Windows, não é problema do projeto. Cole isto, aperte Enter, e repita o comando 4.2:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> Isso libera só esta janela do terminal, e só até você fechá-la. Não muda nada no resto do computador.

**4.3 — Instalar as ferramentas:**

```powershell
pip install -r requirements.txt
```

**Você deve ver:** várias linhas rolando (`Collecting...`, `Downloading...`, barras de progresso) por 2 a 5 minutos, terminando em uma linha `Successfully installed` com uma lista longa de nomes.

Avisos amarelos escritos `WARNING` são normais — pode ignorar. Só linha vermelha com `ERROR` é problema.

---

## Passo 5 — Abrir o painel

```powershell
streamlit run app.py
```

**Você deve ver:** o navegador abrir sozinho em `http://localhost:8501` com o painel. No terminal fica escrito `You can now view your Streamlit app in your browser`.

Se o navegador não abrir sozinho, copie `http://localhost:8501` e cole na barra de endereço.

**Enquanto o painel estiver aberto, o terminal fica ocupado** — é normal, ele está segurando o painel no ar. Não feche essa janela.

**Para fechar o painel:** clique no terminal e aperte `Ctrl + C`.

---

## Voltando depois — a rotina do dia a dia

Da segunda vez em diante, o passo 4 nunca mais se repete. É só isto:

```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```

(Sempre com o terminal aberto na pasta do projeto — passo 3.)

Antes de começar, vale dar um **Pull** no GitHub Desktop para pegar as novidades.

---

## Quero mexer nos dados, não só ver o painel

Mesma preparação (passos 1 a 4), e então:

```powershell
jupyter notebook
```

Abre no navegador uma lista de pastas. Entre em `notebooks/` e abra **`90-eda-guiada.ipynb`** — é um roteiro comentado em português, do básico até as 16 regiões de saúde, feito para explorar sem precisar saber o que está acontecendo por trás.

Combinado do projeto: os notebooks que começam com `90-` são seus. Crie os seus com esse começo (ex.: `90-eda-pedro.ipynb`) e nunca edite os que começam com `01-` — assim o GitHub nunca reclama de conflito entre nós dois.

---

## Deu erro?

| O que apareceu na tela | O que está acontecendo | O que fazer |
|---|---|---|
| `python : O termo 'python' não é reconhecido` | O Windows não sabe onde o Python está. Quase sempre é a caixinha `Add python.exe to PATH` que ficou desmarcada na instalação. | Reinstale o Python pelo passo 1, marcando a caixinha. Feche e reabra o terminal depois. |
| `não é possível carregar o arquivo ... Activate.ps1` (menção a `execution policy`) | Trava padrão do Windows contra scripts. | Cole `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, Enter, e repita o comando que falhou. |
| `streamlit : O termo 'streamlit' não é reconhecido` | Você não está dentro da caixa `.venv`. | Confira se tem `(.venv)` no começo da linha. Se não tiver, rode o passo 4.2. Se tiver e mesmo assim falhou, rode o passo 4.3. |
| `Port 8501 is already in use` | O painel já está aberto em outra janela de terminal. | Ou use a que já está aberta, ou feche a outra janela e tente de novo. |
| `dir app.py` não encontra nada / `No such file or directory` | O terminal está em outra pasta. | Refaça o passo 3. |
| Painel abre mas dá erro dentro da página | Provavelmente dados desatualizados na sua cópia. | **Pull** no GitHub Desktop e rode de novo. Se persistir, manda print pro Augusto. |

Qualquer erro fora dessa tabela: tira print da tela inteira (terminal incluído) e manda no WhatsApp. Não perca tempo caçando — a maior parte é configuração de máquina, resolve em dois minutos a dois.

---

## Os dois repositórios

O trabalho está dividido em dois repositórios no GitHub. Eles são independentes: cada um vira uma pasta separada na sua máquina, e cada um tem o seu próprio Pull.

| | `projeto-saude-pb` | `projeto-saude-pb-workspace` |
|---|---|---|
| **O que é** | O projeto em si | A coordenação entre nós dois |
| **O que tem dentro** | Código, dados, painel, relatórios, `STATUS.md` | Cronograma de estudo, lista de tarefas |
| **Quem vê** | Público — é o que o professor abre | Privado — só nós dois |
| **Você precisa dele para** | Rodar o painel, explorar os dados | Estudar até 07/08 |

Por isso os planos de estudo não estão junto do projeto: o repositório do projeto é público, e o material de coordenação interna não precisa estar à vista de quem vai avaliar o trabalho.

**Para clonar o segundo (uma vez só):** GitHub Desktop → **File → Clone repository** → aba **GitHub.com** → escolha `projeto-saude-pb-workspace` → Clone. Se ele não aparecer na lista, clique em **Fetch** / recarregue — você foi adicionado como colaborador, então ele tem que estar lá. Se mesmo assim não aparecer, me avisa.

Dentro dele, o que interessa a você:

- **`docs/plano-estudos-pedro.md`** — seu cronograma de 10 dias até a apresentação. É por aqui que você começa.
- `docs/plano-estudos.md` — o plano mestre, que explica a lógica da divisão entre nós dois.
- `TASKS.md` — a lista de tarefas técnicas. Pode ignorar.

**Atenção ao trocar de pasta:** os comandos deste guia (`streamlit`, `jupyter`) só funcionam dentro da pasta do `projeto-saude-pb`. O outro repositório tem só textos — nada para rodar.

---

## Cartão de bolso

```powershell
# 1. Terminal na pasta do projeto (GitHub Desktop → Repository → Open in PowerShell)

# 2. Entrar na caixa
.venv\Scripts\Activate.ps1

# 3. Abrir o painel
streamlit run app.py

# Fechar: Ctrl + C no terminal
```

---

**Onde está cada coisa:**
- [`STATUS.md`](STATUS.md) — o que mudou no projeto e o que fazer agora. Seu arquivo de referência, leia sempre depois do Pull.
- [`README.md`](README.md) — descrição técnica do projeto (para a apresentação e para o professor).
- [`reports/narrativa-executiva.md`](reports/narrativa-executiva.md) — o texto da apresentação em uma página.
- `docs/plano-estudos-pedro.md` — cronograma de estudo até 07/08. **Fica no outro repositório** (`projeto-saude-pb-workspace`) — veja [Os dois repositórios](#os-dois-repositórios).
