from typing import Iterable
from collections import defaultdict
from entry import Entry, ClassEntry
from derivational_pair import DerivationalPair

ROOT_LEXICON_NAME = 'Root'
PREFIX_LEXICON_NAME = 'Prefixes'
PREFIX_CLASS_ENTRY = ClassEntry(PREFIX_LEXICON_NAME)
END_OF_WORD_NEXT_CLASS = '#'
END_OF_WORD_ENTRY = ClassEntry(END_OF_WORD_NEXT_CLASS)
ROOT_FORM_TEMPLATE = '<?+>'
LEXICON_HEADER_TEMPLATE = 'LEXICON {0}'

class Lexicon:
  lexicons: defaultdict[str, set[Entry | ClassEntry]]
  parts_of_speech: list[str]

  def __init__(self, parts_of_speech: Iterable[str]):
    self.lexicons = defaultdict(set)
    self.parts_of_speech = sorted(parts_of_speech)
    root_lexicon = self.lexicons[ROOT_LEXICON_NAME]
    root_lexicon.add(PREFIX_CLASS_ENTRY)
    for part_of_speech in parts_of_speech:
      root_entry = Entry(ROOT_FORM_TEMPLATE, part_of_speech)
      root_lexicon.add(root_entry)
      self.lexicons[part_of_speech].add(END_OF_WORD_ENTRY)

  @property
  def lexicon_order(self) -> list[str]:
    return [ROOT_LEXICON_NAME, PREFIX_LEXICON_NAME] + sorted(self.parts_of_speech)

  def add(self, row: DerivationalPair) -> None:
    form: str = row.affix
    match row.affix_type:
      case 'prefix':
        if row.base_pos == row.deriv_pos:
          lexicon_name = PREFIX_LEXICON_NAME
          next_class: str = row.base_pos
        else:
          return
      case 'suffix':
        lexicon_name = row.base_pos
        next_class = row.deriv_pos
      case _:
        return
    entry = Entry(form, next_class)
    self.lexicons[lexicon_name].add(entry)

  def store(self, file_name: str) -> None:
    with open(file_name, 'w', encoding='utf-8') as fout:
      for i, lexicon_name in enumerate(self.lexicon_order):
        if i > 0:
          print(file=fout)
        entries = self.lexicons[lexicon_name]
        lexicon_header = LEXICON_HEADER_TEMPLATE.format(lexicon_name)
        print(lexicon_header, file=fout)
        for lexicon_entry in sorted(entries):
          print(lexicon_entry.to_lexicon_line(), file=fout)
