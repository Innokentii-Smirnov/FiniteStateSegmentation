import os
from os import path
import argparse
import pandas as pd
from lexicon import Lexicon
from typing import Any
import json
DATA_REPOSITORY = 'MorphyNet'
DATA_FILE_NAME_TEMPLATE = '{0}.derivational.v1.tsv'
SEP = '\t'
COLUMN_NAMES = ['base', 'derivative', 'base_pos', 'deriv_pos', 'affix', 'affix_type']
ENDING_FILE_NAME = 'Endings.json'
LEXICON_DIRECTORY_TEMPLATE = '{0}/src'
LEXICON_FILE_NAME = 'Affixes.lexc'
UNKNOWN_POS_SYMBOL = 'U'
language_codes = list[str]()
if not path.exists(DATA_REPOSITORY):
  print('The repository {0} with the data could not be found.'.format(DATA_REPOSITORY))
  exit()
for file_or_directory in os.listdir(DATA_REPOSITORY):
  full_path = path.join(DATA_REPOSITORY, file_or_directory)
  if path.isdir(full_path):
    language_code = file_or_directory
    data_file = path.join(full_path, DATA_FILE_NAME_TEMPLATE.format(language_code))
    if path.exists(data_file):
      language_codes.append(language_code)
parser = argparse.ArgumentParser(
  prog='generate_affix_lexicon.py',
  description='Generate a Foma affix lexicon for the specified language'
)
parser.add_argument('language_code', choices=language_codes,
                    help='the three-letter code of a language for which a lexicon should be generated')
args = parser.parse_args()
language_code = args.language_code
data_frame_file = path.join(DATA_REPOSITORY, language_code,
                            DATA_FILE_NAME_TEMPLATE.format(language_code))
df = pd.read_csv(data_frame_file, sep=SEP, names=COLUMN_NAMES)
print(df.head())
parts_of_speech = set(df['base_pos']) | set(df['deriv_pos'])
parts_of_speech.remove(UNKNOWN_POS_SYMBOL)
ending_file_path = path.join(language_code, ENDING_FILE_NAME)
with open(ending_file_path, 'r', encoding='utf-8') as fin:
  endings: dict[str, list[str]] = json.load(fin)
lexicon = Lexicon(parts_of_speech, endings)
row: Any = None
derivations = set[tuple[str, str]]()
for row in df.itertuples(name='DerivationalPair'):
  derivations.add((row.derivative, row.deriv_pos))
bases = set[tuple[str, str]]()
for row in df.itertuples(name='DerivationalPair'):
  bases.add((row.base, row.base_pos))
underived = bases - derivations
for base, base_pos in underived:
  if base_pos != UNKNOWN_POS_SYMBOL:
    lexicon.add_citation_form(base, base_pos)
for row in df.itertuples(name='DerivationalPair'):
  if row.base_pos != UNKNOWN_POS_SYMBOL and row.deriv_pos != UNKNOWN_POS_SYMBOL:
    lexicon.add(row)
lexicon_directory = LEXICON_DIRECTORY_TEMPLATE.format(language_code)
os.makedirs(lexicon_directory, exist_ok=True)
lexicon_full_path = path.join(lexicon_directory, LEXICON_FILE_NAME)
lexicon.store(lexicon_full_path)
