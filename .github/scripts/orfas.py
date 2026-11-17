"""Checagem "orfas" (regra 28 do AGENTS.md).

Todo arquivo precisa de link no README.md da pasta onde está. Toda subpasta
precisa de link no README.md da pasta de cima, para a pasta ou para o
README.md dela. Ficam de fora os arquivos da raiz, .github/, .claude/ e a
tradução (regras 17 e 21). Conta link de Markdown, de referência e de HTML
(<a href>). Não conta link em bloco de código, entre crases, em comentário ou
de imagem. Link que começa com "/" parte da raiz. O resumo do README.md não é
conferido aqui: fica com o Copilot e com o Renato.
"""
import os
import re
import subprocess
import sys
import urllib.parse

LINK = re.compile(r"(?<!!)\[[^\]]*\]\((?:<([^>\n]+)>|((?:[^()\s]|\([^()\s]*\))+))")
HTML = re.compile(r"<a\s[^>]*href\s*=\s*[\"']([^\"']+)[\"']", re.I)
REFERENCIA = re.compile(r"^ {0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)", re.M)
FORA = re.compile(r"```.*?```|`[^`\n]*`|<!--.*?-->", re.S)


def de_fora(arq):
    return "/" not in arq or arq.startswith((".github/", ".claude/")) or "/traducao/" in arq


def destinos(readme):
    """Caminhos, a partir da raiz, para onde o README.md aponta."""
    with open(readme, encoding="utf-8") as f:
        texto = FORA.sub(" ", f.read())
    saida = set()
    alvos = [a or b for a, b in LINK.findall(texto)]
    for alvo in alvos + REFERENCIA.findall(texto) + HTML.findall(texto):
        alvo = urllib.parse.unquote(re.split(r"[#?]", alvo)[0])
        if not alvo or "://" in alvo or alvo.startswith("mailto:"):
            continue
        if alvo.startswith("/"):
            saida.add(os.path.normpath(alvo.lstrip("/")))
        else:
            saida.add(os.path.normpath(os.path.join(os.path.dirname(readme), alvo)))
    return saida


def orfas():
    lista = subprocess.run(["git", "-c", "core.quotePath=false", "ls-files"],
                           capture_output=True, text=True, check=True).stdout.split("\n")
    saida = []
    for arq in filter(None, lista):
        if de_fora(arq):
            continue
        pasta = os.path.dirname(arq)
        if os.path.basename(arq) == "README.md":
            de_cima = os.path.dirname(pasta)
            readme = os.path.join(de_cima, "README.md") if de_cima else "README.md"
            alvos = {pasta, arq}
        else:
            readme, alvos = os.path.join(pasta, "README.md"), {arq}
        if not os.path.exists(readme):
            saida.append((arq, f"Falta {readme} para apontar para este arquivo."))
        elif not destinos(readme) & alvos:
            saida.append((arq, f"Sem link em {readme}. Ponha um resumo com link."))
    return saida


if __name__ == "__main__":
    achou = orfas()
    for arq, msg in achou:
        print(f"::error file={arq}::Página órfã. {msg} (regra 28)")
    if not achou:
        print("Nenhuma página órfã.")
    sys.exit(1 if achou else 0)
