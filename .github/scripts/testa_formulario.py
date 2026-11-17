"""Teste de regressão da checagem "formulario": cada caso tem de dar o
resultado esperado."""
import sys

from formulario import conferir

with open(".github/pull_request_template.md", encoding="utf-8") as f:
    MODELO = f.read()
CERTO = MODELO.replace("\n\n## ", "\n\ntexto\n\n## ").rstrip() + "\n\ntexto\n"
CERTO = CERTO.replace("(sim/não)\n\ntexto", "(sim/não)\n\nnão")

casos = [
    ("certo", CERTO, True),
    ("sem nada", "", False),
    ("senha sim", CERTO.replace("(sim/não)\n\nnão", "(sim/não)\n\nsim"), False),
    ("senha vazia", CERTO.replace("(sim/não)\n\nnão", "(sim/não)\n\n"), False),
    ("campo só com comentário", CERTO.replace("## Meta\n\ntexto", "## Meta\n\n<!-- x -->"), False),
    ("título apagado", CERTO.replace("## Que regra gerou isto?", "## Outro"), False),
    ("título mudado de lugar", CERTO.replace("## Meta\n\ntexto\n\n", "")
     .replace("## Que regra gerou isto?", "## Que regra gerou isto?\n\ntexto\n\n## Meta"), False),
]
falhou = False
for nome, corpo, passa in casos:
    if (not conferir(corpo, MODELO)) != passa:
        print(f"::error::Caso errado: {nome}")
        falhou = True
print("Teste de regressão: certo." if not falhou else "Teste de regressão falhou.")
sys.exit(1 if falhou else 0)
