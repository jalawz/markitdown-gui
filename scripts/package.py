#!/usr/bin/env python3
"""
Empacota o executavel gerado pelo PyInstaller.

Uso:
    python scripts/package.py

Produz em dist/:
    markitdown-gui-windows.zip    (Windows)
    markitdown-gui-<OS>.tar.gz   (Linux / macOS)

Usa shutil.make_archive em vez do comando `zip`, que nao existe no
Git Bash dos runners do Windows.
"""

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
EXE_NAME = "markitdown-gui"


def main() -> int:
    if not DIST.is_dir():
        print(f"ERRO: diretorio {DIST} nao encontrado.", file=sys.stderr)
        return 1

    if os.name == "nt":
        target = DIST / f"{EXE_NAME}.exe"
        if not target.is_file():
            print(f"ERRO: {target} nao encontrado.", file=sys.stderr)
            return 1
        archive = shutil.make_archive(
            str(DIST / f"{EXE_NAME}-windows"),
            "zip",
            root_dir=str(target.parent),
            base_dir=target.name,
        )
    else:
        binary = DIST / EXE_NAME
        if not binary.is_file():
            print(f"ERRO: {binary} nao encontrado.", file=sys.stderr)
            return 1
        runner_os = os.environ.get("RUNNER_OS", "linux")
        archive = shutil.make_archive(
            str(DIST / f"{EXE_NAME}-{runner_os}"),
            "gztar",
            root_dir=str(binary.parent),
            base_dir=binary.name,
        )

    size_mb = Path(archive).stat().st_size / (1024 * 1024)
    print(f"OK: {archive} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
