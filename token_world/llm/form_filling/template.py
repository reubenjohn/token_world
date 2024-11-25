from dataclasses import dataclass
from typing import Dict, Iterable, Union

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


def _get_container_hint_filled_form(
    template: Template, children: Iterable[Template], indents: str
) -> str:
    entries = "\n".join(f"{get_hint_filled_form(child, indents+'  ')}" for child in children)
    return f"""{indents}<{template.name}>
{indents}  {template.hint}
{entries}
{indents}</{template.name}>"""


def get_hint_filled_form(template: Template, indents: str = "") -> str:
    if isinstance(template, TextTemplate):
        return f"{indents}<{template.name}>{template.hint}</{template.name}>"

    if isinstance(template, DictionaryTemplate):
        return _get_container_hint_filled_form(template, template.children.values(), indents)

    if isinstance(template, ArrayTemplate):
        return _get_container_hint_filled_form(template, [template.child_template], indents)
