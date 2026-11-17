#!/usr/bin/env bash
# Teste de regressão da checagem "tipo-e-tamanho": cada caso tem de dar o
# resultado esperado (0 = passa, 1 = barra).
set -u
script="$(cd "$(dirname "$0")" && pwd)/tipo-e-tamanho.sh"
casos=(
  "texto.md|10|0"
  "foto.jpg|10|1"
  "FOTO.JPG|10|1"
  "planilha.xlsx|10|1"
  "sem-extensao|10|0"
  "grande.md|1000001|1"
  "no-limite.md|1000000|0"
  "pasta.pdf/arquivo.md|10|0"
)
falhou=0
for caso in "${casos[@]}"; do
  IFS='|' read -r arq bytes esperado <<< "$caso"
  t=$(mktemp -d)
  git -C "$t" init -q
  git -C "$t" -c user.name=t -c user.email=t@t commit -q --allow-empty -m base
  mkdir -p "$t/$(dirname "$arq")"
  head -c "$bytes" /dev/zero > "$t/$arq"
  git -C "$t" add -A
  git -C "$t" -c user.name=t -c user.email=t@t commit -q -m caso
  (cd "$t" && BASE=HEAD~1 HEAD=HEAD BLOQUEAR="pdf doc docx xls xlsx jpg jpeg heic zip exe pyc" \
    LIMITE=1000000 bash "$script" > /dev/null)
  codigo=$?
  [ "$codigo" -eq "$esperado" ] || { echo "::error::Caso errado: $arq (saída $codigo, esperada $esperado)"; falhou=1; }
  rm -rf "$t"
done
[ "$falhou" -eq 0 ] && echo "Teste de regressão: ${#casos[@]} casos certos."
exit "$falhou"
