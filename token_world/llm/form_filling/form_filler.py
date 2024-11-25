from typing import Dict, List, Optional, Union
import xml.etree.ElementTree as ET

from token_world.llm.form_filling.template import (
    Template,
    TextTemplate,
    ArrayTemplate,
    DictionaryTemplate,
)
from token_world.llm.form_filling.template_parser import Breadcrumbs, parse_template

FilledElement = Union[str, "FilledArray", "FilledDictionary"]
FilledText = str
FilledArray = List[FilledElement]
FilledDictionary = Dict[str, FilledElement]


class FormFillingException(Exception):
    pass


class FormFiller:
    def __init__(self, template: str):
        self._template = parse_template(template)

    def parse(self, xml_input: str) -> FilledElement:
        xml_tree = ET.ElementTree(ET.fromstring(xml_input))
        return self._parse_element(self._template, xml_tree.getroot(), Breadcrumbs())

    def _parse_element(
        self,
        template: Template,
        element: ET.Element,
        breadcrumbs: Breadcrumbs,
        array_index: Optional[int] = None,
    ) -> FilledElement:
        breadcrumbs = breadcrumbs / (
            f"{template.name}[{array_index}]" if array_index is not None else template.name
        )
        if template.name != element.tag:
            raise FormFillingException(
                f"{type(template).__name__} '{breadcrumbs}': expected but found '{element.tag}'"
            )
        if element.attrib != {}:
            raise FormFillingException(f"Element '{element.tag}' must not have attributes")
        if isinstance(template, TextTemplate):
            return self._parse_text_template(template, element, breadcrumbs)
        elif isinstance(template, ArrayTemplate):
            return self._parse_array_template(template, element, breadcrumbs)
        return self._parse_dictionary_template(template, element, breadcrumbs)

    def _parse_text_template(
        self, template: TextTemplate, element: ET.Element, breadcrumbs: Breadcrumbs
    ) -> FilledText:
        if len(element) != 0:
            raise FormFillingException(
                f"TextTemplate '{breadcrumbs}': Element '{element.tag}' must not have children"
            )
        if element.text is None:
            raise FormFillingException(
                f"TextTemplate '{breadcrumbs}': Element '{element.tag}' must have text"
            )
        return element.text.strip()

    def _parse_array_template(
        self, template: ArrayTemplate, element: ET.Element, breadcrumbs: Breadcrumbs
    ) -> FilledArray:
        if len(element) == 0:
            raise FormFillingException(
                f"ArrayTemplate '{breadcrumbs}': Element '{element.tag}' must have children"
            )
        return [
            self._parse_element(template.child_template, child, breadcrumbs, array_index=idx)
            for idx, child in enumerate(element)
        ]

    def _parse_dictionary_template(
        self, template: DictionaryTemplate, element: ET.Element, breadcrumbs: Breadcrumbs
    ) -> FilledDictionary:
        expected_tags = set(template.children.keys())
        actual_tags = {child.tag for child in element}
        if unexpected_tags := actual_tags.difference(expected_tags):
            raise FormFillingException(
                f"DictionaryTemplate '{breadcrumbs}': Found unexpected children {unexpected_tags}"
            )
        if missing_tags := expected_tags.difference(actual_tags):
            raise FormFillingException(
                f"DictionaryTemplate '{breadcrumbs}': Missing children {missing_tags}"
            )
        return {
            child.tag: self._parse_element(template.children[child.tag], child, breadcrumbs)
            for child in element
        }
