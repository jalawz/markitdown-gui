# Contribuindo

Obrigado por querer contribuir! 🎉

Este projeto é pequeno e direto — a barreira de entrada é baixa.

---

## Antes de começar

1. Abra uma **issue** descrevendo o que quer fazer (evita trabalho duplicado)
2. Para mudanças grandes, comente na issue antes de escrever o código
3. Seções marcadas com 🌍, 🧪, 🌐, 📦 no `README.md` são as que mais precisam de ajuda

---

## Ambiente de desenvolvimento

```bash
git clone https://github.com/jalawz/markitdown-gui.git
cd markitdown-gui
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
pre-commit install
```

---

## Fluxo de trabalho

```bash
git checkout -b feature/minha-mudanca
# ... codigo ...
pytest tests/ -v
ruff check . && ruff format .
pre-commit run --all-files
git commit -am "feat: descricao curta da mudanca"
git push origin feature/minha-mudanca
```

Abra um **Pull Request** para `main`.

---

## Regras de código

### Portabilidade é obrigatória

O projeto roda em Windows, macOS e Linux. Testes que só funcionam em um SO
serão rejeitados.

```python
# CERTO
if sys.platform == "win32":
    ...

# ERRADO
if os.name == "nt":   # funciona, mas use sys.platform por consistencia
```

- **Nunca** use `grid()` e `pack()` no mesmo widget pai
- **Sempre** passe `encoding="utf-8"` em `open()` / `write_text()` / `read_text()`
- **Nunca** use `print()` com emoji ou acentos em código que possa rodar em
  console `cp1252` (Windows)
- **Nunca** fixe caminhos absolutos de nenhum SO

### Thread-safety do Tkinter

Tkinter **não** é thread-safe. Qualquer código que rode fora da thread
principal deve passar por `_ui_call`:

```python
# CERTO
self._ui_call(lambda: self.status_var.set("pronto"))

# ERRADO
self.status_var.set("pronto")
```

O CI verifica isso automaticamente via análise de AST.

---

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Tipo | Uso |
|---|---|
| `feat:` | nova funcionalidade |
| `fix:` | correção de bug |
| `docs:` | documentação |
| `test:` | testes |
| `refactor:` | refatoração sem mudança de comportamento |
| `chore:` | manutenção (deps, config) |
| `perf:` | performance |

```
feat: adiciona conversao em lote
fix: corrige crash ao fechar janela durante conversao
docs: traduz README para ingles
```

---

## Pull Request

- **Título** no formato Conventional Commits
- **Descrição** explicando o *porquê*, não o *o quê*
- Referencie a issue relacionada (`Closes #12`)
- Screenshots para mudanças visuais
- Checklist:
  - [ ] `pytest tests/ -v` passa
  - [ ] `ruff check .` limpo
  - [ ] `mypy markitdown_gui.py` sem erros
  - [ ] Testado em pelo menos 2 SOs (se aplicável)
  - [ ] `README.md` atualizado se o comportamento mudou

---

## Checklist de revisão

| Item | Critério |
|---|---|
| Funciona em Windows, macOS e Linux | CI verde na matriz |
| Sem `UnicodeEncodeError` em `cp1252` | Nenhum emoji em `print` |
| Threads não tocam widgets diretamente | AST check no CI |
| Layout não quebra | `pack()` consistente |
| Testes cobrem a mudança | ≥ 70% de cobertura |
| Documentação atualizada | README + AGENTS.md |

---

## Código de conduta

Seja respeitoso e acolhedor. Contribuições de todos os níveis são bem-vindas —
inclusive correções de digitação.
