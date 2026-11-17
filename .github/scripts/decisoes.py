"""Checagem "decisoes" (regra 28 do AGENTS.md).

Registro de decisão já juntado no 00.03 não se edita, não se apaga e não se
move. Única mudança aceita: a linha "- Situação:", e só para "substituído".
Só o README.md da raiz da pasta fica de fora. BASE e HEAD vêm do ambiente.
"""
import os
import subprocess
import sys

PASTA = "00-09-sistema/00-indice-e-governanca/00.03-registros-de-decisao/"
SITUACAO = "- Situação:"
README = PASTA + "README.md"


def git(*args):
    return subprocess.run(["git", "-c", "core.quotePath=false", *args],
                          capture_output=True, text=True, check=True).stdout


def valor(linha):
    return linha[len(SITUACAO):].strip().lower()


def so_situacao(velho, novo):
    """Verdadeiro se a única diferença é a situação, mudada para substituído.

    O registro tem uma linha de situação só. O valor novo começa com
    "substituído", e o antigo não começava.
    """
    a, b = velho.split("\n"), novo.split("\n")
    if len(a) != len(b):
        return False
    if sum(x.startswith(SITUACAO) for x in a) != 1 or sum(y.startswith(SITUACAO) for y in b) != 1:
        return False
    for x, y in zip(a, b):
        if x == y:
            continue
        if not (x.startswith(SITUACAO) and y.startswith(SITUACAO)
                and valor(y).startswith("substituído")
                and not valor(x).startswith("substituído")):
            return False
    return True


def problemas(base, head):
    base = git("merge-base", base, head).strip()
    saida = []
    for linha in git("diff", "--name-status", "-M", base, head, "--", PASTA).splitlines():
        partes = linha.split("\t")
        estado, arq = partes[0], partes[-1]
        velho = partes[1]
        if velho == README and arq == README:
            continue
        if estado == "A":
            continue
        if estado == "D":
            saida.append((velho, "Registro aprovado não se apaga."))
        elif estado.startswith("R"):
            saida.append((velho, "Registro aprovado não se move nem muda de nome."))
        elif estado == "M":
            if not so_situacao(git("show", f"{base}:{velho}"), git("show", f"{head}:{arq}")):
                saida.append((arq, "Registro aprovado não se edita. Só a linha "
                                   "'- Situação:' pode mudar, para 'substituído'."))
        else:
            saida.append((arq, f"Mudança '{estado}' não aceita em registro aprovado."))
    return saida


if __name__ == "__main__":
    achou = problemas(os.environ["BASE"], os.environ["HEAD"])
    for arq, msg in achou:
        print(f"::error file={arq}::{msg} (regra 28)")
    if not achou:
        print("Nenhum registro de decisão aprovado foi editado.")
    sys.exit(1 if achou else 0)
