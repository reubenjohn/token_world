import pytest
from token_world.llm.form_filling.template import TextTemplate, ArrayTemplate, DictionaryTemplate
from token_world.llm.form_filling.template_parser import InvalidTemplateException, parse_template

import xml.etree.ElementTree as ET


def test_parse_template_with_syntactically_invalid_xml():
    xml_string = """
    <FORM>
        Form hint goes here...
        <TEXT minWordCount="5" maxWordCount="10">Sample hint</TEXT
    </FORM>
    """
    with pytest.raises(ET.ParseError):
        parse_template(xml_string)


def test_parse_template_with_valid_text_template():
    xml_string = """
    <FORM>
        Form hint goes here...
        <TEXT minWordCount="5" maxWordCount="10">Sample hint</TEXT>
    </FORM>
    """
    template = parse_template(xml_string)
    assert template == DictionaryTemplate(
        "FORM", "Form hint goes here...", {"TEXT": TextTemplate("TEXT", "Sample hint", 5, 10)}
    )


def test_parse_template_with_invalid_root_tag():
    xml_string = """
    <INVALID>
        <TEXT>Sample hint</TEXT>
    </INVALID>
    """
    with pytest.raises(InvalidTemplateException, match="Root tag must be <FORM>"):
        parse_template(xml_string)


def test_parse_template_with_root_missing_hint():
    xml_string = """
    <FORM>
        <TEXT minWordCount="5" maxWordCount="10">Sample hint</TEXT>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="Element 'FORM': Must have text representing hint",
    ):
        parse_template(xml_string)


def test_parse_template_with_text_missing_hint():
    xml_string = """
    <FORM>
        Form hint goes here...
        <TEXT minWordCount="5" maxWordCount="10"></TEXT>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="Element 'FORM/TEXT': Must have text representing hint",
    ):
        parse_template(xml_string)


def test_parse_template_with_array_template():
    xml_string = """
<FORM>
    Form hint goes here...
    <ARRAY isArray="true">
        Array hint goes here...
        <TEXT>Array hint</TEXT>
        <TEXT>Child hint</TEXT>
    </ARRAY>
</FORM>
    """
    template = parse_template(xml_string)
    assert (
        DictionaryTemplate(
            "FORM",
            "Form hint goes here...",
            {
                "ARRAY": ArrayTemplate(
                    "ARRAY",
                    "Array hint goes here...",
                    TextTemplate("TEXT", "Array hint", 0, 100000),
                )
            },
        )
        == template
    )


def test_parse_template_with_inconsistent_array_children():
    xml_string = """
    <FORM>
        Form hint goes here...
        <ARRAY isArray="true">
            <TEXT>Array hint</TEXT>
            <TEXT minWordCount="1" maxWordCount="5">Child hint</TEXT>
        </ARRAY>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="ArrayTemplate 'FORM/ARRAY': All children must have the same attributes and tags. "
        "Representative is 'TEXT={}'; "
        "Found 'TEXT={'minWordCount': '1', 'maxWordCount': '5'}' at index 1.",
    ):
        parse_template(xml_string)


def test_parse_template_with_invalid_boolean_attribute():
    xml_string = """
    <FORM>
        Form hint goes here...
        <PEOPLE isArray="invalid">
            People hint goes here...
            <TEXT>Person A</TEXT>
        </PEOPLE>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="'isArray' attribute must be 'true' or 'false'. Found invalid",
    ):
        parse_template(xml_string)


def test_parse_template_with_invalid_integer_attribute():
    xml_string = """
    <FORM>
        Form hint goes here...
        <TEXT minWordCount="invalid">Sample hint</TEXT>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="'minWordCount' attribute must be an integer. Found invalid",
    ):
        parse_template(xml_string)


def test_parse_template_with_dictionary_template():
    xml_string = """
    <FORM>
        Form hint goes here...
        <DICTIONARY>
            DICTIONARY hint goes here...
            <FIRST-NAME minWordCount="1" maxWordCount="1">Dictionary hint</FIRST-NAME>
            <LAST-NAME minWordCount="1" maxWordCount="2">Child hint</LAST-NAME>
        </DICTIONARY>
    </FORM>
    """
    template = parse_template(xml_string)
    assert (
        DictionaryTemplate(
            "FORM",
            "Form hint goes here...",
            {
                "DICTIONARY": DictionaryTemplate(
                    "DICTIONARY",
                    "DICTIONARY hint goes here...",
                    {
                        "FIRST-NAME": TextTemplate("FIRST-NAME", "Dictionary hint", 1, 1),
                        "LAST-NAME": TextTemplate("LAST-NAME", "Child hint", 1, 2),
                    },
                )
            },
        )
        == template
    )


def test_parse_template_with_empty_array():
    xml_string = """
    <FORM>
        Form hint goes here...
        <ARRAY isArray="true">
            Array hint
        </ARRAY>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="Attributes {'isArray'} are illegal for TextTemplate 'ARRAY'",
    ):
        parse_template(xml_string)


def test_parse_template_with_illegal_array_attributes():
    xml_string = """
    <FORM>
        Form hint goes here...
        <ARRAY isArray="true" illegalAttr="illegal">
            Array hint goes here...
            <TEXT>Array hint</TEXT>
        </ARRAY>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="Attributes {'illegalAttr'} are illegal for ArrayTemplate 'ARRAY'",
    ):
        parse_template(xml_string)


def test_parse_template_with_invalid_dictionary_attributes():
    xml_string = """
    <FORM>
        Form hint goes here...
        <DICTIONARY asd="1">
            Dictionary hint
            <FIELD-1>Field 1 hint</FIELD-1>
        </DICTIONARY>
    </FORM>
    """
    with pytest.raises(
        InvalidTemplateException,
        match="Attributes {'asd'} are illegal for DictionaryTemplate 'DICTIONARY'",
    ):
        parse_template(xml_string)
