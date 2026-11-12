#!/usr/bin/env python3
"""
MarkItDown GUI - Conversor grafico de documentos para Markdown

Interface grafica multiplataforma (Windows / macOS / Linux) para converter
PDF, DOCX, PPTX, XLSX, HTML, CSV e mais em Markdown usando o Microsoft MarkItDown.

Uso:
    python markitdown_gui.py
    python markitdown_gui.py arquivo.pdf            # ja abre com o arquivo
    python markitdown_gui.py arquivo.pdf saida.md   # ja abre com origem e destino

Requisitos:
    Python 3.10+
    pip install "markitdown[all]"
    (Linux: sudo apt-get install python3-tk)

Este software e distribuido sob a licenca MIT.
"""

import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

APP_NAME = "MarkItDown GUI"
APP_VERSION = "1.1.0"

# Tipos de arquivo suportados pelo MarkItDown
FILE_FILTERS = [
    (
        "Todos os documentos suportados",
        "*.pdf *.docx *.doc *.pptx *.ppt *.xlsx *.xls *.html *.htm *.csv "
        "*.json *.xml *.txt *.md *.epub *.ipynb *.msg *.wav *.mp3 *.jpg *.jpeg *.png",
    ),
    ("PDF", "*.pdf"),
    ("Word", "*.docx *.doc"),
    ("PowerPoint", "*.pptx *.ppt"),
    ("Excel", "*.xlsx *.xls"),
    ("HTML", "*.html *.htm"),
    ("Dados", "*.csv *.json *.xml"),
    ("Texto", "*.txt *.md"),
    ("EPUB / Jupyter", "*.epub *.ipynb"),
    ("Outlook", "*.msg"),
    ("Imagens", "*.jpg *.jpeg *.png *.gif *.bmp"),
    ("Audio", "*.wav *.mp3"),
    ("Todos os arquivos", "*.*"),
]

# Ordem de preferencia de fontes por plataforma.
# As chaves sao os valores retornados por sys.platform.
FONT_CANDIDATES = {
    "win32": ["Segoe UI", "Tahoma", "Verdana", "Arial"],
    "darwin": ["SF Pro Text", "Helvetica Neue", "Helvetica", "Arial"],
    "linux": ["Ubuntu", "DejaVu Sans", "Noto Sans", "Liberation Sans", "Arial"],
    "freebsd": ["DejaVu Sans", "Noto Sans", "Arial"],
}

_FONT_CACHE: list[str] = []


def pick_font_family():
    """Retorna a primeira fonte disponivel para a plataforma atual."""
    if _FONT_CACHE:
        return _FONT_CACHE[0]

    candidates = FONT_CANDIDATES.get(sys.platform, ["Arial", "Sans Serif"])

    # tkfont.families() e tkfont.names() exigem uma raiz Tk existente.
    # Sem ela (ex.: chamada antes de criar a janela) caimos no fallback.
    available = set()
    try:
        available = set(tkfont.families())
    except Exception:
        try:
            available = set(tkfont.names())
        except Exception:
            available = set()

    chosen = "TkDefaultFont"
    for name in candidates:
        if name in available:
            chosen = name
            break
    else:
        # Nenhuma fonte candidato existe: usa a padrao do Tk.
        chosen = "TkDefaultFont"

    _FONT_CACHE.append(chosen)
    return chosen


def enable_windows_dpi_awareness():
    """Evita que o Tkinter fique com conteudo serrilhado em telas de alta resolucao."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def enable_windows_dark_titlebar(widget, dark=True):
    """Aplica barra de titulo escura no Windows 10/11 (silenciosamente ignora erros)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        hwnd = ctypes.windll.user32.GetParent(widget.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
        )
    except Exception:
        pass


def open_in_file_manager(path):
    """Abre um arquivo/pasta no gerenciador padrão do sistema operacional."""
    try:
        if sys.platform == "win32":
            if Path(path).is_dir():
                os.startfile(path)  # noqa: S606
            else:
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        elif sys.platform == "darwin":
            args = ["open"] if Path(path).is_dir() else ["open", "-R"]
            subprocess.Popen([*args, str(path)])
        else:
            folder = path if Path(path).is_dir() else str(Path(path).parent)
            subprocess.Popen(["xdg-open", str(folder)])
    except Exception:
        pass


