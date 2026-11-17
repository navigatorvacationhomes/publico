"""Checagem "formulario" (regra 26 do AGENTS.md).

Os títulos saem do próprio formulário, .github/pull_request_template.md
(fonte única, regra 1). Barra o pedido quando falta um título, quando os títulos
estão fora da ordem do formulário, quando um campo está vazio ou quando a
resposta sobre senha não é "não" (regra 9).
"""
import os
import re
import sys

MODELO = ".github/pull_request_template.md"
SIGILO = "## Tem senha"


def secoes(texto):
    """Devolve {título: conteúdo} das seções '## ' do texto."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    partes = {}
    atual = None
    for linha in texto.splitlines():
        if linha.startswith("## "):
            atual = linha.strip()
            partes[atual] = ""
        elif atual:
            partes[atual] += linha + "\n"
    return partes


def conferir(corpo, modelo):
    erros = []
    pedido = secoes(corpo)
    titulos = list(secoes(modelo))
    achados = [t for t in pedido if t in titulos]
    if achados != [t for t in titulos if t in pedido]:
        erros.append("Os títulos estão fora da ordem do formulário.")
    for titulo in titulos:
        if titulo not in pedido:
            erros.append(f"Falta o título do formulário: {titulo}")
        elif not pedido[titulo].strip():
            erros.append(f"Campo vazio: {titulo}")
        elif titulo.startswith(SIGILO):
            resposta = pedido[titulo].strip().lower().rstrip(".")
            if resposta not in ("não", "nao"):
                erros.append(f"{titulo}: a resposta tem de ser 'não' (regra 9).")
    return erros


if __name__ == "__main__":
    with open(MODELO, encoding="utf-8") as f:
        modelo = f.read()
    erros = conferir(os.environ.get("CORPO", ""), modelo)
    for erro in erros:
        print(f"::error::{erro}")
    if not erros:
        print("Formulário preenchido.")
    sys.exit(1 if erros else 0)
