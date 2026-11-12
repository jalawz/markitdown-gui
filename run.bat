@echo off
REM Atalho para Windows.
REM Uso: run.bat  [arquivo] [destino]

setlocal
set "SCRIPT_DIR=%~dp0"

REM Usa "pythonw" para nao abrir uma janela de console.
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%SCRIPT_DIR%markitdown_gui.py" %*
) else (
    python "%SCRIPT_DIR%markitdown_gui.py" %*
)

endlocal
