"""Teste de regressão da checagem "orfas"."""
import os
import subprocess
import sys
import tempfile

script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orfas.py")
falhou = False


def escreve(t, caminho, texto):
    os.makedirs(os.path.dirname(os.path.join(t, caminho)) or t, exist_ok=True)
    with open(os.path.join(t, caminho), "w", encoding="utf-8") as f:
        f.write(texto)


# (nome, texto do README de 10-19/12, arquivos extras, esperado)
ALVO = "2026-11-13_12.01_alvo.md"
casos = [
    ("link normal", f"[a]({ALVO})", {}, 0),
    ("sem link", "Nada.", {}, 1),
    ("link só em bloco de código", f"```\n[a]({ALVO})\n```", {}, 1),
    ("link só entre crases", f"`[a]({ALVO})`", {}, 1),
    ("link só em comentário", f"<!-- [a]({ALVO}) -->", {}, 1),
    ("link só de imagem", f"![a]({ALVO})", {}, 1),
    ("link com âncora", f"[a]({ALVO}#parte)", {}, 0),
    ("link com parâmetro", f"[a]({ALVO}?raw=1)", {}, 0),
    ("link com espaço codificado", f"[a]({ALVO.replace('_alvo', '_alvo%20x')})",
     {"rename": ALVO.replace("_alvo", "_alvo x")}, 0),
    ("link de referência", f"[a][r]\n\n[r]: {ALVO}", {}, 0),
    ("maiúscula errada", f"[a]({ALVO.replace('alvo', 'Alvo')})", {}, 1),
    ("link para outro arquivo", "[a](outro.md)", {}, 1),
    ("link com ./ na frente", f"[a](./{ALVO})", {}, 0),
    ("link em HTML", f'<a href="{ALVO}">a</a>', {}, 0),
    ("link em HTML só em comentário", f'<!-- <a href="{ALVO}">a</a> -->', {}, 1),
    ("link que começa com barra", f"[a](/10-19/12/{ALVO})", {}, 0),
    ("link com barra para outra pasta", f"[a](/10-19/{ALVO})", {}, 1),
    ("nome com parênteses", "[a](2026-11-13_12.01_alvo-(v2).md)",
     {"rename": "2026-11-13_12.01_alvo-(v2).md"}, 0),
    ("título entre aspas", f'[a]({ALVO} "Título")', {}, 0),
    ("destino entre <>", "[a](<2026-11-13_12.01_alvo com espaço.md>)",
     {"rename": "2026-11-13_12.01_alvo com espaço.md"}, 0),
    ("nome com acento", "[a](2026-11-13_12.01_decisão.md)",
     {"rename": "2026-11-13_12.01_decisão.md"}, 0),
]
for nome, readme, extra, esperado in casos:
    with tempfile.TemporaryDirectory() as t:
        alvo = extra.get("rename", ALVO)
        escreve(t, "README.md", "[d](10-19/README.md)")
        escreve(t, "10-19/README.md", "[c](12/README.md)")
        escreve(t, "10-19/12/README.md", readme)
        escreve(t, "10-19/12/" + alvo, "Texto.")
        escreve(t, ".github/x.md", "Fora.")
        escreve(t, "10-19/12/traducao/y.md", "Fora.")
        escreve(t, "AGENTS.md", "Raiz.")
        subprocess.run(["git", "init", "-q", t], check=True)
        subprocess.run(["git", "-C", t, "add", "-A"], check=True)
        r = subprocess.run([sys.executable, script], cwd=t, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if r.returncode != esperado:
            print(f"::error::Caso errado: {nome} (saída {r.returncode})")
            falhou = True

# Subpastas: ligada pela pasta, pelo README.md dela, sem link e sem README.
for nome, cima, tem_readme, esperado in (
    ("subpasta ligada pela pasta", "[s](sub/)", True, 0),
    ("subpasta ligada pelo README.md", "[s](sub/README.md)", True, 0),
    ("subpasta ligada por HTML", '<a href="sub/">s</a>', True, 0),
    ("subpasta ligada com barra", "[s](/10-19/sub/)", True, 0),
    ("subpasta sem link", "Nada.", True, 1),
    ("pasta sem README.md", "[a](sub/a.md)", False, 1),
):
    with tempfile.TemporaryDirectory() as t:
        escreve(t, "README.md", "[d](10-19/)")
        escreve(t, "10-19/README.md", cima)
        if tem_readme:
            escreve(t, "10-19/sub/README.md", "[a](a.md)")
        escreve(t, "10-19/sub/a.md", "Texto.")
        subprocess.run(["git", "init", "-q", t], check=True)
        subprocess.run(["git", "-C", t, "add", "-A"], check=True)
        r = subprocess.run([sys.executable, script], cwd=t, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if r.returncode != esperado:
            print(f"::error::Caso errado: {nome} (saída {r.returncode})")
            falhou = True
print("Teste de regressão: certo." if not falhou else "Teste de regressão falhou.")
sys.exit(1 if falhou else 0)
