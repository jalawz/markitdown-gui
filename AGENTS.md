# AGENTS.md

Diretrizes para agentes de IA (e pessoas) trabalhando neste repositório.

Este arquivo serve quatro propósitos:

1. **Contexto** — entender a arquitetura e as decisões já tomadas
2. **Estado** — saber o que já está pronto e o que falta
3. **Guardrails** — o que não quebrar e por quê
4. **Backlog** — melhorias sugeridas, priorizadas e com critério de aceite

---

## 0. Retomando o trabalho (leia primeiro)

**Repositório:** https://github.com/jalawz/markitdown-gui
**Branch principal:** `main` · **Última release:** `v1.1.0` · **Versão no código:** `APP_VERSION = "1.1.0"`

### Estado atual

| Item | Status |
|---|---|
| Aplicação GUI (arquivo único, multiplataforma) | ✅ pronto |
| Testes automatizados | ✅ 40 testes, CI verde |
| CI (ruff + mypy + pytest) | ✅ 9/9 jobs, matriz 3 SOs × 4 Pythons |
| Release com binários standalone | ✅ v1.1.0 publicada (Windows/Linux/macOS) |
| Documentação | ✅ README, CONTRIBUTING, SECURITY, docs/PLATFORMS.md |
| **Backlog P0/P1/P2** | ⬜ **não iniciado — comece por 5.1** |

### Checklist para retomar

```bash
git clone https://github.com/jalawz/markitdown-gui.git
cd markitdown-gui
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements-dev.txt
pytest tests/ -q          # deve passar 40/40
```

Depois, escolha **um** item do backlog (seção 5) e:

1. Crie a branch: `git checkout -b feature/<nome>`
2. Implemente seguindo os guardrails (seção 3)
3. Rode o checklist da seção 3.2
4. Atualize a seção 5 e o `README.md`
5. Abra o PR

### Comandos de referência

```bash
# Testes
pytest tests/ -q                      # suite completa
pytest tests/ -k conversion -v        # so uma area

# Qualidade
ruff check .                          # lint
ruff format .                         # formata
mypy markitdown_gui.py                # tipos
pre-commit run --all-files            # tudo junto

# Executar
python markitdown_gui.py                          # GUI
python markitdown_gui.py a.pdf b.md --auto        # abre e converte
python markitdown_gui.py a.pdf b.md --no-gui      # modo batch

# Release (apos merge em main)
git tag -a v1.2.0 -m "v1.2.0" && git push origin v1.2.0
```

### Registro de progresso

| Arquivo | Funcao |
|---|---|
| `CHANGELOG.md` | O que mudou em cada versao (atualize a secao "Nao publicado") |
| `AGENTS.md` secao 5 | Status de cada item do backlog |
| `AGENTS.md` secao 0 | Estado geral e armadilhas conhecidas |
| `docs/PLATFORMS.md` | Diferencas por sistema operacional |

**Sempre atualize o `CHANGELOG.md` junto com o codigo.** Ele e o registro
do que ja foi feito -- sem ele, a proxima sessao nao sabe o que restou.

### Armadilhas conhecidas (aprendidas na marra)

Estas quebraram o projeto de verdade. Nao repita:

