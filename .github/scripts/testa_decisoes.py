"""Teste de regressão da checagem "decisoes"."""
import os
import subprocess
import sys
import tempfile

from decisoes import so_situacao

falhou = False
REG = "- Situação: aceito\n\n## Decisão\n\nTexto.\n"
casos = [
    ("igual", REG, REG, True),
    ("situação para substituído", REG, REG.replace("aceito", "substituído pelo 00.03 seguinte"), True),
    ("situação para outra coisa", REG, REG.replace("aceito", "cancelado"), False),
    ("texto mudado", REG, REG.replace("Texto.", "Outro texto."), False),
    ("linha nova", REG, REG + "Mais.\n", False),
    ("substituído fora da linha da situação", REG, REG.replace("Texto.", "substituído"), False),
    ("situação aceita junto com substituído", REG, REG.replace("aceito", "aceito; substituído"), False),
    ("situação com maiúscula", REG, REG.replace("aceito", "Substituído pelo seguinte"), True),
    ("espaço no fim da situação", REG, REG.replace("aceito", "substituído   "), True),
    ("espaço no fim de outra linha", REG, REG.replace("Texto.", "Texto.  "), False),
    ("maiúscula em outra linha", REG, REG.replace("Texto.", "texto."), False),
    ("já era substituído", REG.replace("aceito", "substituído"), REG.replace("aceito", "substituído por outro"), False),
    ("duas linhas de situação", REG + "- Situação: aceito\n",
     (REG + "- Situação: aceito\n").replace("aceito", "substituído", 1), False),
    ("sem linha de situação", "Texto.\n", "Texto.\n", False),
]
for nome, velho, novo, esperado in casos:
    if so_situacao(velho, novo) != esperado:
        print(f"::error::Caso errado: {nome}")
        falhou = True

script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decisoes.py")
P = "00-09-sistema/00-indice-e-governanca/00.03-registros-de-decisao/"


def git(t, *args):
    return subprocess.run(["git", "-C", t, "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def escreve(t, caminho, texto):
    os.makedirs(os.path.dirname(os.path.join(t, caminho)), exist_ok=True)
    with open(os.path.join(t, caminho), "w", encoding="utf-8") as f:
        f.write(texto)


with tempfile.TemporaryDirectory() as t:
    git(t, "init", "-q")
    escreve(t, P + "README.md", "Índice.\n")
    escreve(t, P + "2026-11-13_00.03_um.md", REG)
    escreve(t, P + "anexos/README.md", "Subpasta.\n")
    git(t, "add", "-A")
    git(t, "commit", "-qm", "base")
    base = git(t, "rev-parse", "HEAD")
    pedidos = (
        ("registro novo", lambda: escreve(t, P + "2026-11-14_00.03_dois.md", REG), 0),
        ("README mudado", lambda: escreve(t, P + "README.md", "Índice novo.\n"), 0),
        ("situação para substituído",
         lambda: escreve(t, P + "2026-11-13_00.03_um.md", REG.replace("aceito", "substituído")), 0),
        ("texto editado",
         lambda: escreve(t, P + "2026-11-13_00.03_um.md", REG.replace("Texto.", "Outro.")), 1),
        ("registro apagado", lambda: os.remove(os.path.join(t, P + "2026-11-13_00.03_um.md")), 1),
        ("registro renomeado", lambda: os.rename(os.path.join(t, P + "2026-11-13_00.03_um.md"),
                                                 os.path.join(t, P + "2026-11-13_00.03_outro.md")), 1),
        ("registro movido para fora do 00.03",
         lambda: os.rename(os.path.join(t, P + "2026-11-13_00.03_um.md"), os.path.join(t, "um.md")), 1),
        ("README de subpasta mudado", lambda: escreve(t, P + "anexos/README.md", "Outro.\n"), 1),
        ("arquivo de mesmo nome fora do 00.03",
         lambda: escreve(t, "outra/2026-11-13_00.03_um.md", "Outro.\n"), 0),
        ("dois envios, o segundo edita",
         [lambda: escreve(t, P + "2026-11-14_00.03_dois.md", REG),
          lambda: escreve(t, P + "2026-11-13_00.03_um.md", REG.replace("Texto.", "Outro."))], 1),
        ("dois envios, o segundo desfaz a edição",
         [lambda: escreve(t, P + "2026-11-13_00.03_um.md", REG.replace("Texto.", "Outro.")),
          lambda: escreve(t, P + "2026-11-13_00.03_um.md", REG)], 0),
    )
    for nome, muda, esperado in pedidos:
        git(t, "checkout", "-q", "-B", "pedido", base)
        for passo in (muda if isinstance(muda, list) else [muda]):
            passo()
            git(t, "add", "-A")
            git(t, "commit", "-qm", nome, "--allow-empty")
        head = git(t, "rev-parse", "HEAD")
        r = subprocess.run([sys.executable, script], cwd=t, capture_output=True, text=True,
                           env=dict(os.environ, BASE=base, HEAD=head, PYTHONDONTWRITEBYTECODE="1"))
        if r.returncode != esperado or (esperado and "::error file=" not in r.stdout):
            print(f"::error::Pedido errado: {nome} (saída {r.returncode})")
            falhou = True
print("Teste de regressão: certo." if not falhou else "Teste de regressão falhou.")
sys.exit(1 if falhou else 0)
