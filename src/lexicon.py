from typing import Iterable
from collections import defaultdict
import logging
from entry import Entry, ClassEntry
from morpheme import Morpheme

ROOT_LEXICON_NAME = 'Root'
PREFIX_LEXICON_NAME = 'Prefixes'
PREFIX_CLASS_ENTRY = ClassEntry(PREFIX_LEXICON_NAME)
END_OF_WORD_NEXT_CLASS = '#'
END_OF_WORD_ENTRY = ClassEntry(END_OF_WORD_NEXT_CLASS)
LEXICON_HEADER_TEMPLATE = 'LEXICON {0}'
MORPHEME_BOUNDARY = '-'
ZERO_ENDING_MARKER = 'zero'

def get_root_positional_class(part_of_speech: str) -> str:
  return part_of_speech + 'Root'

def get_suffix_positional_class(base_pos: str) -> str:
  return base_pos

def get_paradigm_class(part_of_speech: str, citation_form_ending: str) -> str:
  if citation_form_ending != '':
    return part_of_speech + citation_form_ending
  else:
    return part_of_speech + ZERO_ENDING_MARKER

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
    for part_of_speech, ending_list in self.endings.items():
      for ending_form in ending_list:
        paradigm_class = get_paradigm_class(part_of_speech, ending_form)
        ending = Morpheme(ending_form, paradigm_class, END_OF_WORD_NEXT_CLASS, 'suffix')
        self.add_ending(ending)
        self.enable_derivation(paradigm_class, part_of_speech)

  def detach_ending(self, form: str, part_of_speech: str, is_root: bool) -> tuple[str, str] | None:
    endings = self.endings[part_of_speech]
    for ending in endings:
      if form.endswith(ending):
        if not is_root or len(form) - len(ending) > 1:
          return form[:len(form)-len(ending)], ending
    return None

  @property
  def lexicon_order(self) -> list[str]:
    order = ([ROOT_LEXICON_NAME]
      + [part_of_speech + 'Root' for part_of_speech in self.parts_of_speech]
      + [PREFIX_LEXICON_NAME]
      + self.parts_of_speech)
    other = sorted(set(self.lexicons) - set(order))
    return order + other

  def add_morph(self, morpheme: Morpheme) -> None:
    entry = Entry(morpheme.form_with_boundary, morpheme.next_positional_class)
    self.lexicons[morpheme.positional_class].add(entry)

  def add_category_preserving_prefix(self, form: str, base_pos: str) -> None:
    next_positional_class = get_root_positional_class(base_pos)
    prefix = Morpheme(form, PREFIX_LEXICON_NAME, next_positional_class, 'prefix')
    self.add_morph(prefix)

  def add_suffix_with_attached_ending(self, form: str, base_pos: str, deriv_pos: str) -> None:
    suffix = self.detach_ending_from_suffix(form, base_pos, deriv_pos)
    if suffix is not None:
      self.add_suffix(suffix)
    else:
      logging.warning('No ending could be detached from %s %s %s', form, base_pos, deriv_pos)

  def add_citation_form(self, citation_form: str, part_of_speech: str) -> None:
    if ' ' not in citation_form:
      root = self.detach_ending_from_root(citation_form, part_of_speech)
      if root is not None:
        self.add_morph(root)
      else:
        logging.warning('No ending could be detached from %s %s', citation_form, part_of_speech)

  def add_suffix(self, suffix: Morpheme) -> None:
    if suffix.form != '':
      self.add_morph(suffix)

  def add_ending(self, ending: Morpheme) -> None:
    if ending.form != '':
      self.add_morph(ending)
    else:
      self.enable_derivation(ending.positional_class, END_OF_WORD_NEXT_CLASS)

  def detach_ending_from_root(self, citation_form: str, part_of_speech: str) -> Morpheme | None:
    result = self.detach_ending(citation_form, part_of_speech, True)
    if result is not None:
      root_form, ending_form = result
      paradigm_class = get_paradigm_class(part_of_speech, ending_form)
      if root_form == '':
        raise ValueError(citation_form + ' ' + part_of_speech)
      root = Morpheme(root_form, get_root_positional_class(part_of_speech), paradigm_class, 'root')
      return root
    else:
      return None

  def detach_ending_from_suffix(self, suffix_with_ending: str, base_pos: str, deriv_pos: str) -> Morpheme | None:
    result = self.detach_ending(suffix_with_ending, deriv_pos, False)
    if result is not None:
      suffix_form, ending_form = result
      paradigm_class = get_paradigm_class(deriv_pos, ending_form)
      suffix = Morpheme(suffix_form, get_suffix_positional_class(base_pos), paradigm_class, 'suffix')
      return suffix
    else:
      return None

  def enable_derivation(self, positional_class: str, next_positional_class: str) -> None:
    self.lexicons[positional_class].add(ClassEntry(next_positional_class))

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
