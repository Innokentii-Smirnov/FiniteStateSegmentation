from dataclasses import dataclass
from typing import Literal

ROOT_TEMPLATE = '({0})'
MORPHEME_BOUNDARY = '-'

@dataclass(frozen=True, order=True)
class Morpheme:
  form: str
  positional_class: str
  next_positional_class: str
  morpheme_type: Literal['prefix', 'root', 'suffix']

  @property
  def form_with_boundary(self) -> str:
    match self.morpheme_type:
      case 'prefix':
        return self.form + MORPHEME_BOUNDARY
      case 'root':
        return ROOT_TEMPLATE.format(self.form)
      case 'suffix':
        return MORPHEME_BOUNDARY + self.form
