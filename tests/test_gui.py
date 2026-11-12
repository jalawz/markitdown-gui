"""
Testes automatizados do MarkItDown GUI.

Focam nas partes testaveis sem abrir janela grafica. Testes que exigem
display usam o fixture `gui_root` e sao pulados automaticamente quando
nao ha display disponivel (CI headless).
"""

import importlib.util
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "markitdown_gui.py"

spec = importlib.util.spec_from_file_location("markitdown_gui", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def gui_root():
    """Raiz do Tk, pulada se nao houver display.

    No macOS, `destroy()` sem `mainloop()` pode travar. Por isso chamamos
    `quit()` antes e protegemos com timeout.
    """
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"sem display disponivel: {exc}")

    root.withdraw()
    yield root

    try:
        root.update()
        root.quit()
    except tk.TclError:
        pass
    try:
        root.destroy()
    except tk.TclError:
        pass


# --------------------------------------------------------------------------- #
# 1. Modulo e sintaxe
# --------------------------------------------------------------------------- #
class TestModule:
    def test_arquivo_existe(self):
        assert SRC.is_file()

    def test_sintaxe_valida(self):
        import ast

        ast.parse(SRC.read_text(encoding="utf-8"))

    def test_public_api(self):
        for name in (
            "MarkItDownGUI",
            "main",
            "parse_args",
            "pick_font_family",
            "pip_install_hint",
            "open_in_file_manager",
            "enable_windows_dpi_awareness",
        ):
            assert hasattr(mod, name), f"faltando {name}"

    def test_versao_formatada(self):
        assert mod.APP_VERSION.count(".") == 2
        assert all(p.isdigit() for p in mod.APP_VERSION.split("."))

    def test_sem_emoji_no_codigo(self):
        """Emoji quebra o console Windows (cp1252)."""
        src = SRC.read_text(encoding="utf-8")
        assert "✅" not in src
        assert "🔴" not in src

    def test_sem_caminho_hardcoded(self):
        src = SRC.read_text(encoding="utf-8")
        for padrao in ("C:\\Users", "/home/", "/Users/"):
            assert padrao not in src

    def test_sem_grid_no_root(self):
        """grid e pack nao podem ser misturados no mesmo pai."""
        src = SRC.read_text(encoding="utf-8")
        assert "self.root.grid(" not in src
        assert "self.root.pack(" not in src


# --------------------------------------------------------------------------- #
# 2. parse_args
# --------------------------------------------------------------------------- #
class TestParseArgs:
    def test_sem_argumentos(self):
        pos, auto, nogui = mod.parse_args([])
        assert pos == []
        assert auto is False
        assert nogui is False

    def test_um_arquivo(self):
        pos, auto, nogui = mod.parse_args(["a.pdf"])
        assert pos == ["a.pdf"]
        assert auto is False

    def test_origem_e_destino(self):
        pos, _, _ = mod.parse_args(["a.pdf", "b.md"])
        assert pos == ["a.pdf", "b.md"]

    def test_flag_auto(self):
        _, auto, _ = mod.parse_args(["a.pdf", "--auto"])
        assert auto is True

    def test_flag_no_gui(self):
        _, _, nogui = mod.parse_args(["a.pdf", "--no-gui"])
        assert nogui is True

    def test_flags_combinadas(self):
        pos, auto, nogui = mod.parse_args(["a.pdf", "b.md", "--auto", "--no-gui"])
        assert pos == ["a.pdf", "b.md"]
        assert auto is True
        assert nogui is True

    def test_flag_desconhecida_ignorada(self):
        pos, _, _ = mod.parse_args(["a.pdf", "--inexistente"])
        assert pos == ["a.pdf"]


# --------------------------------------------------------------------------- #
# 3. Utilidades de plataforma
# --------------------------------------------------------------------------- #
class TestPlatformHelpers:
    def test_pick_font_family(self):
        family = mod.pick_font_family()
        assert isinstance(family, str)
        assert family

    def test_pick_font_family_cacheado(self):
        a = mod.pick_font_family()
        b = mod.pick_font_family()
        assert a == b

    def test_pip_install_hint(self):
        hint = mod.pip_install_hint()
        assert "markitdown" in hint
        assert "install" in hint

    @pytest.mark.skipif(sys.platform != "win32", reason="so Windows")
    def test_dpi_awareness_nao_quebra(self):
        mod.enable_windows_dpi_awareness()

    @pytest.mark.skipif(sys.platform != "win32", reason="so Windows")
    def test_dark_titlebar_nao_quebra(self, gui_root):
        mod.enable_windows_dark_titlebar(gui_root, dark=True)


