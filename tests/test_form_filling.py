import pytest

from token_world.llm.form_filling.form_filler import FormFiller, FormFillingException


def test_form_filler_with_valid_text_template():
    template = """
    <FORM>
        Form hint goes here...
        <TEXT minWordCount="5" maxWordCount="10">Sample hint</TEXT>
    </FORM>
    """
    xml_input = """
    <FORM>
        Form hint goes here...
        <TEXT>Sample text</TEXT>
    </FORM>
    """
    form_filler = FormFiller(template)
    result = form_filler.parse(xml_input)
    assert result == {"TEXT": "Sample text"}


def test_form_filler_with_invalid_root_tag():
    template = """
    <FORM>
        Form hint goes here...
        <TEXT minWordCount="5" maxWordCount="10">Sample hint</TEXT>
    </FORM>
    """
    xml_input = """
    <INVALID>
        <TEXT>Sample text</TEXT>
    </INVALID>
    """
    form_filler = FormFiller(template)
    with pytest.raises(
        FormFillingException, match="DictionaryTemplate 'FORM': expected but found 'INVALID'"
    ):
        form_filler.parse(xml_input)


def test_form_filler_with_missing_text():
    template = """
    <FORM>
        Form hint goes here...
        <TEXT minWordCount="5" maxWordCount="10">Sample hint</TEXT>
    </FORM>
    """
    xml_input = """
    <FORM>
        Form hint goes here...
        <TEXT></TEXT>
    </FORM>
    """
    form_filler = FormFiller(template)
    with pytest.raises(
        FormFillingException, match="TextTemplate 'FORM/TEXT': Element 'TEXT' must have text"
    ):
        form_filler.parse(xml_input)


def test_form_filler_with_array_template():
    template = """
    <FORM>
        Form hint goes here...
        <ARRAY isArray="true">
            Array hint goes here...
            <TEXT>Array hint</TEXT>
        </ARRAY>
    </FORM>
    """
    xml_input = """
    <FORM>
        Form hint goes here...
        <ARRAY>
            <TEXT>Item 1</TEXT>
            <TEXT>Item 2</TEXT>
        </ARRAY>
    </FORM>
    """
    form_filler = FormFiller(template)
    result = form_filler.parse(xml_input)
    assert result == {"ARRAY": ["Item 1", "Item 2"]}


def test_form_filler_with_dictionary_template():
    template = """
    <FORM>
        Form hint goes here...
        <DICTIONARY>
            Dictionary hint goes here...
            <FIRST-NAME minWordCount="1" maxWordCount="1">Dictionary hint</FIRST-NAME>
            <LAST-NAME minWordCount="1" maxWordCount="2">Child hint</LAST-NAME>
        </DICTIONARY>
    </FORM>
    """
    xml_input = """
    <FORM>
        Form hint goes here...
        <DICTIONARY>
            <FIRST-NAME>John</FIRST-NAME>
            <LAST-NAME>Doe</LAST-NAME>
        </DICTIONARY>
    </FORM>
    """
    form_filler = FormFiller(template)
    result = form_filler.parse(xml_input)
    assert result == {"DICTIONARY": {"FIRST-NAME": "John", "LAST-NAME": "Doe"}}


def test_form_filler_with_unexpected_child():
    template = """
    <FORM>
        Form hint goes here...
        <DICTIONARY>
            Dictionary hint goes here...
            <FIRST-NAME minWordCount="1" maxWordCount="1">Dictionary hint</FIRST-NAME>
            <LAST-NAME minWordCount="1" maxWordCount="2">Child hint</LAST-NAME>
        </DICTIONARY>
    </FORM>
    """
    xml_input = """
    <FORM>
        Form hint goes here...
        <DICTIONARY>
            <FIRST-NAME>John</FIRST-NAME>
            <LAST-NAME>Doe</LAST-NAME>
            <AGE>30</AGE>
        </DICTIONARY>
    </FORM>
    """
    form_filler = FormFiller(template)
    with pytest.raises(
        FormFillingException,
        match="DictionaryTemplate 'FORM/DICTIONARY': Found unexpected children {'AGE'}",
    ):
        form_filler.parse(xml_input)


def test_form_filler_with_missing_child():
    template = """
    <FORM>
        Form hint goes here...
        <DICTIONARY>
            Dictionary hint goes here...
            <FIRST-NAME minWordCount="1" maxWordCount="1">Dictionary hint</FIRST-NAME>
            <LAST-NAME minWordCount="1" maxWordCount="2">Child hint</LAST-NAME>
        </DICTIONARY>
    </FORM>
    """
    xml_input = """
    <FORM>
        Form hint goes here...
        <DICTIONARY>
            <FIRST-NAME>John</FIRST-NAME>
        </DICTIONARY>
    </FORM>
    """
    form_filler = FormFiller(template)
    with pytest.raises(
        FormFillingException,
        match="DictionaryTemplate 'FORM/DICTIONARY': Missing children {'LAST-NAME'}",
    ):
        form_filler.parse(xml_input)
