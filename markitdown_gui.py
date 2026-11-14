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

import json
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

try:
    from tkinterdnd2 import DND_FILES

    HAS_DND = True
except ImportError:
    HAS_DND = False

APP_NAME = "MarkItDown GUI"
APP_VERSION = "1.1.0"
CONFIG_DIR_NAME = "markitdown-gui"
CONFIG_FILE_NAME = "config.json"

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


def get_config_dir() -> Path:
    """Retorna o diretorio de configuracao por plataforma."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / CONFIG_DIR_NAME


def get_config_path() -> Path:
    """Retorna o caminho completo do arquivo de configuracao."""
    return get_config_dir() / CONFIG_FILE_NAME


def load_config() -> dict:
    """Carrega a configuracao do arquivo JSON. Retorna dict vazio se nao existir ou invalido."""
    path = get_config_path()
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_config(config: dict) -> None:
    """Salva a configuracao no arquivo JSON."""
    path = get_config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # Falha silenciosa: configuracao e apenas conveniencia
        pass


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

        # Inicializa variaveis de controle
        self.src_var = tk.StringVar()
        self.dst_var = tk.StringVar()
        self.plugins_var = tk.BooleanVar(value=False)
        self.keep_uris_var = tk.BooleanVar(value=False)

        # Inicializa fila de conversao
        self._queue = []
        self._queue_index = 0
        self._total_files = 0
        self._cancel_requested = False

        self._build_ui()
        self._bind_keys()

        # Carrega configuracao salva (diretorios recentes)
        self._load_config()

        self._apply_cli_args(cli_args)

        if auto_start and cli_args:
            self.root.after(400, self.convert_queue)

        # Configura drag-and-drop se disponivel
        if HAS_DND:
            self._setup_drag_drop()

    def _setup_drag_drop(self):
        """Configura drag-and-drop para a janela e campos de entrada."""
        try:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self._on_drop)

            # Torna os campos de entrada tambem alvos de drop
            if hasattr(self, "src_entry"):
                self.src_entry.drop_target_register(DND_FILES)
                self.src_entry.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event):
        """Manipula eventos de drag-and-drop."""
        files = self.root.tk.splitlist(event.data)
        if not files:
            return

        # Filtra apenas arquivos suportados
        valid_files = []
        for f in files:
            path = Path(f)
            if path.is_file() and path.suffix.lower() in {
                ".pdf",
                ".docx",
                ".doc",
                ".pptx",
                ".ppt",
                ".xlsx",
                ".xls",
                ".html",
                ".htm",
                ".csv",
                ".json",
                ".xml",
                ".txt",
                ".md",
                ".epub",
                ".ipynb",
                ".msg",
                ".wav",
                ".mp3",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
            }:
                valid_files.append(path)

        if not valid_files:
            self._log("Nenhum arquivo valido foi solto.", "erro")
            return

        # Adiciona arquivos validos a fila
        for path in valid_files:
            src_path = path
            dst_path = path.with_suffix(".md")
            self._queue.append((src_path, dst_path))

        self._update_queue_display()
        self._log(f"{len(valid_files)} arquivo(s) adicionado(s) via drag-and-drop.", "info")

    def _load_config(self):
        """Carrega configuracao salva e preenche campos se nao ha args CLI."""
        config = load_config()
        if not self.src_var.get().strip() and config.get("last_source_dir"):
            self.src_var.set(config["last_source_dir"])
        if not self.dst_var.get().strip() and config.get("last_dest_dir"):
            self.dst_var.set(config["last_dest_dir"])

    def _save_config(self, src_dir: str | None = None, dst_dir: str | None = None):
        """Salva configuracao com diretorios atualizados."""
        config = load_config()
        if src_dir:
            config["last_source_dir"] = src_dir
        if dst_dir:
            config["last_dest_dir"] = dst_dir
        save_config(config)

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

        # Corpo: fila de arquivos, opcoes
        body = tk.Frame(container, bg="#f4f6f7", padx=22, pady=18)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        # --- Fila de arquivos ---
        tk.Label(
            body, text="Fila de conversao:", bg="#f4f6f7", font=(self.family, 9, "bold"), anchor="w"
        ).grid(row=0, column=0, sticky="nw", pady=(0, 6))

        # Frame da lista com scrollbar
        queue_frame = tk.Frame(body, bg="#f4f6f7")
        queue_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=(10, 0), pady=(0, 10))
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)

        self.queue_listbox = tk.Listbox(
            queue_frame,
            height=6,
            font=("Consolas", 9),
            relief="solid",
            bd=1,
            selectmode=tk.EXTENDED,
            activestyle="none",
        )
        self.queue_listbox.grid(row=0, column=0, sticky="nsew")

        queue_scrollbar = ttk.Scrollbar(
            queue_frame, orient="vertical", command=self.queue_listbox.yview
        )
        queue_scrollbar.grid(row=0, column=1, sticky="ns")
        self.queue_listbox.configure(yscrollcommand=queue_scrollbar.set)

        # Botoes da fila
        queue_btns = tk.Frame(body, bg="#f4f6f7")
        queue_btns.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(4, 0))

        self.add_to_queue_btn = self._button(
            queue_btns, "Adicionar a fila", self.add_to_queue, "#2980b9"
        )
        self.add_to_queue_btn.pack(side="left", padx=(0, 6))

        # Aliases para compatibilidade com testes antigos
        self.src_btn = self.add_to_queue_btn
        self.dst_btn = self.add_to_queue_btn

        self.remove_from_queue_btn = self._button(
            queue_btns, "Remover selecionados", self.remove_from_queue, "#e67e22"
        )
        self.remove_from_queue_btn.pack(side="left", padx=6)

        self.clear_queue_btn = self._button(queue_btns, "Limpar fila", self.clear_queue, "#e74c3c")
        self.clear_queue_btn.pack(side="left", padx=6)

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

        # Progress bar com label de porcentagem
        prog_top = tk.Frame(prog_box, bg="#f4f6f7")
        prog_top.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        prog_top.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(prog_top, mode="determinate", length=500)
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.progress_pct_var = tk.StringVar(value="0%")
        tk.Label(
            prog_top,
            textvariable=self.progress_pct_var,
            bg="#f4f6f7",
            font=(self.family, 9, "bold"),
            fg="#2c3e50",
            width=5,
        ).grid(row=0, column=1, sticky="e")

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
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        buttons.columnconfigure(2, weight=1)
        buttons.columnconfigure(2, weight=1)
        buttons.columnconfigure(2, weight=1)

        self.convert_btn = tk.Button(
            buttons,
            text="Converter fila",
            command=self.convert_queue,
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
        self.convert_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.cancel_btn = tk.Button(
            buttons,
            text="Cancelar",
            command=self.cancel_queue,
            bg="#e74c3c",
            fg="white",
            font=(self.family, 11, "bold"),
            relief="flat",
            padx=26,
            pady=9,
            cursor="hand2",
            state="disabled",
            activebackground="#c0392b",
            activeforeground="white",
            bd=0,
        )
        self.cancel_btn.grid(row=0, column=1, padx=8, sticky="ew")

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
        self.reset_btn.grid(row=0, column=2, padx=8, sticky="ew")

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
        self.open_btn.grid(row=0, column=3, padx=8, sticky="ew")

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
        src = Path(cli_args[0]).expanduser()
        dst = Path(cli_args[1]).expanduser() if len(cli_args) > 1 else src.with_suffix(".md")

        self.src_var.set(str(src))
        self.dst_var.set(str(dst))

        # Adiciona a fila se o arquivo existe
        if src.is_file():
            self._queue.append((src, dst))
            self._update_queue_display()

    # --------------------------------------------------------------- Acoes
    # --------------------------------------------------------------- Acoes
    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo para converter", filetypes=FILE_FILTERS
        )
        if path:
            self.src_var.set(path)
            self._save_config(src_dir=str(Path(path).parent))
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
            self._save_config(dst_dir=str(Path(path).parent))

    # --------------------------------------------------------------- Fila
    def add_to_queue(self):
        """Adiciona o arquivo atual (origem/destino) a fila de conversao."""
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

        # Adiciona a fila
        self._queue.append((src_path, dst_path))
        self._update_queue_display()

        # Limpa campos para proximo
        self.src_var.set("")
        self.dst_var.set("")
        self.src_btn.focus_set()

    def remove_from_queue(self):
        """Remove itens selecionados da fila."""
        selection = self.queue_listbox.curselection()
        if not selection:
            return
        # Remove do fim pro inicio para nao baguncar indices
        for idx in reversed(selection):
            del self._queue[idx]
        self._update_queue_display()

    def clear_queue(self):
        """Limpa toda a fila."""
        self._queue.clear()
        self._update_queue_display()

    def _update_queue_display(self):
        """Atualiza a listbox com o conteudo da fila."""
        self.queue_listbox.delete(0, tk.END)
        for src, dst in self._queue:
            self.queue_listbox.insert(tk.END, f"{src.name} -> {dst.name}")

    # --------------------------------------------------------------- Acoes
    def convert_queue(self):
        """Inicia a conversao da fila de arquivos."""
        if self._busy:
            return

        if not self._queue:
            messagebox.showerror("Erro", "A fila esta vazia. Adicione arquivos primeiro.")
            return

        # Valida que todos os itens tem destino
        for _src, dst in self._queue:
            if not str(dst).strip():
                messagebox.showerror(
                    "Erro", "Todos os arquivos da fila devem ter um destino definido."
                )
                return

        # Desabilita botoes durante a conversao
        self._set_busy(True)
        self.cancel_btn.config(state="normal")
        self.convert_btn.config(state="disabled")

        self._cancel_requested = False
        self._queue_index = 0
        self._total_files = len(self._queue)

        # Configura progress bar
        self.progress.configure(mode="determinate", maximum=len(self._queue), value=0)
        self.progress_pct_var.set("0%")

        self._process_next_in_queue()

    def cancel_queue(self):
        """Cancela a conversao da fila atual."""
        if not self._busy:
            return
        self._cancel_requested = True
        self._log("Cancelamento solicitado pelo usuario...", "erro")
        self._set_status("Cancelando...")

    def _process_next_in_queue(self):
        """Processa o proximo arquivo da fila."""
        if self._cancel_requested or self._queue_index >= len(self._queue):
            self._finish_queue()
            return

        src_path, dst_path = self._queue[self._queue_index]

        # Atualiza UI
        self.progress.configure(value=self._queue_index)
        self.progress_pct_var.set(f"{int((self._queue_index / len(self._queue)) * 100)}%")
        self._set_status(f"Convertendo {self._queue_index + 1}/{len(self._queue)}: {src_path.name}")
        self._log(f"Iniciando {self._queue_index + 1}/{len(self._queue)}: {src_path.name}", "info")

        # Seleciona o item na listbox
        self.queue_listbox.selection_clear(0, tk.END)
        self.queue_listbox.selection_set(self._queue_index)
        self.queue_listbox.see(self._queue_index)

        opts = {
            "enable_plugins": bool(self.plugins_var.get()),
            "keep_data_uris": bool(self.keep_uris_var.get()),
        }

        threading.Thread(target=self._worker, args=(src_path, dst_path, opts), daemon=True).start()

    def _finish_queue(self):
        """Finaliza o processamento da fila."""
        self._ui_call(self._finish_queue_internal)

    def _finish_queue_internal(self):
        """Finaliza o processamento da fila (chamado na thread principal)."""
        self._set_busy(False)
        self.cancel_btn.config(state="disabled")
        self.convert_btn.config(state="normal")

        if self._cancel_requested:
            self.progress.configure(value=0)
            self.progress_pct_var.set("0%")
            self._set_status("Fila cancelada.")
            self._log("Fila cancelada pelo usuario.", "erro")
        else:
            self.progress.configure(value=len(self._queue))
            self.progress_pct_var.set("100%")
            self._set_status(f"Fila concluida: {len(self._queue)} arquivo(s) processado(s).")
            self._log(f"Fila finalizada: {len(self._queue)} arquivo(s) processado(s).", "ok")

        self._queue.clear()
        self._update_queue_display()
        self._enable_open_button(False)

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
            dst_path.parent.mkdir(parents=True, exist_ok=True)
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

            # Salva os diretorios usados para proxima vez
            self._save_config(src_dir=str(src_path.parent), dst_dir=str(dst_path.parent))

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

        # Salva os diretorios usados para proxima vez
        try:
            save_config({"last_source_dir": str(src.parent), "last_dest_dir": str(dst.parent)})
        except Exception:
            pass  # Falha silenciosa: configuracao e apenas conveniencia

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
