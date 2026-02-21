language_code="$1"
line_number="$2"
sed -n "${line_number}p" "$language_code/input.txt" \
  | flookup "$language_code/src/Segmentation.bin"
