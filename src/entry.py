from dataclasses import dataclass

LEXICON_ROW_TEMPLATE = '{0}\t{1};'
LEXICON_CLASS_ROW_TEMPLATE = '{0};'

@dataclass(frozen=True)
class Entry:
  form: str
  next_class: str

  def to_lexicon_line(self) -> str:
    return LEXICON_ROW_TEMPLATE.format(self.form, self.next_class)

  def __lt__(self, other: Entry | ClassEntry) -> bool:
    if isinstance(other, ClassEntry):
      return True
    else:
      return self.form < other.form and self.next_class < other.next_class

@dataclass(frozen=True)
class ClassEntry:
  next_class: str

  def to_lexicon_line(self) -> str:
    return LEXICON_CLASS_ROW_TEMPLATE.format(self.next_class)

  def __lt__(self, other: Entry | ClassEntry) -> bool:
    if isinstance(other, Entry):
      return False
    else:
      return self.next_class < other.next_class
