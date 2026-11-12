#!/usr/bin/env bash
# Atalho para macOS e Linux.
# Uso: ./run.sh  [arquivo] [destino]
# Crie um link simbolico em ~/bin ou ~/Desktop para usar em qualquer lugar.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PYTHON_BIN=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c "import tkinter" >/dev/null 2>&1; then
            PYTHON_BIN="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "ERRO: Python com tkinter nao encontrado."
    if [ "$(uname)" = "Linux" ]; then
        echo "  Instale com: sudo apt-get install python3-tk"
    else
        echo "  Instale com: brew install python-tk"
    fi
    exit 1
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/markitdown_gui.py" "$@"
