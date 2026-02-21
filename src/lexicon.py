from typing import Iterable
from collections import defaultdict
from entry import Entry, ClassEntry
from derivational_pair import DerivationalPair

ROOT_LEXICON_NAME = 'Root'
PREFIX_LEXICON_NAME = 'Prefixes'
PREFIX_CLASS_ENTRY = ClassEntry(PREFIX_LEXICON_NAME)
END_OF_WORD_NEXT_CLASS = '#'
END_OF_WORD_ENTRY = ClassEntry(END_OF_WORD_NEXT_CLASS)
LEXICON_HEADER_TEMPLATE = 'LEXICON {0}'
MORPHEME_BOUNDARY = '-'

def add_boundary(affix_form: str, affix_type: str) -> str:
  match affix_type:
    case 'prefix':
      return affix_form + MORPHEME_BOUNDARY
    case 'suffix':
      return MORPHEME_BOUNDARY + affix_form
    case _:
      raise ValueError('Unsupported affix type: {0}.'.format(affix_type))

class Lexicon:
  lexicons: defaultdict[str, set[Entry | ClassEntry]]
  parts_of_speech: list[str]
  endings: dict[str, list[str]]

  def __init__(self, parts_of_speech: Iterable[str], endings: dict[str, list[str]]):
    self.lexicons = defaultdict(set)
    self.parts_of_speech = sorted(parts_of_speech)
    root_lexicon = self.lexicons[ROOT_LEXICON_NAME]
    root_lexicon.add(PREFIX_CLASS_ENTRY)
    for part_of_speech in parts_of_speech:
      root_lexicon.add(ClassEntry(part_of_speech + 'Root'))
    self.endings = endings

  def detach_ending(self, form: str, part_of_speech: str) -> tuple[str, str]:
    endings = self.endings[part_of_speech]
    for ending in endings:
      if len(ending) < len(form) and form.endswith(ending):
        return form[:-len(ending)], ending
    return form, ''

  @property
  def lexicon_order(self) -> list[str]:
    order = ([ROOT_LEXICON_NAME]
      + [part_of_speech + 'Root' for part_of_speech in self.parts_of_speech]
      + [PREFIX_LEXICON_NAME]
      + self.parts_of_speech)
    other = sorted(set(self.lexicons) - set(order))
    return order + other

  def add(self, row: DerivationalPair) -> None:
    form: str = add_boundary(row.affix, row.affix_type)
    match row.affix_type:
      case 'prefix':
        if row.base_pos == row.deriv_pos:
          lexicon_name = PREFIX_LEXICON_NAME
          next_class: str = row.base_pos + 'Root'
        else:
          return
      case 'suffix':
        lexicon_name = row.base_pos
        next_class = row.deriv_pos
      case _:
        return
    entry = Entry(form, next_class)
    self.lexicons[lexicon_name].add(entry)

  def add_root(self, citation_form: str, part_of_speech: str) -> None:
    root, ending = self.detach_ending(citation_form, part_of_speech)
    if ' ' not in root:
      if ending == '':
        inflectional_class_lexicon_name = part_of_speech + 'zero'
        ending_entry: Entry | ClassEntry = END_OF_WORD_ENTRY
      else:
        inflectional_class_lexicon_name = part_of_speech + ending
        ending_entry = Entry('-' + ending, END_OF_WORD_NEXT_CLASS)
      self.lexicons[part_of_speech + 'Root'].add(Entry( '({0})'.format(root), inflectional_class_lexicon_name))
      self.lexicons[inflectional_class_lexicon_name].add(ending_entry)
      self.lexicons[inflectional_class_lexicon_name].add(ClassEntry(part_of_speech))

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
