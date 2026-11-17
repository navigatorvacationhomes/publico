#!/usr/bin/env bash
# Teste de regressão da checagem "prosa": cada caso tem de dar o resultado
# esperado (0 = passa, 1 = barra). Frase longa só avisa, então passa.
set -u
raiz=$(git rev-parse --show-toplevel)
t=$(mktemp -d)
casos=(
  "certo|0|O CNPJ da empresa e o arquivo \`MD043\` ficam."
  "excecoes|0|O ID 15.01, a data AAAA-MM-DD, o README e o AGENTS ficam. A área de TI também."
  "sigla com crases|0|O termo \`ENTRA\` entre crases fica."
  "sigla|1|A IA escreve."
  "maiusculas|1|Esta frase ENTRA aqui."
  "proibida|1|Texto com xxpalavra-proibida-de-testexx."
  "longa|0|$(printf 'palavra %.0s' $(seq 30))fim."
)
falhou=0
for caso in "${casos[@]}"; do
  IFS='|' read -r nome esperado texto <<< "$caso"
  printf '# Título\n\n%s\n' "$texto" > "$t/$nome.md"
  vale --config="$raiz/.vale.ini" --no-wrap "$t/$nome.md" > /dev/null; codigo=$?
  [ "$codigo" -eq "$esperado" ] || { echo "::error::Caso errado: $nome (saída $codigo, esperada $esperado)"; falhou=1; }
done
rm -rf "$t"
[ "$falhou" -eq 0 ] && echo "Teste de regressão: ${#casos[@]} casos certos."
exit "$falhou"
