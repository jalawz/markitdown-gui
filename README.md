# MarkItDown GUI

> Uma interface gráfica multiplataforma para converter documentos em Markdown usando o [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

[![Licença MIT](https://img.shields.io/badge/licença-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![CI](https://github.com/jalawz/markitdown-gui/actions/workflows/ci.yml/badge.svg)](https://github.com/jalawz/markitdown-gui/actions/workflows/ci.yml)
[![Plataformas](https://img.shields.io/badge/plataformas-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](docs/PLATFORMS.md)
![Status](https://img.shields.io/badge/status-estável-brightgreen.svg)

---

## Sumário

- [Por que_markitdown_gui?](#por-que-markitdown-gui)
- [Captura de tela](#captura-de-tela)
- [Instalação](#instalação)
- [Uso](#uso)
- [Recursos](#recursos)
- [Formatos suportados](#formatos-suportados)
- [Linha de comando](#linha-de-comando)
- [Atalhos de teclado](#atalhos-de-teclado)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Changelog](#changelog)
- [Desenvolvimento](#desenvolvimento)
- [Solução de problemas](#solução-de-problemas)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## Por que markitdown_gui?

O [MarkItDown](https://github.com/microsoft/markitdown) é uma biblioteca excelente, mas o uso no dia a dia exige digitar comandos. Esta GUI resolve isso:

- **Zero configuração** — abra, escolha o arquivo, converta.
- **Multiplataforma** — o mesmo código roda em Windows, macOS e Linux.
- **Sem dependências pesadas** — apenas `tkinter` (já vem com o Python) e o MarkItDown.
- **Conversão em lote** — monte uma fila na janela, acompanhe o progresso
  e cancele entre arquivos; modo `--no-gui` para scripts e automação.
- **Transparente** — código aberto, sem telemetria, sem serviços externos.

> [!NOTE]
> O MarkItDown converte **para Markdown**, formato pensado para Consumption por LLMs. A saída é limpa e estruturada, mas não é um conversor de alta fidelidade para leitura humana.

---

## Captura de tela

```
+--------------------------------------------------------------+
|  MarkItDown GUI v1.6.0                                       |
+--------------------------------------------------------------+
|  MarkItDown Converter                                        |
|  Converta documentos em Markdown pronto para LLMs            |
+--------------------------------------------------------------+
|  Arquivo de origem: [C:\Users\...\Go Programming.pdf][Procurar]|
|  Salvar em:         [C:\Users\...\go-programming.md][Procurar]|
|                                                              |
|  Fila de conversao:                                          |
|  +--------------------------------------------------------+  |
|  | livro.pdf -> livro.md                                  |  |
|  | artigo.docx -> artigo.md                               |  |
|  +--------------------------------------------------------+  |
|  [Adicionar a fila] [Remover selecionados] [Limpar fila]      |
|                                                              |
|  + Opcoes ------------------------------------------------+  |
|  | [ ] Usar plugins de terceiros (--use-plugins)          |  |
|  | [ ] Manter data URIs (imagens base64) no resultado     |  |
|  | [x] Estruturar PDF por capitulos (usa o sumario)       |  |
|  | [ ] Salvar um arquivo por capitulo (pasta destino)     |  |
|  +--------------------------------------------------------+  |
|                                                              |
|  + Progresso ---------------------------------------------+  |
|  | [#################################        ]      66%   |  |
|  | Convertendo 2/3: artigo.docx                           |  |
|  +--------------------------------------------------------+  |
|                                                              |
|  + Registro ----------------------------------------------+  |
|  | Fila iniciada com 3 arquivo(s).                        |  |
|  | OK: 1.062.373 caracteres, 20.992 linhas, 1.063,9 KB    |  |
|  +--------------------------------------------------------+  |
|                                                              |
|  [Converter fila] [Cancelar] [Limpar] [Abrir pasta]          |
+--------------------------------------------------------------+
```

---

## Instalação

### Pré-requisitos

| Item | Versão |
|---|---|
| Python | 3.10 ou superior |
| [markitdown](https://pypi.org/project/markitdown/) | `0.1.9` ou superior |
| tkinter | Já vem com o Python no Windows e macOS |

<details>
<summary><b>Instalando o tkinter no Linux</b></summary>

```bash
# Ubuntu / Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

</details>

### Windows

```cmd
git clone https://github.com/jalawz/markitdown-gui.git
cd markitdown-gui
pip install -r requirements.txt
python markitdown_gui.py
```

### macOS

```bash
git clone https://github.com/jalawz/markitdown-gui.git
cd markitdown-gui
pip3 install -r requirements.txt
python3 markitdown_gui.py
```

### Linux

```bash
git clone https://github.com/jalawz/markitdown-gui.git
cd markitdown-gui
sudo apt-get install python3-tk      # se necessário
pip3 install -r requirements.txt
python3 markitdown_gui.py
```

### Atalho de execução

| SO | Comando |
|---|---|
| Windows | `run.bat` — não abre janela de console (usa `pythonw`) |
| macOS / Linux | `./run.sh` — valida o tkinter antes de executar |

---

## Uso

### Passo a passo

1. **Abra** a aplicação (`python markitdown_gui.py`)
2. **Clique em "Procurar"** em *Arquivo de origem* e escolha o documento
   — o destino `.md` é sugerido automaticamente
3. **Ajuste o destino** se necessário
4. **Clique em "Adicionar a fila"** — repita os passos 2–4 para converter
   vários documentos de uma vez
5. **Clique em "Converter fila"** (ou `Ctrl+Enter`)
6. Acompanhe o progresso e o registro em tempo real; **"Cancelar"**
   interrompe a fila entre um arquivo e outro
7. Use **"Abrir pasta do resultado"** para ver o último arquivo gerado

Dica: arraste arquivos para a janela (requer `pip install tkinterdnd2`) —
eles entram na fila automaticamente.

> O destino nunca pode ser o próprio arquivo de origem. Se você abrir um
> `.md` sem informar destino, a GUI sugere `<nome>.converted.md`.

### Opções

| Opção | Equivalente CLI | Efeito |
|---|---|---|
| Usar plugins de terceiros | `--use-plugins` | Habilita conversores instalados via `entry_points` |
| Manter data URIs | `--keep-data-uris` | Preserva imagens base64 no Markdown em vez de truncar |
| Estruturar PDF por capítulos | `--no-outline` (desliga) | Usa o sumário do PDF para emitir `# Capítulo` antes de cada capítulo e escapa os `#` do texto corrido |
| Salvar um arquivo por capítulo | `--split` | Escreve cada capítulo em `<destino>-capitulos/cap-NN-titulo.md` e gera um índice com links |

### Estrutura de capítulos em PDF

O MarkItDown entrega o texto do PDF como um fluxo contínuo — a troca de capítulo
fica no meio de um parágrafo, sem heading algum. Isso quebra qualquer fatiamento
por `#` (RAG, resumo por LLM, navegação).

Com a opção ligada (padrão), a GUI lê o **outline do PDF** e insere
`# <título do capítulo>` no ponto exato onde cada capítulo começa. O título vem
do sumário; quando o sumário só diz `Chapter 12`, a GUI pega o título real da
primeira página do capítulo.

Como o texto de PDF é corrido, qualquer `#` que já exista nele é comentário de
código/YAML/shell — esses são **escapados** (`\#`) para não virarem heading.
Nada é adicionado nem removido do texto: só estrutura.

PDF sem sumário (ou `pdfminer` ausente) → o arquivo sai como antes, e o registro
avisa.

### Um arquivo por capítulo

Com o sumário aplicado, marque **"Salvar um arquivo por capítulo"** (ou use
`--split` no batch) para não gerar um único `.md` gigante. A saída vira:

```
livro.md                          # índice com links
livro-capitulos/
├── cap-01-capa.md
├── cap-04-introducao-aos-microsservicos.md
├── cap-05-introducao-ao-spring-boot.md
...
└── cap-28-indice.md
```

Os nomes são transliterados (acentos viram ASCII) e truncados em 60 caracteres.
É o formato mais prático para RAG, leitura parcial ou alimentar um LLM por
capítulo.

No livro de referência (1009 páginas): 28 arquivos, `cap-04` → página 1 do
capítulo, até `cap-26` → capítulo 23.

---

## Formatos suportados

O MarkItDown detecta o tipo automaticamente. A GUI cobre 24 formatos no seletor:

| Categoria | Formatos | Dependência extra |
|---|---|---|
| Documentos | `.pdf` | `pdfplumber`, `pdfminer.six` |
| Word | `.docx`, `.doc` | `mammoth` |
| PowerPoint | `.pptx`, `.ppt` | `python-pptx` |
| Excel | `.xlsx`, `.xls` | `pandas`, `openpyxl` |
| Web | `.html`, `.htm` | `beautifulsoup4`, `markdownify` |
| Dados | `.csv`, `.json`, `.xml` | — |
| Texto | `.txt`, `.md` | — |
| Livros | `.epub` | — |
| Notebook | `.ipynb` | — |
| Outlook | `.msg` | `olefile` |
| Imagens | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp` | — |
| Áudio | `.wav`, `.mp3` | `pydub`, `SpeechRecognition` |

Instalar tudo de uma vez:

```bash
pip install "markitdown[all]"
```

Ou por categoria:

```bash
pip install "markitdown[pdf,docx,pptx]"
```

---

## Linha de comando

Além da interface gráfica, o script aceita argumentos — útil para automação.

```bash
# Abre a GUI já com o arquivo selecionado
python markitdown_gui.py livro.pdf

# Abre com origem e destino definidos
python markitdown_gui.py livro.pdf saida.md

# Converte e fecha automaticamente
python markitdown_gui.py livro.pdf saida.md --auto

# Modo batch: sem interface gráfica (ideal para scripts e cron)
python markitdown_gui.py livro.pdf saida.md --no-gui

# Mesmo no batch, o sumário do PDF é aplicado; use --no-outline para desligar
python markitdown_gui.py livro.pdf saida.md --no-gui --no-outline

# Um arquivo por capítulo (cria saida-capitulos/ + indice em saida.md)
python markitdown_gui.py livro.pdf saida.md --no-gui --split
```

Exemplo em script:

```bash
#!/usr/bin/env bash
for pdf in documentos/*.pdf; do
    python markitdown_gui.py "$pdf" "markdown/$(basename "${pdf%.pdf}").md" --no-gui
done
```

---

## Atalhos de teclado

| Atalho | Ação |
|---|---|
| `Ctrl+O` | Selecionar arquivo de origem |
| `Ctrl+S` | Selecionar destino |
| `Ctrl+Enter` | Converter a fila |
| `Esc` | Limpar campos |

---

## Estrutura do projeto

```
markitdown-gui/
├── markitdown_gui.py        # Aplicação principal (classe MarkItDownGUI)
├── requirements.txt         # Dependências de execução
├── requirements-dev.txt     # Dependências de desenvolvimento
├── pyproject.toml           # Metadados e configuração de ferramentas
├── run.bat                  # Atalho Windows (sem console)
├── run.sh                   # Atalho macOS/Linux
├── AGENTS.md                # Diretrizes para agentes de IA + backlog
├── CHANGELOG.md             # Histórico de mudanças por versão
├── CONTRIBUTING.md          # Guia de contribuição
├── LICENSE                  # MIT
├── docs/
│   └── PLATFORMS.md         # Notas específicas por sistema operacional
├── tests/
│   └── test_gui.py          # Testes automatizados
└── .github/
    └── workflows/
        ├── ci.yml           # CI: lint + testes (matrix OS × Python)
        └── release.yml      # Empacotamento com PyInstaller
```

---

## Changelog

O histórico completo de mudanças está em [`CHANGELOG.md`](CHANGELOG.md).

O plano de trabalho futuro — com prioridades, soluções, riscos e critérios de
aceite — está em [`AGENTS.md`](AGENTS.md), seção 5.

---

## Desenvolvimento

```bash
pip install -r requirements-dev.txt

# Testes
pytest tests/ -v

# Lint e formatação
ruff check .
ruff format .

# Verificação de tipos
mypy markitdown_gui.py

# Todos de uma vez
pre-commit run --all-files
```

O CI roda em uma matriz de **3 sistemas operacionais × 4 versões do Python**
(Windows, macOS e Linux × 3.10, 3.11, 3.12, 3.13).

Consulte o [`AGENTS.md`](AGENTS.md) para as diretrizes de arquitetura e a lista de melhorias planejadas.

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: markitdown` | Pacote não instalado | `pip install "markitdown[all]"` |
| `ModuleNotFoundError: tkinter` | tkinter ausente (Linux) | `sudo apt-get install python3-tk` |
| `MissingDependencyException` no PDF | Dependências de PDF ausentes | `pip install "markitdown[pdf]"` |
| Interface abre em branco | tkinter desatualizado | `sudo apt install --reinstall python3-tk` |
| Texto sem acento na interface | Codificação do console | Defina `PYTHONIOENCODING=utf-8` |
| Conversão muito lenta | PDF grande com OCR | Normalmente leva ~35s para 2.100 páginas |
| "Abrir pasta" não funciona | Gerenciador ausente | Instale `xdg-utils` no Linux |

---

## Contribuindo

Contribuições são bem-vindas! Veja [`CONTRIBUTING.md`](CONTRIBUTING.md).

Áreas onde mais ajuda é necessária:

- 🌍 **Portabilidade** — testar em Linux/macOS e relatar diferenças
- 🧪 **Testes** — cobertura de `tests/` ainda baixa
- 🌐 **i18n** — strings hoje estão fixas em português
- 📦 **Empacotamento** — binários standalone via PyInstaller

---

## Licença

Distribuído sob a licença [MIT](LICENSE).

Este projeto não é afiliado, endossado ou oficialmente conectado ao Microsoft.
MarkItDown é um projeto da Microsoft sob a licença MIT.

---

<div align="center">
  <sub>Feito com ☕ e Python por <a href="https://github.com/jalawz">jalawz</a></sub>
</div>
