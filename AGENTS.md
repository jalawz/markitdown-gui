# AGENTS.md

Diretrizes para agentes de IA (e pessoas) trabajando neste repositório.

Este arquivo serve três propósitos:

1. **Contexto** — entender a arquitetura e as decisões já tomadas
2. **Guardrails** — o que não quebrar e por quê
3. **Backlog** — melhorias sugeridas, priorizadas e com critério de aceite

---

## 1. O que é este projeto

Uma GUI de arquivo único (`markitdown_gui.py`) que envolve o
[MarkItDown](https://github.com/microsoft/markitdown) para converter documentos
em Markdown.

**Restrição estrutural:** o projeto é intencionalmente **um único arquivo Python**
sem dependências além do `tkinter` (stdlib) e do `markitdown`. Isso o torna
fácil de copiar, compartilhar e executar em qualquer máquina. Antes de quebrar
essa restrição, pesquise as alternativas na seção 4.

---

## 2. Arquitetura atual

### 2.1. Módulos de nível superior

| Módulo | Responsabilidade |
|---|---|
| `pick_font_family()` | Escolhe a primeira fonte disponível para a plataforma |
| `enable_windows_dpi_awareness()` | Evita serrilhado em telas 4K |
| `enable_windows_dark_titlebar()` | Barra de título escura no Windows 10/11 |
| `pip_install_hint()` | Comando de instalação adaptado ao SO |
| `open_in_file_manager()` | Abre o arquivo/pasta no gerenciador do SO |
| `parse_args()` | Separa posicionais de `--auto` / `--no-gui` |
| `main()` | Ponto de entrada; modo batch ou GUI |

### 2.2. Classe `MarkItDownGUI`

```
__init__            → constrói UI, aplica args, opcionalmente auto-inicia
_build_ui           → hierarquia de widgets (pack, nunca grid no root)
_bind_keys          → atalhos de teclado
_apply_cli_args     → pré-preenche origem/destino

browse_file         → seletor de arquivo (24 formatos)
browse_dest         → seletor de destino (.md)
convert_file        → valida, prepara e despacha a thread de conversão

_worker             → executa a conversão FORA da thread principal
  _set_status       → status label
  _log              → painel de registro (info/ok/erro)
  _ui_call          → despachante thread-safe para a thread principal

reset_all           → limpa os campos
open_output         → abre a pasta do resultado
on_closing          → confirmação se houver conversão em andamento
```

### 2.3. O padrão `_ui_call`

**Regra inviolável:** nenhuma função `_worker` (ou qualquer função executada em
thread secundária) pode tocar widgets do Tkinter diretamente.

```python
# CERTO
self._ui_call(lambda: self.open_btn.config(state="normal"))

# ERRADO
self.open_btn.config(state="normal")
```

Por quê: o Tkinter não é thread-safe. Chamar `config()` de outra thread pode
causar travamentos, `RuntimeError: main thread is not in main loop` ou
exceções silenciosas intermitentes.

`_ui_call` encapsula três proteções:

1. `root.after(0, func)` — agenda na thread principal
2. `try/except (RuntimeError, tk.TclError)` — ignora se a janela foi destruída
3. `threading.Lock` + flag `_closed` — evita corrida no fechamento

### 2.4. Decisões já tomadas (não rever sem motivo forte)

| Decisão | Alternativa descartada | Motivo |
|---|---|---|
| Sem subprocesso | `python -c "..."` | Era a causa do `NameError: Path`; `python` do PATH podia ser outro interpretador |
| `pack()` no root | `grid()` | `grid` no root com colunas desbalanceadas colapsa o layout em alguns TK builds |
| Import tardio do MarkItDown | Import no topo | `magika` carrega um modelo; o import no topo atrasa a abertura da janela em ~2s |
| `pathlib` | `os.path` | Portabilidade e clareza |
| Sem emoji em `print` | Emoji decorativo | `cp1252` no Windows quebra com `UnicodeEncodeError` |
| Threads com `daemon=True` | Threads não-daemon | O processo não pode ficar preso se o usuário fechar a janela |

---

## 3. Guardrails

### 3.1. Regras de código

- **Portabilidade é obrigatória.** Qualquer PR que quebre em Linux ou macOS
  será rejeitado. Verifique `sys.platform` em vez de assumir Windows.
- **Nunca usar `grid()` e `pack()` no mesmo widget pai.** Misturar os dois
  gerenciadores de geometria no mesmo pai causa comportamento indefinido.
- **Strings em UTF-8 explícito** em qualquer `open()`, `write_text()` ou
  `read_text()`.
- **Sem caminhos absolutos** de nenhum SO no código.
- **Sem `print` com caracteres não-ASCII** (emoji, acentos) em código que
  possa rodar em console `cp1252`.

### 3.2. Antes de enviar PR

```bash
pytest tests/ -v      # testes passam
ruff check .          # lint limpo
ruff format .         # formatação aplicada
mypy markitdown_gui.py  # sem erros de tipo
```

### 3.3. Compatibilidade

| Item | Mínimo |
|---|---|
| Python | 3.10 |
| tkinter | 8.6+ |
| markitdown | 0.1.9 |

---

## 4. Alternativas ao arquivo único

Só considere quebrar o arquivo único se **todas** as opções abaixo falharem:

| Opção | Ganho | Custo |
|---|---|---|
| Manter 1 arquivo | portabilidade máxima | arquivo cresce (~600 linhas) |
| Pacote `src/markitdown_gui/` | importável, testável | muda a forma de uso |
| Múltiplos módulos no mesmo dir | legibilidade | `sys.path` hack nos testes |

Se decidir empacotar, mantenha `markitdown_gui.py` na raiz como **wrapper
compatível** para não quebrar quem já usa.

---

## 5. Backlog de melhorias

Prioridade: 🔴 alta · 🟡 média · 🟢 baixa

### 🔴 P0 — Funcionalidade essencial

#### 5.1 Arrastar e soltar arquivos

O usuário espera arrastar o PDF para a janela.

- **Solução:** `tkinterdnd2` (opcional, degrade graciosamente se ausente)
- **Aceite:** arrastar 1 arquivo preenche origem + sugere destino; múltiplos
  arquivos disparam conversão em lote
- **Risco:** `tkinterdnd2` traz um Tcl patch que pode conflitar com o Tk do
  sistema. Testar em 3 SOs antes de merge.

#### 5.2 Conversão em lote / fila

- **Solução:** lista de tarefas, converter vários de uma vez
- **Aceite:** N arquivos → N saídas; um erro em um não interrompe os demais;
  log mostra `2/10 concluído`
- **Dependência:** refatorar `_worker` para aceitar uma fila

#### 5.3 Cancelamento

- **Solução:** `threading.Event` compartilhado, verificado entre etapas
- **Aceite:** botão "Cancelar" aparece durante a conversão; ao cancelar, o
  arquivo parcial **não** é salvo e o status mostra "Cancelado"
- **Nota:** `MarkItDown.convert()` não é cancelável — o cancelamento só tem
  efeito entre arquivos (na fila) ou após a etapa atual

#### 5.4 Progresso real (percentual)

- **Solução:** converter a cada página via `pdfplumber` para estimar
- **Aceite:** barra determinística com `%` real em PDFs multi-página
- **Risco:** exige hook no conversor do MarkItDown ou reimplementação local

#### 5.5 Tópicos em português

Hoje todas as strings estão fixas em português no código.

- **Solução:** `gettext` com `locale.setlocale()`; PT-BR e EN
- **Aceite:** `LANG=pt_BR` mostra português, `LANG=en_US` mostra inglês
- **Risco:** strings com acento precisam de encoding correto em `.po`

---

### 🟡 P1 — Qualidade de vida

#### 5.6 Preview antes de salvar

- **Solução:** `ScrolledText` read-only com os primeiros N caracteres
- **Aceite:** botão "Visualizar" abre um diálogo com o Markdown

#### 5.7 Lembrar diretórios

- **Solução:** `~/.config/markitdown-gui/config.json` (XDG no Linux,
  `%APPDATA%` no Windows, `~/Library/Application Support` no macOS)
- **Aceite:** reabrir o app restaura origem e destino anteriores
- **Risco:** validar o JSON para não quebrar por arquivo corrompido

#### 5.8 Ações de clipboard

- Copiar caminho do arquivo de origem
- Copiar caminho do destino
- Copiar todo o Markdown gerado
- Abrir o Markdown no editor padrão

#### 5.9 Metadados em YAML front matter

O Azure Content Understanding já emite front matter. Padronizar localmente:

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

#### 5.10 Temas claro/escuro

- **Solução:** dict de cores + detecção de `ttk` theme do SO
- **Aceite:** seguir a preferência do sistema por padrão

#### 5.11 Acessibilidade

- Navegação completa por teclado (Tab order)
- `underline` nos mnemônicos dos campos
- Textos dos widgets com `name` descritivo
- Verificar contraste ≥ 4.5:1 (WCAG AA)

#### 5.12 Testes automatizados

Hoje a cobertura é mínima.

- **Solução:** `pytest` + `pytest-mock` + `pytest-timeout`
- **Cobertura alvo:** ≥ 70% em `markitdown_gui.py`
- **Casos obrigatórios:**
  - `parse_args` com todas as combinações de flags
  - `pick_font_family` com e sem Tk root
  - `_worker` com sucesso, com `ImportError`, com exceção genérica
  - Fechar a janela durante a conversão **não** deixa thread órfã
  - `pip_install_hint` por plataforma

> **Dica para agentes:** ao testar a GUI, use `root.after(...)` + `mainloop()`.
> Chamar `root.update()` em loop não roda o event loop de verdade e o
> `root.after()` falha com `RuntimeError: main thread is not in main loop`.

---

### 🟢 P2 — Polish

#### 5.13 Empacotamento standalone

- **Solução:** PyInstaller + GitHub Actions (matriz OS × SO)
- **Aceite:** binário único, sem Python instalado no destino
- **Risco:** `magika` carrega modelo TensorFlow — o executável fica grande
  (~200MB). Avaliar `--exclude` de módulos ou usar `--onedir`

#### 5.14 Internationalização completa

- **Solução:** `gettext` + `babel`
- **Aceite:** PRs de tradução aceitos via Crowdin

#### 5.15 Painel de pré-visualização do Markdown

- **Solução:** `tkhtml` ou `Text` com renderização simples
- **Aceite:** preview lado a lado enquanto converte

#### 5.16 Integração com explorador de arquivos

- **Solução:** `tkinterdnd2` + extensão de shell para Windows
- **Aceite:** "Converter com MarkItDown GUI" no menu de contexto

#### 5.17 Suporte a configurações remotas do MarkItDown

- **Solução:** ler `MARKITDOWN_DOCINTEL_ENDPOINT` e afins, exibir status
- **Aceite:** a UI indica quando Azure Doc Intel está configurado e pronto

---

## 6. Como contribuir com este arquivo

Ao implementar um item do backlog:

1. Remova o item da seção 5 (ou marque com ✅ e a PR)
2. Atualize o `README.md` se o comportamento visível mudou
3. Adicione um teste em `tests/`
4. Atualize o número da versão em `APP_VERSION`

---

## 7. Referências

- [MarkItDown (Microsoft)](https://github.com/microsoft/markitdown) — a biblioteca subjacente
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — toolkit da GUI
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) — drag and drop
- [PyInstaller](https://pyinstaller.org/) — empacotamento
- [WCAG 2.1](https://www.w3.org/TR/WCAG21/) — acessibilidade
