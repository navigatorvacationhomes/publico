"""Checagem "prazos" (regra 22 do AGENTS.md).

Procura "Em teste até: AAAA-MM-DD" (regra 22) e "Próxima revisão: AAAA-MM-DD"
(regra 8) em todo o texto dos arquivos .md e aponta as datas vencidas ou que
não existem. Exemplo entre crases ou em bloco de código não conta.

Modo "pedido": confere só os .md mudados no pedido (BASE e HEAD no ambiente).
Modo "semanal": confere todos os .md. Nos dois, data vencida deixa vermelho.
"""
import datetime
import os
import re
import subprocess
import sys

MARCA = re.compile(r"(Em teste até|Próxima revisão):\s*(\d{4}-\d{2}-\d{2})")
CODIGO = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def vencidas(texto, hoje):
    """Devolve [(marca, data)] vencidas. A marca pode quebrar de linha."""
    texto = re.sub(r"\s+", " ", CODIGO.sub(" ", texto))
    saida = []
    for nome, data in MARCA.findall(texto):
        try:
            dia = datetime.date.fromisoformat(data)
        except ValueError:
            saida.append((nome, data + " (data que não existe)"))
            continue
        if dia < hoje:
            saida.append((nome, data))
    return saida


def arquivos(modo):
    if modo == "pedido":
        faixa = f"{os.environ['BASE']}...{os.environ['HEAD']}"
        cmd = ["git", "-c", "core.quotePath=false", "diff", "--name-only",
               "--diff-filter=AMR", faixa, "--", "*.md"]
    else:
        cmd = ["git", "-c", "core.quotePath=false", "ls-files", "*.md"]
    saida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [a for a in saida.split("\n") if a]


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo not in ("pedido", "semanal"):
        sys.exit("Uso: prazos.py pedido|semanal")
    achou = False
    lista = arquivos(modo)
    for arq in lista:
        with open(arq, encoding="utf-8") as f:
            for nome, data in vencidas(f.read(), datetime.date.today()):
                print(f"::error file={arq}::'{nome}: {data}' venceu. O Renato decide: "
                      "manter, mudar ou apagar (regra 22).")
                achou = True
    if not achou:
        print(f"Nenhuma data vencida em {len(lista)} arquivo(s).")
    sys.exit(1 if achou else 0)
