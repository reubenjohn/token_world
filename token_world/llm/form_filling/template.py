from dataclasses import dataclass
from typing import Dict, Union

Template = Union["TextTemplate", "DictionaryTemplate", "ArrayTemplate"]


@dataclass
class BaseTemplate:
    name: str
    hint: str


@dataclass
class TextTemplate(BaseTemplate):
    min_word_count: int
    max_word_count: int


@dataclass
class DictionaryTemplate(BaseTemplate):
    children: Dict[str, Template]


@dataclass
class ArrayTemplate(BaseTemplate):
    child_template: Template