| Armadilha | Sintoma | Solucao |
|---|---|---|
| `root.update()` no macOS | trava o CI indefinidamente | usar `run_until()` (ver 5.12) |
| `root.update_idletasks()` | **nao** executa `after(0, ...)` | usar `mainloop()` + polling |
| `zip` no Git Bash (Windows) | `zip: command not found` | `python scripts/package.py` |
| `\` continuacao de linha | quebra no pwsh (Windows) | comando em linha unica |
| `pady=(18, 4)` em `Frame` | `TclError: bad screen distance` | `pady` escalar; tupla so em `grid` |
| `grid` e `pack` no mesmo pai | layout colapsa sem erro | use **um** gerenciador por pai |
| `from pathlib import Path` faltando no subprocesso | `NameError: name 'Path'` | nao use subprocesso |
| emoji em `print` | `UnicodeEncodeError` no `cp1252` | ASCII puro em output de console |
| `sys.platform == "Windows"` | nunca casa (e `win32`) | use os valores reais de `sys.platform` |

---

## 1. O que é este projeto

Uma GUI de arquivo unico (`markitdown_gui.py`) que envolve o
[MarkItDown](https://github.com/microsoft/markitdown) para converter documentos
em Markdown.

**Restricao estrutural:** o projeto e intencionalmente **um unico arquivo Python**
sem dependencias alem do `tkinter` (stdlib) e do `markitdown`. Isso o torna
facil de copiar, compartilhar e executar em qualquer maquina. Antes de quebrar
essa restricao, pesquise as alternativas na secao 4.

---

## 2. Arquitetura atual

### 2.1. Modulos de nivel superior

| Modulo | Responsabilidade |
|---|---|
| `pick_font_family()` | Escolhe a primeira fonte disponivel para a plataforma |
| `enable_windows_dpi_awareness()` | Evita serrilhado em telas 4K |
| `enable_windows_dark_titlebar()` | Barra de titulo escura no Windows 10/11 |
| `pip_install_hint()` | Comando de instalacao adaptado ao SO |
| `open_in_file_manager()` | Abre o arquivo/pasta no gerenciador do SO |
| `parse_args()` | Separa posicionais de `--auto` / `--no-gui` |
| `main()` | Ponto de entrada; modo batch ou GUI |

### 2.2. Classe `MarkItDownGUI`

```
__init__            -> constroi UI, aplica args, opcionalmente auto-inicia
_build_ui           -> hierarquia de widgets (pack, nunca grid no root)
_bind_keys          -> atalhos de teclado
_apply_cli_args     -> pre-preenche origem/destino

browse_file         -> seletor de arquivo (24 formatos)
browse_dest         -> seletor de destino (.md)
convert_file        -> valida, prepara e despacha a thread de conversao

_worker             -> executa a conversao FORA da thread principal
  _set_status       -> status label
  _log              -> painel de registro (info/ok/erro)
  _ui_call          -> despachante thread-safe para a thread principal

reset_all           -> limpa os campos
open_output         -> abre a pasta do resultado
on_closing          -> confirmacao se houver conversao em andamento
```

### 2.3. O padrao `_ui_call`

**Regra inviolavel:** nenhuma funcao `_worker` (ou qualquer funcao executada em
thread secundaria) pode tocar widgets do Tkinter diretamente.

```python
# CERTO
self._ui_call(lambda: self.open_btn.config(state="normal"))

