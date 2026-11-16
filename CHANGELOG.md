# Changelog

Todas as mudanças relevantes deste projeto.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento seguindo [SemVer](https://semver.org/lang/pt-BR/).

---

## [Não publicado]

Próximo release a ser preparado. Use este seção para registrar o que está
em andamento antes de cortar uma versão.

### Corrigido

- **Fila de conversão avançava só o primeiro arquivo.** `_queue_index` nunca
  era incrementado e o worker não disparava o próximo item; agora cada arquivo
  concluído chama `_item_done`, que avança o índice e inicia o seguinte. Um erro
  em um arquivo não interrompe os demais e o resumo é exibido uma única vez no
  fim (antes era um `messagebox` por arquivo).
- **`Ctrl+Enter` levantava `AttributeError`.** O atalho chamava `convert_file()`,
  removido no refactor de drag-and-drop; agora chama `convert_queue()`.
- **Campos de origem/destino não existiam mais na janela.** O refactor de 5.1
  removeu os `Entry` e os botões "Procurar" e deixou `browse_file()` sem efeito
  visível; os campos voltaram, ligados a `src_var`/`dst_var`, e o drag-and-drop
  agora registra os dois (o `hasattr(self, "src_entry")` era sempre falso).
- **Destino podia sobrescrever a origem.** Abrir um `.md` sem destino gerava
  `arquivo.md -> arquivo.md` e apagava o original; `default_destination()` agora
  sugere `<nome>.converted.md` e `convert_queue` recusa origem == destino.
- **Barra de progresso usava escalas diferentes** (máximo = nº de arquivos,
  valor = 100 no fim). Agora usa uma unidade por arquivo.
- **Botões do rodapé colapsavam** com a nova altura de conteúdo: janela
  redimensionada para `760x780` (mínimo `720x680`).

### Alterado

- `_set_busy` também desabilita os campos de entrada e os botões da fila.
- Removidos `_on_success`, `_progress_complete` e `_progress_reset`, que ficaram
  sem uso depois da agregação do resumo.
- Limpezas: `columnconfigure` duplicado, comentário `# Acoes` duplicado,
  `BooleanVar` inicializada duas vezes e `_total_files` agora é usado de fato.
- **41 → 45 testes**; nova classe `TestQueue` cobre avanço da fila, erro parcial,
  cancelamento e a regressão do `Ctrl+Enter`.

---

## [1.1.0] — 2026-11-13

Primeira release estável.

### Adicionado

- **Aplicação GUI** de arquivo único (`markitdown_gui.py`) para converter
  documentos em Markdown via Microsoft MarkItDown
- **24 formatos** no seletor de arquivos: PDF, Word, PowerPoint, Excel, HTML,
  CSV, JSON, XML, TXT, MD, EPUB, Jupyter, Outlook, imagens e áudio
- **Painel de log** com cores por nível (info / ok / erro) e status em tempo real
- **Barra de progresso** que vai a 100% ao concluir
- **Botão "Abrir pasta do resultado"** com abertura no gerenciador do SO
- **Opções**: usar plugins de terceiros, manter data URIs
- **Modo batch** (`--no-gui`) para automação e scripts
- **Modo automático** (`--auto`) que converte ao abrir
- **Argumentos de linha de comando**: `arquivo.pdf saida.md`
- **Atalhos de teclado**: `Ctrl+O`, `Ctrl+S`, `Ctrl+Enter`, `Esc`
- **Portabilidade**: detecção de fonte por plataforma, DPI awareness e barra
  de título escura no Windows, gerenciador de arquivos por SO, dicas de
  instalação adaptadas ao sistema
- **40 testes automatizados** (`tests/test_gui.py`)
- **CI** com matriz de 3 SOs × 4 versões do Python, rodando ruff, mypy e pytest
- **Release** com binários standalone via PyInstaller (Windows, Linux, macOS)
- **Documentação**: README, CONTRIBUTING, SECURITY, AGENTS.md, docs/PLATFORMS.md
- Templates de issue (bug report e feature request) e `config.yml`

### Corrigido

- `NameError: name 'Path' is not defined` — o subprocesso não importava
  `pathlib`; o subprocesso foi eliminado
- `UnicodeEncodeError` em console `cp1252` — removidos emojis de `print`
- Botão "Limpar" nunca aparecia — faltava `.pack()`
- Widgets do Tkinter sendo tocados fora da thread principal — padrão `_ui_call`
  com `root.after(0, ...)`, `threading.Lock` e flag `_closed`
- Crash ao fechar a janela durante uma conversão
- `pick_font_family()` levantava `RuntimeError` sem raiz Tk
- Layout colapsado — `grid` e `pack` misturados; uniformizado em `pack`
- `pady` com tupla em `Frame` — `TclError: bad screen distance`
- `zip` inexistente no Git Bash do Windows — `scripts/package.py` com
  `shutil.make_archive`
- Continuação de linha `\` quebrando no PowerShell do Windows

### Conhecido

- Os binários standalone têm 105–131 MB porque o `magika` carrega um modelo ONNX
- Sem preview do Markdown antes de salvar (backlog 5.6)
- Sem conversão em lote (backlog 5.2)
- Sem arrastar e soltar (backlog 5.1)

[Não publicado]: https://github.com/jalawz/markitdown-gui/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/jalawz/markitdown-gui/releases/tag/v1.1.0
