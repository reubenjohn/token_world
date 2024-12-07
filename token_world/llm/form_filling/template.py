from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, Union
from typing_extensions import override

Template = Union["TextTemplate", "DictionaryTemplate", "ArrayTemplate"]


@dataclass
class BaseTemplate(ABC):
    name: str
    hint: str

    @abstractmethod
    def get_hint_filled_form(self, indents: str = "") -> str:
        pass  # pragma: no cover


def _get_container_hint_filled_form(
    template: Template, children: Iterable[Template], indents: str
) -> str:
    entries = "\n".join(f"{child.get_hint_filled_form(indents+'  ')}" for child in children)
    return f"""{indents}<{template.name}>
{indents}  {template.hint}
{entries}
{indents}</{template.name}>"""


@dataclass
class TextTemplate(BaseTemplate):
    MAX_WORD_COUNT = 100000

    min_word_count: int = 0
    max_word_count: int = MAX_WORD_COUNT

    @property
    def has_min_word_count(self):
        return self.min_word_count != 0

    @property
    def has_max_word_count(self):
        return self.max_word_count != self.MAX_WORD_COUNT

    @override
    def get_hint_filled_form(self, indents: str = "") -> str:

        return f"""{indents}<{self.name}>
{indents}  {self.hint}{self._get_word_limit_hint()}
{indents}</{self.name}>"""

    def _get_word_limit_hint(self) -> str:
        if not self.has_min_word_count and not self.has_max_word_count:
            return ""
        elif self.has_min_word_count and not self.has_max_word_count:
            return f" (at least {self.min_word_count} words)"
        elif not self.has_min_word_count and self.has_max_word_count:
            return f" (at most {self.max_word_count} words)"
        return f" ({self.min_word_count}-{self.max_word_count} words)"


@dataclass
class DictionaryTemplate(BaseTemplate):
    children: Dict[str, Template]

    @override
    def get_hint_filled_form(self, indents: str = "") -> str:
        return _get_container_hint_filled_form(self, self.children.values(), indents)


@dataclass
class ArrayTemplate(BaseTemplate):
    child_template: Template

    @override
    def get_hint_filled_form(self, indents: str = "") -> str:
        return _get_container_hint_filled_form(self, [self.child_template], indents)