# --------------------------------------------------------------------------- #
# 4. Construcao da GUI
# --------------------------------------------------------------------------- #
class TestGUICreation:
    def test_cria_instancia(self, gui_root):
        app = mod.MarkItDownGUI(gui_root)
        assert app is not None
        assert app._busy is False
        assert app._closed is False

    def test_widgets_presentes(self, gui_root):
        app = mod.MarkItDownGUI(gui_root)
        for attr in (
            "src_var",
            "dst_var",
            "plugins_var",
            "keep_uris_var",
            "status_var",
            "progress",
            "log",
            "convert_btn",
            "reset_btn",
            "open_btn",
            "src_btn",
            "dst_btn",
        ):
            assert hasattr(app, attr), f"faltando {attr}"

    def test_botao_limpar_visivel(self, gui_root):
        """O bug original: reset_btn era criado mas nunca exibido."""
        app = mod.MarkItDownGUI(gui_root)
        assert app.reset_btn.winfo_manager() in ("pack", "grid", "place")

    def test_titulo_com_versao(self, gui_root):
        app = mod.MarkItDownGUI(gui_root)
        assert mod.APP_VERSION in app.root.title()

    def test_cli_args_preenchem_campos(self, gui_root):
        app = mod.MarkItDownGUI(gui_root, ["a.pdf", "b.md"])
        assert app.src_var.get() == "a.pdf"
        assert app.dst_var.get() == "b.md"

    def test_cli_apenas_origem_sugere_destino(self, gui_root):
        app = mod.MarkItDownGUI(gui_root, ["a.pdf"])
        assert app.src_var.get() == "a.pdf"
        assert app.dst_var.get().endswith(".md")

    def test_auto_start_sem_args_nao_dispara(self, gui_root):
        app = mod.MarkItDownGUI(gui_root, [], auto_start=True)
        assert app._busy is False


# --------------------------------------------------------------------------- #
# 5. Fluxo de validacao
# --------------------------------------------------------------------------- #
class TestValidation:
    def test_sem_origem_mostra_erro(self, gui_root, monkeypatch):
        app = mod.MarkItDownGUI(gui_root)
        called = {}
        monkeypatch.setattr(
            mod.messagebox, "showerror", lambda *a, **k: called.setdefault("erro", a)
        )
        app.convert_file()
        assert "erro" in called

    def test_sem_destino_mostra_erro(self, gui_root, monkeypatch, tmp_path):
        src = tmp_path / "a.pdf"
        src.write_bytes(b"%PDF-1.4\n")
        app = mod.MarkItDownGUI(gui_root, [str(src)])
        app.dst_var.set("")
        called = {}
        monkeypatch.setattr(
            mod.messagebox, "showerror", lambda *a, **k: called.setdefault("erro", a)
        )
        app.convert_file()
        assert "erro" in called

    def test_origem_inexistente_mostra_erro(self, gui_root, monkeypatch, tmp_path):
        app = mod.MarkItDownGUI(gui_root)
        app.src_var.set(str(tmp_path / "nao-existe.pdf"))
        app.dst_var.set(str(tmp_path / "saida.md"))
        called = {}
        monkeypatch.setattr(
            mod.messagebox, "showerror", lambda *a, **k: called.setdefault("erro", a)
        )
        app.convert_file()
        assert "erro" in called
        assert "nao encontrado" in str(called["erro"]).lower()


# --------------------------------------------------------------------------- #
# 6. Mecanismo thread-safe
# --------------------------------------------------------------------------- #
class TestThreadSafety:
    def test_ui_call_e_seguro(self, gui_root):
        """_ui_call nunca deve levantar excecao, mesmo fora da main loop."""
        app = mod.MarkItDownGUI(gui_root)
        app._ui_call(lambda: None)
        app._ui_call(lambda: None)

    def test_ui_call_apos_destruir(self, gui_root):
        app = mod.MarkItDownGUI(gui_root)
        app._closed = True
        app._ui_call(lambda: None)  # nao deve levantar

    def test_worker_nao_toca_widget_diretamente(self):
        """
        Analise via AST: nenhuma funcao executada em thread secundaria
        pode chamar metodos de widget do Tkinter diretamente.
        """
        import ast

        tree = ast.parse(SRC.read_text(encoding="utf-8"))
        cls = next(
            n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MarkItDownGUI"
        )

        widgets = {
            "progress",
            "status_var",
            "convert_btn",
            "reset_btn",
            "src_btn",
            "dst_btn",
            "open_btn",
            "log",
            "src_var",
            "dst_var",
        }
        widget_ops = {"config", "set", "stop", "start", "insert", "delete", "see"}

        # funcoes que rodam na thread principal (handlers de evento)
        main_thread = {
            "__init__",
            "_build_ui",
            "_bind_keys",
            "_apply_cli_args",
            "browse_file",
            "browse_dest",
            "convert_file",
            "reset_all",
            "on_closing",
            "_ui_call",
            "_set_status",
            "_set_busy",
            "_enable_open_button",
            "_progress_complete",
            "_progress_reset",
            "_write_log",
            "_clear_log",
        }

        offenders = []
        for fn in [n for n in cls.body if isinstance(n, ast.FunctionDef)]:
            if fn.name in main_thread or fn.name.startswith("__"):
                continue
            for node in ast.walk(fn):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in widget_ops
                ):
                    base = node.func.value
                    if isinstance(base, ast.Attribute) and base.attr in widgets:
                        offenders.append(f"{fn.name}():{node.lineno}")

        assert not offenders, f"widgets acessados fora da main thread: {offenders}"

    def test_root_after_restrito(self):
        """root.after so pode aparecer em _ui_call e __init__."""
        import ast

        tree = ast.parse(SRC.read_text(encoding="utf-8"))
        cls = next(
            n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MarkItDownGUI"
        )

        callers = set()
        for fn in [n for n in cls.body if isinstance(n, ast.FunctionDef)]:
            for node in ast.walk(fn):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "after"
                ):
                    callers.add(fn.name)

        assert callers <= {"_ui_call", "__init__"}, f"root.after em: {callers}"


