#!/usr/bin/env bash
# Checagem "tipo-e-tamanho": barra, nos arquivos novos ou alterados do pedido,
# os tipos proibidos e o arquivo acima do limite. Faz o papel da regra de
# envio do GitHub, que só vale em repositório privado.
# Ambiente: BASE e HEAD (o pedido), BLOQUEAR (extensões separadas por espaço)
# e LIMITE (em bytes).
set -u
erro=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  nome=$(basename "$f")
  ext=""
  case "$nome" in *.*) ext=$(printf '%s' "${nome##*.}" | tr '[:upper:]' '[:lower:]') ;; esac
  for b in $BLOQUEAR; do
    if [ "$ext" = "$b" ]; then
      echo "::error file=$f::Tipo de arquivo proibido: .$ext."
      erro=1
    fi
  done
  tam=$(git cat-file -s "$HEAD:$f")
  if [ "$tam" -gt "$LIMITE" ]; then
    echo "::error file=$f::Arquivo com $tam bytes. O limite é $LIMITE."
    erro=1
  fi
done < <(git -c core.quotePath=false diff --name-only --diff-filter=AMR "$BASE...$HEAD")
[ "$erro" -eq 0 ] && echo "Nenhum arquivo proibido nem acima de $LIMITE bytes."
exit "$erro"