# ERRADO
self.open_btn.config(state="normal")
```

Por que: o Tkinter nao e thread-safe. Chamar `config()` de outra thread pode
causar travamentos, `RuntimeError: main thread is not in main loop` ou
excecoes silenciosas intermitentes.

`_ui_call` encapsula tres protecoes:

1. `root.after(0, func)` -- agenda na thread principal
2. `try/except (RuntimeError, tk.TclError)` -- ignora se a janela foi destruida
3. `threading.Lock` + flag `_closed` -- evita corrida no fechamento

### 2.4. Decisoes ja tomadas (nao rever sem motivo forte)

| Decisao | Alternativa descartada | Motivo |
|---|---|---|
| Sem subprocesso | `python -c "..."` | Era a causa do `NameError: Path`; `python` do PATH podia ser outro interpretador |
| `pack()` no root | `grid()` | `grid` no root com colunas desbalanceadas colapsa o layout em alguns TK builds |
| Import tardio do MarkItDown | Import no topo | `magika` carrega um modelo; o import no topo atrasa a abertura da janela em ~2s |
| `pathlib` | `os.path` | Portabilidade e clareza |
| Sem emoji em `print` | Emoji decorativo | `cp1252` no Windows quebra com `UnicodeEncodeError` |
| Threads com `daemon=True` | Threads nao-daemon | O processo nao pode ficar preso se o usuario fechar a janela |
| `run_until()` nos testes | `root.update()` | `update()` trava no macOS; `update_idletasks()` nao dispara `after(0)` |
| `scripts/package.py` | comando `zip` | `zip` nao existe no Git Bash do Windows |

---

## 3. Guardrails

### 3.1. Regras de codigo

- **Portabilidade e obrigatoria.** Qualquer PR que quebre em Linux ou macOS
  sera rejeitado. Verifique `sys.platform` em vez de assumir Windows.
- **Nunca usar `grid()` e `pack()` no mesmo widget pai.** Misturar os dois
  gerenciadores de geometria no mesmo pai causa comportamento indefinido.
- **Strings em UTF-8 explicito** em qualquer `open()`, `write_text()` ou
  `read_text()`.
- **Sem caminhos absolutos** de nenhum SO no codigo.
- **Sem `print` com caracteres nao-ASCII** (emoji, acentos) em codigo que
  possa rodar em console `cp1252`.
- **Acrescente encoding explicito** ao abrir arquivos; nunca dependa do default.

### 3.2. Antes de enviar PR

```bash
pytest tests/ -v      # testes passam
ruff check .          # lint limpo
ruff format .         # formatacao aplicada
mypy markitdown_gui.py  # sem erros de tipo
```

O CI valida isso automaticamente em 3 SOs x 4 versoes do Python.

### 3.3. Compatibilidade

| Item | Minimo |
|---|---|
| Python | 3.10 |
| tkinter | 8.6+ |
| markitdown | 0.1.9 |

---

## 4. Alternativas ao arquivo unico

So considere quebrar o arquivo unico se **todas** as opcoes abaixo falharem:

| Opcao | Ganho | Custo |
|---|---|---|
| Manter 1 arquivo | portabilidade maxima | arquivo cresce (~700 linhas) |
| Pacote `src/markitdown_gui/` | importavel, testavel | muda a forma de uso |
| Multiplos modulos no mesmo dir | legibilidade | `sys.path` hack nos testes |

Se decidir empacotar, mantenha `markitdown_gui.py` na raiz como **wrapper
compativel** para nao quebrar quem ja usa.

---

## 5. Backlog de melhorias

Prioridade: alta · media · baixa
Legenda: ✅ feito · ⬜ pendente · 🚧 em andamento

### P0 — Funcionalidade essencial

#### 5.1 Arrastar e soltar arquivos  ⬜

O usuario espera arrastar o PDF para a janela.

- **Solucao:** `tkinterdnd2` (opcional, degrade graciosamente se ausente)
- **Aceite:** arrastar 1 arquivo preenche origem + sugere destino; multiplos
  arquivos disparam conversao em lote
- **Risco:** `tkinterdnd2` traz um Tcl patch que pode conflitar com o Tk do
  sistema. Testar em 3 SOs antes de merge.

#### 5.2 Conversao em lote / fila  ⬜

- **Solucao:** lista de tarefas, converter varios de uma vez
- **Aceite:** N arquivos -> N saidas; um erro em um nao interrompe os demais;
  log mostra `2/10 concluido`
- **Dependencia:** refatorar `_worker` para aceitar uma fila
- **Atalho:** resolve parte de 5.1

#### 5.3 Cancelamento  ⬜

- **Solucao:** `threading.Event` compartilhado, verificado entre etapas
- **Aceite:** botao "Cancelar" aparece durante a conversao; ao cancelar, o
  arquivo parcial **nao** e salvo e o status mostra "Cancelado"
- **Nota:** `MarkItDown.convert()` nao e cancelavel — o cancelamento so tem
  efeito entre arquivos (na fila) ou apos a etapa atual

#### 5.4 Progresso real (percentual)  ⬜

- **Solucao:** converter a cada pagina via `pdfplumber` para estimar
- **Aceite:** barra deterministica com `%` real em PDFs multi-pagina
- **Risco:** exige hook no conversor do MarkItDown ou reimplementacao local

#### 5.5 Topicos em portugues  ⬜

Hoje todas as strings estao fixas em portugues no codigo.

- **Solucao:** `gettext` com `locale.setlocale()`; PT-BR e EN
- **Aceite:** `LANG=pt_BR` mostra portugues, `LANG=en_US` mostra ingles
- **Risco:** strings com acento precisam de encoding correto em `.po`

---

### P1 — Qualidade de vida

#### 5.6 Preview antes de salvar  ⬜

- **Solucao:** `ScrolledText` read-only com os primeiros N caracteres
- **Aceite:** botao "Visualizar" abre um dialogo com o Markdown

#### 5.7 Lembrar diretorios  ⬜

- **Solucao:** `~/.config/markitdown-gui/config.json` (XDG no Linux,
  `%APPDATA%` no Windows, `~/Library/Application Support` no macOS)
- **Aceite:** reabrir o app restaura origem e destino anteriores
- **Risco:** validar o JSON para nao quebrar por arquivo corrompido

#### 5.8 Acoes de clipboard  ⬜

- Copiar caminho do arquivo de origem
- Copiar caminho do destino
- Copiar todo o Markdown gerado
- Abrir o Markdown no editor padrao

#### 5.9 Metadados em YAML front matter  ⬜

O Azure Content Understanding ja emite front matter. Padronizar localmente:

```markdown
---
title: Go Programming
source: livro.pdf
pages: 2124
converted_at: 2026-11-12T10:30:00
converter: markitdown-gui 1.1.0
---
```

- **Aceite:** toggle na UI; front matter ausente quando desmarcado

#### 5.10 Temas claro/escuro  ⬜

- **Solucao:** dict de cores + deteccao de `ttk` theme do SO
- **Aceite:** seguir a preferencia do sistema por padrao

#### 5.11 Acessibilidade  ⬜

- Navegacao completa por teclado (Tab order)
- `underline` nos mnemonicos dos campos
- Textos dos widgets com `name` descritivo
- Verificar contraste >= 4.5:1 (WCAG AA)

#### 5.12 Testes automatizados  🚧 parcial

**Ja feito:** 40 testes em `tests/test_gui.py`, rodando no CI em 3 SOs x 4
versoes do Python.

**Falta:**

- [ ] `_worker` com `ImportError` (markitdown ausente)
- [ ] `_worker` com excecao generica (arquivo corrompido)
- [ ] Fechar a janela durante a conversao **nao** deixa thread orfa
- [ ] `pip_install_hint` parametrizado por plataforma (monkeypatch de `sys.platform`)
- [ ] `open_in_file_manager` por plataforma (monkeypatch de `subprocess.Popen`)
- [ ] Cobertura >= 70% em `markitdown_gui.py` (rodar `pytest --cov`)

> **Dica para agentes:** ao testar a GUI, use o helper `run_until()` de
> `tests/test_gui.py`. Ele roda o event loop real (`mainloop()`) com polling e
> encerra com `quit()`.
>
> **Armadilha do macOS:** `root.update()` **trava** no macOS, porque o
> `update` completo do Tcl processa a fila de Apple Events e bloqueia esperando
> eventos do sistema. Use **sempre** `run_until()`.
>
> **Segunda armadilha:** `root.update_idletasks()` **nao** executa timers
> `after(0, ...)` — que e exatamente o mecanismo usado por `_ui_call`. Por
> isso `update_idletasks()` tambem nao serve. `mainloop()` + polling resolve
> os dois casos.

---

### P2 — Polish

#### 5.13 Empacotamento standalone  ✅

- **Feito:** `.github/workflows/release.yml` + `scripts/package.py`
- **Resultado:** binarios publicados na release v1.1.0
  (Windows 110 MB, Linux 131 MB, macOS 105 MB)
- **Restante:** avaliar `--onedir` ou `--exclude-module` para reduzir o tamanho
  (o `magika` carrega modelo ONNX)

#### 5.14 Internationalizacao completa  ⬜

- **Solucao:** `gettext` + `babel`
- **Aceite:** PRs de traducao aceitos via Crowdin

#### 5.15 Painel de pre-visualizacao do Markdown  ⬜

- **Solucao:** `tkhtml` ou `Text` com renderizacao simples
- **Aceite:** preview lado a lado enquanto converte

#### 5.16 Integracao com explorador de arquivos  ⬜

- **Solucao:** `tkinterdnd2` + extensao de shell para Windows
- **Aceite:** "Converter com MarkItDown GUI" no menu de contexto

#### 5.17 Suporte a configuracoes remotas do MarkItDown  ⬜

- **Solucao:** ler `MARKITDOWN_DOCINTEL_ENDPOINT` e afins, exibir status
- **Aceite:** a UI indica quando Azure Doc Intel esta configurado e pronto

---

## 6. Como contribuir com este arquivo

Ao implementar um item do backlog:

1. Marque o item com ✅ (ou 🚧 se parcial) e liste o que falta
2. Atualize a tabela "Estado atual" na secao 0 se o status geral mudou
3. Atualize o `README.md` se o comportamento visivel mudou
4. Adicione um teste em `tests/test_gui.py`
5. Atualize o numero da versao em `APP_VERSION` e no `pyproject.toml`

Se encontrar uma armadilha nova (bug que travou CI, erro de encoding,
incompatibilidade entre SOs), **adicione-a na tabela da secao 0** — e o que
mais vai economizar tempo na proxima sessao.

---

## 7. Referencias

- [MarkItDown (Microsoft)](https://github.com/microsoft/markitdown) — a biblioteca subjacente
- [MarkItDown GUI](https://github.com/jalawz/markitdown-gui) — este repositorio
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — toolkit da GUI
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) — drag and drop
- [PyInstaller](https://pyinstaller.org/) — empacotamento
- [WCAG 2.1](https://www.w3.org/TR/WCAG21/) — acessibilidade
