language_code="$1"
cut -f 2 "MorphyNet/$language_code/$language_code.derivational.v1.tsv" \
  > "$language_code/input.txt"
