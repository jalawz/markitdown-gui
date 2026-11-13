"""Auditoria de conteudo: procura typos, links quebrados e incoerencias."""

import re
from pathlib import Path

ROOT = Path(".")
problemas = []

# --- 1. Typos conhecidos / placeholders ---
TYPOS = {
    "REQUIRED": "placeholder esquecido",
    "TODO": "TODO nao resolvido",
    "FIXME": "FIXME nao resolvido",
    "XXX": "placeholder",
    "eREQUIRED": "typo de 'e REQUIRED'",
}

for f in sorted(ROOT.rglob("*.md")):
    if ".git" in f.parts:
        continue
    txt = f.read_text(encoding="utf-8")
    for typo, desc in TYPOS.items():
        for m in re.finditer(re.escape(typo), txt):
            linha = txt[: m.start()].count("\n") + 1
            problemas.append(f"{f}:{linha} -> {typo} ({desc})")

# --- 2. Links internos quebrados ---
for f in sorted(ROOT.rglob("*.md")):
    if ".git" in f.parts:
        continue
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r"\]\(([^)#:]+\.md)(?:#[^)]*)?\)", txt):
        alvo = f.parent / m.group(1)
        if not alvo.exists():
            linha = txt[: m.start()].count("\n") + 1
            problemas.append(f"{f}:{linha} -> link quebrado: {m.group(1)}")

# --- 3. Arquivos referenciados no README que nao existem ---
readme = (ROOT / "README.md").read_text(encoding="utf-8")
for m in re.finditer(r"`([\w./-]+\.(?:py|md|toml|txt|bat|sh|yml|yaml))`", readme):
    nome = m.group(1)
    if nome.startswith("http"):
        continue
    if "/" in nome and not (ROOT / nome).exists():
        # pode ser um caminho ilustrativo
        continue
    if not (ROOT / nome).exists() and "*" not in nome:
        problemas.append(f"README.md -> arquivo citado e inexistente: {nome}")

# --- 4. Coerencia de versao ---
gui = (ROOT / "markitdown_gui.py").read_text(encoding="utf-8")
m = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', gui)
versao_app = m.group(1) if m else None
pyproj = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
m2 = re.search(r'^version\s*=\s*"([^"]+)"', pyproj, re.M)
versao_proj = m2.group(1) if m2 else None
if versao_app != versao_proj:
    problemas.append(
        f"versao divergente: markitdown_gui.py={versao_app} vs pyproject.toml={versao_proj}"
    )

# --- 5. AGENTS.md cita arquivos que existem? ---
agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
for m in re.finditer(r"`(tests/[\w./-]+\.py|scripts/[\w./-]+\.py|docs/[\w./-]+\.md)`", agents):
    if not (ROOT / m.group(1)).exists():
        problemas.append(f"AGENTS.md -> arquivo inexistente: {m.group(1)}")

# --- 6. Status do backlog coerente com os arquivos ---
if "CHANGELOG.md" not in agents:
    problemas.append("AGENTS.md -> nao menciona CHANGELOG.md")

print("=" * 62)
if problemas:
    print(f"{len(problemas)} PROBLEMA(S):\n")
    for p in problemas:
        print("  -", p)
else:
    print("Nenhum problema encontrado.")
print("=" * 62)
print(f"Versao no codigo : {versao_app}")
print(f"Versao no projeto: {versao_proj}")
print("=" * 62)
