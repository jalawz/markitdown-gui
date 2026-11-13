# Notas por Sistema Operacional

A aplicação é portável — o mesmo `markitdown_gui.py` roda nos três SOs.
Este documento registra as diferenças conhecidas.

---

## Windows

### Executar sem janela de console

O `run.bat` usa `pythonw` (interpretador sem console):

```cmd
run.bat
```

Se o `pythonw` não existir no PATH, ele cai para `python` automaticamente.

### DPI awareness

Chamado em `main()` antes de criar a raiz do Tk, para evitar texto
serrilhado em telas 4K / 150% de escala:

```python
ctypes.windll.shcore.SetProcessDpiAwareness(1)
```

### Barra de título escura

Aplicada via `DwmSetWindowAttribute` (DWM attribute 20). Disponível no
Windows 10 2004+ e 11. Em versões antigas a chamada falha silenciosamente —
sem impacto.

### Gerenciador de arquivos

```python
subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
```

O `/select,` destaca o arquivo convertido dentro da pasta.

### Codificação do console

O console do Windows usa `cp1252` por padrão. Se aparecer `UnicodeEncodeError`:

```cmd
set PYTHONIOENCODING=utf-8
python markitdown_gui.py
```

---

## macOS

### Tkinter

O Python do site oficial (`python.org`) já inclui o tkinter. Homebrew também.

Se `ModuleNotFoundError: No module named 'tkinter'`:

```bash
brew install python-tk
```

### Barra de título escura

Não aplicada — o Tk do macOS não expõe o atributo DWM. A interface usa o
título nativo do sistema.

### Gerenciador de arquivos

```python
subprocess.Popen(["open", "-R", str(path)])  # -R revela no Finder
```

### Gatekeeper

Se um binário empacotado for bloqueado:

```bash
xattr -d com.apple.quarantine markitdown-gui
```

---

## Linux

### Tkinter

Não vem instalado por padrão na maioria das distros:

```bash
# Ubuntu / Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk

# openSUSE
sudo zypper install python3-tk
```

### Gerenciador de arquivos

Requer `xdg-utils`:

```bash
sudo apt-get install xdg-utils
```

```python
subprocess.Popen(["xdg-open", str(folder)])
```

### Distros sem GNOME/KDE

Sem gerenciador de arquivos padrão, o botão "Abrir pasta do resultado"
falha silenciosamente. Use `xdg-open` com um terminal ou instale
`xdg-utils`.

### Tkinter desatualizado

Interfaces quebradas (widgets desalinhados, cores erradas) costumam
indicar um Tk antigo:

```bash
sudo apt install --reinstall python3-tk
```

### Wayland

Funciona, mas alguns gerenciadores de arquivos ignora `xdg-open` com
argumentos extras. O workaround é abrir o diretório pai em vez do arquivo.

---

## Tabela comparativa

| Recurso | Windows | macOS | Linux |
|---|:---:|:---:|:---:|
| DPI awareness | ✅ | n/a | n/a |
| Barra de título escura | ✅ | ❌ | ❌ |
| Gerenciador de arquivos | `explorer` | `open -R` | `xdg-open` |
| tkinter pré-instalado | ✅ | ✅ | ❌ |
| Executável sem console | `pythonw` | `pythonw` | `python3` |

---

## Testes em CI headless

O GitHub Actions roda em Linux sem display. Os testes que precisam de uma
janela usam o fixture `gui_root`, que faz `pytest.skip()` se não houver
display:

```python
try:
    root = tk.Tk()
except tk.TclError as exc:
    pytest.skip(f"sem display disponivel: {exc}")
```

Para rodar a suíte completa localmente com display virtual no Linux:

```bash
sudo apt-get install xvfb
xvfb-run -a pytest tests/ -v
```

### ⚠️ `update()` trava no macOS

Este é o gotcha mais importante para quem escreve testes nesta aplicação.

| Método | Comportamento | macOS |
|---|---|---|
| `root.update()` | Processa **todos** os eventos, incluindo Apple Events | ❌ **trava** |
| `root.update_idletasks()` | Processa apenas tarefas ociosas | ⚠️ **não executa `after(0, ...)`** |
| `mainloop()` + polling | Event loop real, com `quit()` no fim | ✅ correto |

O `update` completo do Tcl no macOS bloqueia esperando eventos do sistema.
Por isso **não use `update()`**.

Mas `update_idletasks()` também não serve: ela não executa timers
`after(0, ...)` — que é exatamente o mecanismo usado pelo padrão `_ui_call`
da aplicação.

**A solução é o helper `run_until()`**, que roda o event loop de verdade:

```python
def run_until(root, predicate, timeout=60.0):
    """Roda o event loop do Tk ate predicate() virar verdadeiro."""
    state = {"ok": False, "elapsed": 0.0}

    def poll():
        if predicate():
            state["ok"] = True
            root.quit()
            return
        state["elapsed"] += 0.05
        if state["elapsed"] > timeout:
            root.quit()
            return
        root.after(50, poll)

    root.after(50, poll)
    root.mainloop()
    return state["ok"]
```

Uso típico:

```python
# ERRADO — trava no macOS
gui_root.update()

# ERRADO — nao dispara o after(0) do _ui_call
gui_root.update_idletasks()

# CERTO
assert run_until(gui_root, lambda: not app._busy)
```

Além disso, `destroy()` sem `mainloop()` pode bloquear no macOS. O fixture
chama `quit()` antes de `destroy()`.

---

## Cobertura por SO

A matriz do CI roda **3 SOs × 4 versões do Python**:

| SO | Py 3.10 | Py 3.11 | Py 3.12 | Py 3.13 |
|---|:---:|:---:|:---:|:---:|
| Windows | ✅ | — | ✅ | ✅ |
| Linux | ✅ | ✅ | ✅ | — |
| macOS | ✅ | — | ✅ | — |

Testes que dependem de display são pulados automaticamente onde não há
window server (Linux headless).
