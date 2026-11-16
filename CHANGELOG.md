# Changelog

Todas as mudanças relevantes deste projeto.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento seguindo [SemVer](https://semver.org/lang/pt-BR/).

---

## [1.5.0] — 2026-11-16

Consolida o fix de fila (publicado sem querer como `v1.1.1`) e a estrutura de
capítulos em PDF. As versões 1.2.0–1.4.0 foram tagueadas antes de o
`APP_VERSION` acompanhar; elas aparecem abaixo reconstruídas a partir dos
commits.

### Adicionado

- **Estrutura de capítulos para PDF.** O MarkItDown entrega o texto de PDF como
  fluxo contínuo, sem headings: a troca de capítulo fica no meio de um
  parágrafo e os únicos `#` do arquivo são comentários de código. A GUI agora lê
  o outline do PDF (via `pdfminer`) e insere `# <título>` no início de cada
  capítulo; quando o outline só traz `Chapter 12`, usa o título real da primeira
  página. Os `#` do texto corrido são escapados para não virar heading.
  Validado em um livro de 1009 páginas / 23 capítulos: 28 seções marcadas, todas
  na página certa, e 53 `#` de código escapados.
- Toggle na UI ("Estruturar PDF por capítulos", ligado por padrão) e flag
  `--no-outline` para o modo `--no-gui`.

### Adicionado (continuação)

- **Salvar um arquivo por capítulo.** Com o sumário do PDF aplicado, a GUI
  pode escrever cada capítulo em seu próprio arquivo dentro de uma pasta
  `<destino>-capitulos/`, com nomes normalizados (`cap-08-adicionando-uma-
  descricao-de-api-usando-openapi.md`) e um `<destino>.md` servindo de índice
  com links relativos. Toggle na UI ("Salvar um arquivo por capítulo") e flag
  `--split` no modo `--no-gui`.
- `split_pdf_chapters()` e `_slug()` (com `unicodedata` para transliterar
  acentos em nomes de arquivo).

### Corrigido (continuação)

- **Testes de fechar a janela durante a conversão** (pendência do item 5.12):
  `test_fechar_janela_durante_a_conversao_nao_deixa_thread_ativa` e
  `test_worker_termina_quando_janela_fecha` cobrem o caminho em que a janela
  morre antes do worker terminar. Nenhuma thread órfã, e o arquivo continua
  sendo salvo.
- Novas funções: `pdf_outline_anchors`, `inject_outline_headings`,
  `escape_leading_hashes`, `apply_pdf_structure`, `_titulo_do_sumario`,
  `_normalizar_com_mapa`. Nenhuma dependência nova (`pdfminer.six` já vem com
  `markitdown[all]`).

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
- **41 → 63 testes**; as classes `TestQueue`, `TestOutline` e `TestSplitChapters`
  cobrem avanço da fila, erro parcial, cancelamento, a regressão do `Ctrl+Enter`,
  a injeção de headings do sumário e o corte por capítulo.

---

## [1.4.0] — 2026-11-14

*Registro reconstruído: tagueado sem entrada no changelog.*

### Adicionado

- **Arrastar e soltar** (5.1): `tkinterdnd2` opcional, com degradação
  silenciosa quando ausente; arquivos soltos entram na fila.
- `FILE_FILTERS` com os 24 formatos suportados.

### Corrigido

- Layout com um único container `pack()` no root, evitando o colapso de
  `grid` em algumas builds do Tk.

---

## [1.3.0] — 2026-11-14

*Registro reconstruído: tagueado sem entrada no changelog.*

### Adicionado

- **Conversão em lote (5.2)**, **cancelamento (5.3)** e **progresso
  determinístico (5.4)** na fila de conversão.
- `_queue`, `_cancel_requested` e barra de progresso por arquivo.

---

## [1.2.0] — 2026-11-13

*Registro reconstruído: tagueado sem entrada no changelog.*

### Adicionado

- **Lembrar diretórios (5.7)**: `config.json` em `%APPDATA%` (Windows),
  `~/Library/Application Support` (macOS) e `$XDG_CONFIG_HOME` (Linux);
  origem e destino anteriores são restaurados ao abrir.

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
