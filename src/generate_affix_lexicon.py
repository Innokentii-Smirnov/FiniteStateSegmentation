import os
from os import path
import argparse
import pandas as pd
from entry import Entry, ClassEntry
from collections import defaultdict
from typing import Any
DATA_REPOSITORY = 'MorphyNet'
DATA_FILE_NAME_TEMPLATE = '{0}.derivational.v1.tsv'
SEP = '\t'
COLUMN_NAMES = ['base', 'derivative', 'base_pos', 'deriv_pos', 'affix', 'affix_type']
PREFIX_LEXICON_NAME = 'Prefixes'
LEXICON_DIRECTORY_TEMPLATE = '{0}/src'
LEXICON_FILE_NAME = 'Affixes.lexc'
ROOT_FORM_TEMPLATE = '<?*>'
LEXICON_HEADER_TEMPLATE = 'LEXICON {0}'
UNKNOWN_POS_SYMBOL = 'U'
ROOT_LEXICON_NAME = 'Root'
END_OF_WORD_NEXT_CLASS = '#'
END_OF_WORD_ENTRY = ClassEntry(END_OF_WORD_NEXT_CLASS)
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
lexicons: defaultdict[str, set[Entry | ClassEntry]] = defaultdict(set)
parts_of_speech = set[str]()
row: Any = None
for row in df.itertuples():
  if row.base_pos != UNKNOWN_POS_SYMBOL and row.deriv_pos != UNKNOWN_POS_SYMBOL:
    parts_of_speech.add(row.base_pos)
    parts_of_speech.add(row.deriv_pos)
    form: str = row.affix
    match row.affix_type:
      case 'prefix':
        if row.base_pos == row.deriv_pos:
          lexicon_name = PREFIX_LEXICON_NAME
          next_class: str = row.base_pos
        else:
          continue
      case 'suffix':
        lexicon_name = row.base_pos
        next_class = row.deriv_pos
      case _:
        continue
    entry = Entry(form, next_class)
    lexicons[lexicon_name].add(entry)
root_lexicon_entries = lexicons[ROOT_LEXICON_NAME]
prefix_class_entry = ClassEntry(PREFIX_LEXICON_NAME)
root_lexicon_entries.add(prefix_class_entry)
for part_of_speech in parts_of_speech:
  root_entry = Entry(ROOT_FORM_TEMPLATE, part_of_speech)
  root_lexicon_entries.add(root_entry)
  lexicons[part_of_speech].add(END_OF_WORD_ENTRY)
lexicon_directory = LEXICON_DIRECTORY_TEMPLATE.format(language_code)
os.makedirs(lexicon_directory, exist_ok=True)
lexicon_full_path = path.join(lexicon_directory, LEXICON_FILE_NAME)
lexicon_order = [ROOT_LEXICON_NAME, PREFIX_LEXICON_NAME] + sorted(parts_of_speech)
with open(lexicon_full_path, 'w', encoding='utf-8') as fout:
  for lexicon_name in lexicon_order:
    entries = lexicons[lexicon_name]
    lexicon_header = LEXICON_HEADER_TEMPLATE.format(lexicon_name)
    print(lexicon_header, file=fout)
    for lexicon_entry in sorted(entries):
      print(lexicon_entry.to_lexicon_line(), file=fout)
    print(file=fout)