def pip_install_hint():
    """Comando de instalacao adaptado ao SO e ao gerenciador de pacotes."""
    if sys.platform == "win32":
        return 'pip install "markitdown[all]"'
    if sys.platform == "darwin":
        return "pip3 install 'markitdown[all]'"
    if shutil.which("pipx"):
        return "pipx install 'markitdown[all]'"
    return "pip3 install 'markitdown[all]'"


# --------------------------------------------------------------------------- #
# Aplicacao
# --------------------------------------------------------------------------- #
class MarkItDownGUI:
    def __init__(self, root, cli_args=None, auto_start=False):
        self.root = root
        self.family = pick_font_family()
        self._busy = False
        self._last_output = None
        self._closed = False
        self._state_lock = threading.Lock()

        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("700x620")
        self.root.minsize(700, 560)
        self.root.configure(bg="#f4f6f7")

        enable_windows_dpi_awareness()
        enable_windows_dark_titlebar(self.root, dark=False)

        self._build_ui()
        self._bind_keys()
        self._apply_cli_args(cli_args)

        if auto_start and cli_args:
            self.root.after(400, self.convert_file)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # Um unico container com pack() garante geometria previsivel em todos os SOs.
        container = tk.Frame(self.root, bg="#f4f6f7")
        container.pack(fill="both", expand=True)

        # Cabecalho
        header = tk.Frame(container, bg="#2c3e50")
        header.pack(fill="x")
        tk.Label(
            header,
            text="MarkItDown Converter",
            bg="#2c3e50",
            fg="white",
            font=(self.family, 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(14, 0))
        tk.Label(
            header,
            text="Converta documentos em Markdown pronto para LLMs",
            bg="#2c3e50",
            fg="#bdc3c7",
            font=(self.family, 9),
        ).pack(anchor="w", padx=20, pady=(0, 14))

        # Corpo: origem, destino e opcoes
        body = tk.Frame(container, bg="#f4f6f7", padx=22, pady=18)
        body.pack(fill="x")
        body.columnconfigure(1, weight=1)

        # --- Origem ---
        tk.Label(
            body, text="Arquivo de origem:", bg="#f4f6f7", font=(self.family, 9, "bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.src_var = tk.StringVar()
        tk.Entry(body, textvariable=self.src_var, font=("Consolas", 9), relief="solid", bd=1).grid(
            row=0, column=1, sticky="ew", padx=(10, 8), pady=(0, 10)
        )
        self.src_btn = self._button(body, "Procurar...", self.browse_file, "#2980b9")
        self.src_btn.grid(row=0, column=2, pady=(0, 10))

        # --- Destino ---
        tk.Label(
            body, text="Salvar em:", bg="#f4f6f7", font=(self.family, 9, "bold"), anchor="w"
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))
        self.dst_var = tk.StringVar()
        tk.Entry(body, textvariable=self.dst_var, font=("Consolas", 9), relief="solid", bd=1).grid(
            row=1, column=1, sticky="ew", padx=(10, 8), pady=(0, 10)
        )
        self.dst_btn = self._button(body, "Procurar...", self.browse_dest, "#2980b9")
        self.dst_btn.grid(row=1, column=2, pady=(0, 10))

        # --- Opcoes ---
        opts = tk.LabelFrame(
            body,
            text="Opcoes",
            padx=12,
            pady=10,
            bg="#f4f6f7",
            font=(self.family, 9, "bold"),
            bd=1,
            relief="groove",
        )
        opts.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(6, 14))
        opts.columnconfigure(0, weight=1)

        self.plugins_var = tk.BooleanVar(value=False)
        self.keep_uris_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            opts,
            text="Usar plugins de terceiros (--use-plugins)",
            variable=self.plugins_var,
            bg="#f4f6f7",
            activebackground="#f4f6f7",
            font=(self.family, 9),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        tk.Checkbutton(
            opts,
            text="Manter data URIs (imagens base64) no resultado",
            variable=self.keep_uris_var,
            bg="#f4f6f7",
            activebackground="#f4f6f7",
            font=(self.family, 9),
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

        # --- Area central: progresso + log ---
        center = tk.Frame(container, bg="#f4f6f7", padx=22)
        center.pack(fill="both", expand=True, pady=(6, 0))
        center.columnconfigure(0, weight=1)
        center.rowconfigure(1, weight=1)

        prog_box = tk.LabelFrame(
            center,
            text="Progresso",
            padx=12,
            pady=10,
            bg="#f4f6f7",
            font=(self.family, 9, "bold"),
            bd=1,
            relief="groove",
        )
        prog_box.grid(row=0, column=0, sticky="ew")
        prog_box.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(prog_box, mode="indeterminate", length=600)
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.status_var = tk.StringVar(value="Pronto para converter.")
        tk.Label(
            prog_box,
            textvariable=self.status_var,
            bg="#f4f6f7",
            font=(self.family, 9),
            fg="#2c3e50",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew")

        # Log
        log_box = tk.LabelFrame(
            center,
            text="Registro",
            padx=8,
            pady=8,
            bg="#f4f6f7",
            font=(self.family, 9, "bold"),
            bd=1,
            relief="groove",
        )
        log_box.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        log_box.columnconfigure(0, weight=1)
        log_box.rowconfigure(0, weight=1)

        self.log = tk.Text(
            log_box,
            height=8,
            wrap="word",
            font=("Consolas", 9),
            bg="#ffffff",
            fg="#2c3e50",
            relief="flat",
            bd=0,
            insertbackground="#2c3e50",
            state="disabled",
        )
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_box, orient="vertical", command=self.log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)

        # --- Botoes ---
        buttons = tk.Frame(container, bg="#f4f6f7", pady=16)
        buttons.pack(fill="x")

        self.convert_btn = tk.Button(
            buttons,
            text="Converter",
            command=self.convert_file,
            bg="#27ae60",
            fg="white",
            font=(self.family, 11, "bold"),
            relief="flat",
            padx=26,
            pady=9,
            cursor="hand2",
            activebackground="#219a52",
            activeforeground="white",
            bd=0,
        )
        self.convert_btn.pack(side="left", padx=(0, 8))

        self.reset_btn = tk.Button(
            buttons,
            text="Limpar",
            command=self.reset_all,
            bg="#c0392b",
            fg="white",
            font=(self.family, 11),
            relief="flat",
            padx=20,
            pady=9,
            cursor="hand2",
            activebackground="#a93226",
            activeforeground="white",
            bd=0,
        )
        self.reset_btn.pack(side="left", padx=8)

        self.open_btn = tk.Button(
            buttons,
            text="Abrir pasta do resultado",
            command=self.open_output,
            bg="#7f8c8d",
            fg="white",
            font=(self.family, 11),
            relief="flat",
            padx=20,
            pady=9,
            cursor="hand2",
            state="disabled",
            activebackground="#707d8a",
            activeforeground="white",
            bd=0,
        )
        self.open_btn.pack(side="left", padx=8)

    def _button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            activebackground=color,
            activeforeground="white",
            bd=0,
            font=(self.family, 9),
        )

    def _bind_keys(self):
        self.root.bind("<Control-o>", lambda e: self.browse_file())
        self.root.bind("<Control-s>", lambda e: self.browse_dest())
        self.root.bind("<Control-Return>", lambda e: self.convert_file())
        self.root.bind("<Escape>", lambda e: self.reset_all())

    def _apply_cli_args(self, cli_args):
        """Permite iniciar ja com origem (e opcionalmente destino) pre-preenchidos."""
        if not cli_args:
            return
        self.src_var.set(str(cli_args[0]))
        if len(cli_args) > 1:
            self.dst_var.set(str(cli_args[1]))
        else:
            self.dst_var.set(str(Path(cli_args[0]).with_suffix(".md")))

    # --------------------------------------------------------------- Acoes
    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo para converter", filetypes=FILE_FILTERS
        )
        if path:
            self.src_var.set(path)
            if not self.dst_var.get().strip():
                self.dst_var.set(str(Path(path).with_suffix(".md")))

    def browse_dest(self):
        initial = self.dst_var.get().strip() or str(
            Path.home() / "Downloads" / "livros-md" / "documento.md"
        )
        try:
            Path(initial).parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            initial = str(Path.home() / "documento.md")
        path = filedialog.asksaveasfilename(
            title="Salvar Markdown como",
            defaultextension=".md",
            initialfile=initial,
            filetypes=[("Markdown", "*.md"), ("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if path:
            self.dst_var.set(path)

    def convert_file(self):
        if self._busy:
            return

        src = self.src_var.get().strip().strip('"')
        dst = self.dst_var.get().strip().strip('"')

        if not src:
            messagebox.showerror("Erro", "Selecione um arquivo de origem.")
            return
        if not dst:
            messagebox.showerror("Erro", "Escolha um arquivo de destino.")
            return

        src_path = Path(src).expanduser()
        dst_path = Path(dst).expanduser()

        if not src_path.is_file():
            messagebox.showerror("Erro", f"Arquivo de origem nao encontrado:\n{src_path}")
            return

        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            messagebox.showerror("Erro", f"Nao foi possivel criar o destino:\n{exc}")
            return

        self._set_busy(True)
        self.progress.configure(mode="indeterminate", value=0)
        self.progress.start(12)
        self._set_status("Carregando o motor de conversao...")
        self._log(f"Inicio: {src_path.name} -> {dst_path.name}", "info")

        opts = {
            "enable_plugins": bool(self.plugins_var.get()),
            "keep_data_uris": bool(self.keep_uris_var.get()),
        }
        threading.Thread(target=self._worker, args=(src_path, dst_path, opts), daemon=True).start()

    def _worker(self, src_path, dst_path, opts):
        try:
            self._set_status("Carregando conversores...")
            self._log("Importando markitdown...", "info")
            try:
                from markitdown import MarkItDown
            except ImportError:
                hint = pip_install_hint()
                self._log(f"markitdown nao encontrado. Instale com: {hint}", "erro")
                self._ui_call(
                    lambda: messagebox.showerror(
                        "Dependencia ausente",
                        f"O pacote 'markitdown' nao esta instalado.\n\n"
                        f"Execute no terminal:\n    {hint}",
                    )
                )
                return

            self._set_status(f"Convertendo {src_path.name}...")
            self._log(f"Convertendo {src_path} ({src_path.stat().st_size:,} bytes)", "info")

            md = MarkItDown(enable_plugins=opts["enable_plugins"])
            result = md.convert(str(src_path), keep_data_uris=opts["keep_data_uris"])

            self._set_status("Salvando o resultado...")
            dst_path.write_text(result.markdown, encoding="utf-8")

            chars = len(result.markdown)
            size_kb = dst_path.stat().st_size / 1024
            lines = result.markdown.count("\n") + 1
            self._log(f"OK: {chars:,} caracteres, {lines:,} linhas, {size_kb:,.1f} KB", "ok")
            self._set_status(f"Concluido: {dst_path.name} ({chars:,} caracteres)")
            self._ui_call(self._progress_complete)

            self._last_output = dst_path
            self._ui_call(lambda: self._enable_open_button(True))
            self._ui_call(lambda: self._on_success(dst_path, chars, size_kb))

        except Exception as exc:
            detail = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            self._log(f"ERRO: {detail}", "erro")
            self._set_status(f"Erro: {detail}")
            self._ui_call(self._progress_reset)
            self._ui_call(
                lambda d=detail: messagebox.showerror(
                    "Erro na conversao",
                    f"Nao foi possivel converter o arquivo.\n\n{d}\n\n"
                    "Se for PDF, instale as dependencias:\n"
                    "    pip install 'markitdown[all]'",
                )
            )
        finally:
            self._ui_call(self.progress.stop)
            self._set_busy(False)

    def _on_success(self, dst_path, chars, size_kb):
        messagebox.showinfo(
            "Conversao concluida",
            f"Arquivo salvo em:\n{dst_path}\n\n{chars:,} caracteres  |  {size_kb:,.1f} KB",
        )

    def open_output(self):
        if self._last_output:
            open_in_file_manager(self._last_output)

    def reset_all(self):
        if self._busy:
            return
        self.src_var.set("")
        self.dst_var.set("")
        self.plugins_var.set(False)
        self.keep_uris_var.set(False)
        self.status_var.set("Pronto para converter.")
        self._clear_log()
        self._enable_open_button(False)
        self._last_output = None

    def on_closing(self):
        if self._busy and not messagebox.askyesno(
            "Sair", "Uma conversao esta em andamento. Sair mesmo assim?"
        ):
            return
        # Sinaliza para a thread de conversao que a UI nao existe mais.
        with self._state_lock:
            self._closed = True
        self.root.destroy()

    # -------------------------------------------------------------- Widgets
    def _ui_call(self, func):
        """Agenda uma acao na thread principal de forma segura.

        Pode ser chamado de qualquer thread. Se a janela ja foi fechada,
        a chamada e simplesmente ignorada (sem excecao).
        """
        with self._state_lock:
            if self._closed:
                return
        try:
            self.root.after(0, func)
        except (RuntimeError, tk.TclError):
            # Janela destruida ou main loop encerrado.
            with self._state_lock:
                self._closed = True

    def _set_status(self, text):
        self._ui_call(lambda: self.status_var.set(text))

    def _set_busy(self, busy):
        self._busy = busy
        state = "disabled" if busy else "normal"
        for btn in (self.convert_btn, self.reset_btn, self.src_btn, self.dst_btn):
            self._ui_call(lambda b=btn, s=state: b.config(state=s))

    def _enable_open_button(self, enabled):
        self.open_btn.config(state="normal" if enabled else "disabled")

    def _progress_complete(self):
        """Barra deterministica em 100% apos a conversao."""
        self.progress.stop()
        self.progress.configure(mode="determinate", value=100)

    def _progress_reset(self):
        """Zera a barra após um erro."""
        self.progress.stop()
        self.progress.configure(mode="determinate", value=0)

    def _log(self, message, level="info"):
        colors = {"info": "#2c3e50", "ok": "#1e8449", "erro": "#c0392b"}
        color = colors.get(level, "#2c3e50")
        self._ui_call(lambda: self._write_log(message, color))

    def _write_log(self, message, color):
        self.log.configure(state="normal")
        self.log.insert("end", message.rstrip() + "\n", color)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")


def parse_args(argv):
    """Separa os argumentos posicionais das opcoes.

    Uso:
        markitdown_gui.py [arquivo] [destino] [--auto] [--no-gui]
    """
    auto = False
    no_gui = False
    positional = []
    for arg in argv:
        if arg == "--auto":
            auto = True
        elif arg == "--no-gui":
            no_gui = True
        elif arg.startswith("-"):
            continue
        else:
            positional.append(arg)
    return positional, auto, no_gui


def main():
    enable_windows_dpi_awareness()
    positional, auto, no_gui = parse_args(sys.argv[1:])

    # Modo linha de comando: converte e sai, sem abrir a janela.
    if no_gui:
        if not positional:
            print("Erro: informe o arquivo a converter.")
            return 2
        src = Path(positional[0])
        dst = Path(positional[1]) if len(positional) > 1 else src.with_suffix(".md")
        try:
            from markitdown import MarkItDown
        except ImportError:
            print(f"Erro: markitdown nao instalado. Use: {pip_install_hint()}")
            return 1
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            result = MarkItDown().convert(str(src))
            dst.write_text(result.markdown, encoding="utf-8")
        except Exception as exc:
            print(f"Erro na conversao: {exc}")
            return 1
        print(f"OK: {len(result.markdown):,} caracteres -> {dst}")
        return 0

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"\nErro ao iniciar a interface grafica: {exc}\n")
        if sys.platform.startswith("linux"):
            print("No Ubuntu/Debian instale o tkinter com:\n    sudo apt-get install python3-tk\n")
        elif sys.platform == "darwin":
            print("No macOS instale o tkinter com:\n    brew install python-tk\n")
        return 1

    app = MarkItDownGUI(root, positional, auto_start=auto)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
