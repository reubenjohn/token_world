from typing import List, Set, Type
import xml.etree.ElementTree as ET

from token_world.llm.form_filling.template import (
    Template,
    TextTemplate,
    ArrayTemplate,
    DictionaryTemplate,
)


class InvalidTemplateException(Exception):
    pass


class Breadcrumbs:
    def __init__(self, breadcrumbs: List[str] = []):
        self.breadcrumbs = breadcrumbs

    # / operator
    def __truediv__(self, other: str) -> "Breadcrumbs":
        return Breadcrumbs(self.breadcrumbs + [other])

    def __str__(self) -> str:
        return "/".join(self.breadcrumbs)

    def __repr__(self) -> str:
        return f"Breadcrumbs({self.breadcrumbs})"


def parse_template(template: str) -> Template:
    template_tree = ET.ElementTree(ET.fromstring(template))
    template_root = template_tree.getroot()
    if template_root.tag != "FORM":
        raise InvalidTemplateException("Root tag must be <FORM>")

    return _parse_template_element(template_root, Breadcrumbs())


def _parse_template_element(element: ET.Element, breadcrumbs: Breadcrumbs) -> Template:
    breadcrumbs = breadcrumbs / element.tag
    if len(element) == 0:
        return _parse_text_template(element, breadcrumbs)
    elif _parse_boolean_attribute(element, "isArray", breadcrumbs):
        return _parse_template_array(element, breadcrumbs)
    return _parse_template_dictionary(element, breadcrumbs)


def _parse_text_template(element: ET.Element, breadcrumbs: Breadcrumbs) -> TextTemplate:
    _validate_legal_attributes(TextTemplate, element, {"minWordCount", "maxWordCount"}, breadcrumbs)
    return TextTemplate(
        name=element.tag,
        hint=_parse_template_element_hint(element, breadcrumbs),
        min_word_count=_parse_integer_attribute(element, "minWordCount", breadcrumbs),
        max_word_count=_parse_integer_attribute(
            element, "maxWordCount", default="100000", breadcrumbs=breadcrumbs
        ),
    )


def _parse_template_array(element: ET.Element, breadcrumbs: Breadcrumbs) -> ArrayTemplate:
    _validate_legal_attributes(ArrayTemplate, element, {"isArray"}, breadcrumbs)
    if len(element) == 0:
        raise InvalidTemplateException(
            f"ArrayTemplate '{breadcrumbs}': Must have at least one child. "
            f"Found {len(element)}."
        )

    representative_child = element[0]
    for idx, child in enumerate(element[1:], start=1):
        if child.tag != representative_child.tag or child.attrib != representative_child.attrib:
            raise InvalidTemplateException(
                f"ArrayTemplate '{breadcrumbs}': All children "
                "must have the same attributes and tags. "
                f"Representative is '{representative_child.tag}={representative_child.attrib}'; "
                f"Found '{child.tag}={child.attrib}' at index {idx}."
            )

    return ArrayTemplate(
        name=element.tag,
        hint=_parse_template_element_hint(element, breadcrumbs),
        child_template=_parse_template_element(representative_child, breadcrumbs),
    )


def _parse_template_dictionary(element: ET.Element, breadcrumbs: Breadcrumbs) -> DictionaryTemplate:
    _validate_legal_attributes(DictionaryTemplate, element, set(), breadcrumbs)
    if len(element) == 0:
        raise InvalidTemplateException(
            f"DictionaryTemplate '{breadcrumbs}': "
            f"Must have at least 1 child. Found {len(element)}."
        )

    return DictionaryTemplate(
        name=element.tag,
        hint=_parse_template_element_hint(element, breadcrumbs),
        children={child.tag: _parse_template_element(child, breadcrumbs) for child in element},
    )


def _parse_template_element_hint(element: ET.Element, breadcrumbs: Breadcrumbs) -> str:
    if element.text is None or not (hint := element.text.strip()):
        raise InvalidTemplateException(f"Element '{breadcrumbs}': Must have text representing hint")
    return hint


def _parse_boolean_attribute(
    element: ET.Element, attribute: str, breadcrumbs: Breadcrumbs, default="false"
) -> bool:
    is_array = element.attrib.get(attribute, default)
    if is_array not in ["true", "false"]:
        raise InvalidTemplateException(
            f"Element '{breadcrumbs}': '{attribute}' attribute must be 'true' or 'false'. "
            f"Found {is_array}"
        )
    return is_array == "true"


def _parse_integer_attribute(
    element: ET.Element, attribute: str, breadcrumbs: Breadcrumbs, default="0"
) -> int:
    value = element.attrib.get(attribute, default)
    if not value.isdigit():
        raise InvalidTemplateException(
            f"Element '{breadcrumbs}': '{attribute}' attribute must be an integer. Found {value}"
        )
    return int(value)


def _validate_legal_attributes(
    template_class: Type, element: ET.Element, legal_attributes: Set[str], breadcrumbs: Breadcrumbs
):
    illegal_attributes = set(element.attrib.keys()).difference(legal_attributes)
    if illegal_attributes != set():
        raise InvalidTemplateException(
            f"Element '{breadcrumbs}': Attributes {illegal_attributes} are illegal for "
            f"{template_class.__name__} '{element.tag}'"
        )
