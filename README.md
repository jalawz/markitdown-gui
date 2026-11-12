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
- **Conversão em lote** — modo `--no-gui` para scripts e automação.
- **Transparente** — código aberto, sem telemetria, sem serviços externos.

> [!NOTE]
> O MarkItDown converte **para Markdown**, formato pensado para Consumption por LLMs. A saída é limpa e estruturada, mas não é um conversor de alta fidelidade para leitura humana.

---

## Captura de tela

```
+--------------------------------------------------------------+
|  MarkItDown GUI v1.1.0                                       |
+--------------------------------------------------------------+
|  MarkItDown Converter                                        |
|  Converta documentos em Markdown pronto para LLMs             |
+--------------------------------------------------------------+
|  Arquivo de origem: [C:\Users\...\Go Programming.pdf][Procurar]|
|  Salvar em:         [C:\Users\...\go-programming.md][Procurar]|
|                                                              |
|  + Options ------------------------------------------------+  |
|  | [ ] Usar plugins de terceiros (--use-plugins)          |  |
|  | [ ] Manter data URIs (imagens base64) no resultado     |  |
|  +--------------------------------------------------------+  |
|                                                              |
|  + Progress ------------------------------------------------+  |
|  | [############################################        ] |  |
|  | Concluído: go-programming.md (1.062.373 caracteres)   |  |
|  +--------------------------------------------------------+  |
|                                                              |
|  + Registro ------------------------------------------------+  |
|  | Importando markitdown...                              |  |
|  | Convertendo ... (12.010.307 bytes)                    |  |
|  | OK: 1.062.373 caracteres, 20.992 linhas, 1.063,9 KB    |  |
|  +--------------------------------------------------------+  |
|                                                              |
|  [ Converter ]  [ Limpar ]  [ Abrir pasta do resultado ]     |
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
2. **Clique em "Procurar..."** em *Arquivo de origem* e escolha o documento
   — o destino `.md` é sugerido automaticamente
3. **Ajuste o destino** se necessário
4. **Clique em "Converter"**
5. Acompanhe o progresso e o registro em tempo real
6. Use **"Abrir pasta do resultado"** para ver o arquivo

### Opções

| Opção | Equivalente CLI | Efeito |
|---|---|---|
| Usar plugins de terceiros | `--use-plugins` | Habilita conversores instalados via `entry_points` |
| Manter data URIs | `--keep-data-uris` | Preserva imagens base64 no Markdown em vez de truncar |

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
| `Ctrl+Enter` | Converter |
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
├── AGENTS.md                # Diretrizes para agentes de IA eQUIRED
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
