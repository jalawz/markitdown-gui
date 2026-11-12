## Primeira release estavel

Interface grafica de arquivo unico para converter documentos em Markdown usando o [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

### Recursos

- **24 formatos** suportados no seletor (PDF, Word, PPT, Excel, HTML, CSV, JSON, XML, EPUB, Jupyter, Outlook, imagens, audio e mais)
- **Painel de log** com cores por nivel e status em tempo real
- **Modo batch** (`--no-gui`) para automacao e scripts
- **Modo auto** (`--auto`) que converte ao abrir
- Opcoes de **plugins de terceiros** e **manutencao de data URIs**
- Botao **Abrir pasta do resultado**
- Atalhos de teclado: `Ctrl+O`, `Ctrl+S`, `Ctrl+Enter`, `Esc`

### Portabilidade

| SO | Recursos |
|---|---|
| Windows | DPI awareness, barra de titulo escura, `explorer` |
| macOS | `open -R`, instrucoes para `brew install python-tk` |
| Linux | `xdg-open`, instrucoes para `python3-tk` |

### Qualidade

- 40 testes automatizados
- `ruff` + `mypy` + `pytest` no CI (matriz 3 SOs x 4 versoes do Python)
- Verificacao via AST de que widgets do Tkinter nunca sao tocados fora da thread principal

### Documentacao

- `README.md` — instalacao, uso, troubleshooting
- `AGENTS.md` — arquitetura, guardrails e backlog priorizado (P0/P1/P2)
- `docs/PLATFORMS.md` — notas especificas por sistema operacional
- `CONTRIBUTING.md` — guia de contribuicao

---

### Instalacao

```bash
pip install -r requirements.txt
python markitdown_gui.py
```

Ou use o modo batch:

```bash
python markitdown_gui.py livro.pdf saida.md --no-gui
```

---

Feito com Python e tkinter. Licenca MIT.