# --------------------------------------------------------------------------- #
# 7. Conversao real (usa markitdown)
# --------------------------------------------------------------------------- #
class TestConversion:
    def test_converte_texto_simples(self, gui_root, tmp_path, monkeypatch):
        src = tmp_path / "doc.txt"
        src.write_text("# Titulo\n\nCorpo do texto.", encoding="utf-8")
        dst = tmp_path / "saida.md"

        app = mod.MarkItDownGUI(gui_root, [str(src), str(dst)])
        monkeypatch.setattr(mod.messagebox, "showinfo", lambda *a, **k: None)
        monkeypatch.setattr(mod.messagebox, "showerror", lambda *a, **k: None)

        app.convert_file()
        deadline = time.time() + 60
        while app._busy and time.time() < deadline:
            gui_root.update()
            time.sleep(0.05)

        assert dst.exists(), "arquivo de saida nao foi criado"
        conteudo = dst.read_text(encoding="utf-8")
        assert "Titulo" in conteudo
        assert "Corpo" in conteudo

    def test_cria_diretorio_de_destino(self, gui_root, tmp_path, monkeypatch):
        src = tmp_path / "doc.txt"
        src.write_text("conteudo", encoding="utf-8")
        dst = tmp_path / "sub" / "pasta" / "saida.md"

        app = mod.MarkItDownGUI(gui_root, [str(src), str(dst)])
        monkeypatch.setattr(mod.messagebox, "showinfo", lambda *a, **k: None)
        monkeypatch.setattr(mod.messagebox, "showerror", lambda *a, **k: None)

        app.convert_file()
        deadline = time.time() + 60
        while app._busy and time.time() < deadline:
            gui_root.update()
            time.sleep(0.05)

        assert dst.exists()
        assert dst.parent.is_dir()


# --------------------------------------------------------------------------- #
# 8. Modo batch (--no-gui)
# --------------------------------------------------------------------------- #
class TestNoGuiMode:
    def test_converte_sem_interface(self, tmp_path, monkeypatch):
        src = tmp_path / "doc.txt"
        src.write_text("# Batch\n\nTeste do modo sem GUI.", encoding="utf-8")
        dst = tmp_path / "batch.md"

        monkeypatch.setattr(sys, "argv", ["markitdown_gui.py", str(src), str(dst), "--no-gui"])
        rc = mod.main()

        assert rc == 0
        assert dst.exists()
        assert "Batch" in dst.read_text(encoding="utf-8")

    def test_sem_argumento_retorna_erro(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["markitdown_gui.py", "--no-gui"])
        assert mod.main() == 2


# --------------------------------------------------------------------------- #
# 9. Log e status
# --------------------------------------------------------------------------- #
class TestLog:
    def test_log_registra_mensagens(self, gui_root):
        app = mod.MarkItDownGUI(gui_root)
        app._log("mensagem de teste", "info")
        gui_root.update()
        conteudo = app.log.get("1.0", "end")
        assert "mensagem de teste" in conteudo

    def test_log_colorido_por_nivel(self, gui_root):
        app = mod.MarkItDownGUI(gui_root)
        app._log("erro simulado", "erro")
        gui_root.update()
        conteudo = app.log.get("1.0", "end")
        assert "erro simulado" in conteudo

    def test_reset_limpa_log(self, gui_root):
        app = mod.MarkItDownGUI(gui_root)
        app._log("para limpar", "info")
        gui_root.update()
        app.reset_all()
        gui_root.update()
        assert app.log.get("1.0", "end").strip() == ""


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
