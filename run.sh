language_code="$1"
clear
env/bin/mypy --strict src && \
env/bin/python src/generate_lexicon.py "$language_code" || exit
cd spa && \
../CompileFST/CompileFST.sh src/Segmentation.foma
cd ..
git diff "$language_code/src/Lexicon.lexc" "$language_code/output.txt"
