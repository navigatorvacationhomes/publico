"""Teste de regressão da checagem "prazos"."""
import datetime
import os
import subprocess
import sys
import tempfile

from prazos import vencidas

HOJE = datetime.date(2027, 2, 11)
casos = [
    ("no prazo", "Em teste até: 2027-02-12.", 0),
    ("vencida", "Em teste até: 2027-02-10.", 1),
    ("quebra de linha", "Em teste até:\n2027-02-10.", 1),
    ("revisão vencida", "Próxima revisão: 2026-01-01", 1),
    ("data que não existe", "Em teste até: 2027-02-30.", 1),
    ("duas marcas", "Em teste até: 2027-01-01. Próxima revisão: 2027-01-02", 2),
    ("sem marca", "Texto qualquer de 2020-01-01.", 0),
    ("exemplo em bloco de código", "```markdown\nEm teste até: 2027-02-10.\n```", 0),
    ("exemplo entre crases", "`Em teste até: 2027-02-10`", 0),
]
falhou = False
for nome, texto, esperado in casos:
    if len(vencidas(texto, HOJE)) != esperado:
        print(f"::error::Caso errado: {nome}")
        falhou = True

# Os dois modos. "pedido" confere só o que mudou; "semanal" confere tudo.
script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prazos.py")


def git(t, *args):
    return subprocess.run(["git", "-C", t, "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


with tempfile.TemporaryDirectory() as t:
    git(t, "init", "-q")
    with open(os.path.join(t, "velho.md"), "w", encoding="utf-8") as f:
        f.write("Em teste até: 2020-01-01.\n")
    git(t, "add", "-A")
    git(t, "commit", "-qm", "base")
    base = git(t, "rev-parse", "HEAD")
    with open(os.path.join(t, "novo.md"), "w", encoding="utf-8") as f:
        f.write("Sem marca.\n")
    git(t, "add", "-A")
    git(t, "commit", "-qm", "pedido sem data vencida")
    sem = git(t, "rev-parse", "HEAD")
    with open(os.path.join(t, "velho.md"), "a", encoding="utf-8") as f:
        f.write("Mais texto.\n")
    git(t, "add", "-A")
    git(t, "commit", "-qm", "pedido que mexe no arquivo vencido")
    com = git(t, "rev-parse", "HEAD")
    for nome, modo, head, esperado in (
        ("pedido que não mexe no arquivo vencido", "pedido", sem, 0),
        ("pedido que mexe no arquivo vencido", "pedido", com, 1),
        ("rodada semanal", "semanal", com, 1),
    ):
        ambiente = dict(os.environ, BASE=base, HEAD=head)
        r = subprocess.run([sys.executable, script, modo], cwd=t, env=ambiente,
                           capture_output=True, text=True)
        if r.returncode != esperado or (esperado and "::error file=velho.md::" not in r.stdout):
            print(f"::error::Modo errado: {nome} (saída {r.returncode})")
            falhou = True
print("Teste de regressão: certo." if not falhou else "Teste de regressão falhou.")
sys.exit(1 if falhou else 0)
