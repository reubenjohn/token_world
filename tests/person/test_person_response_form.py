import pytest

from token_world.llm.form_filling.form_filler import FormFiller
from token_world.llm.form_filling.template import ArrayTemplate, DictionaryTemplate, TextTemplate
from token_world.llm.form_filling.template_parser import parse_template


@pytest.fixture
def form_template():
    with open("token_world/person/PersonActionForm.xml", "r") as f:
        form_template = f.read()
        return form_template


@pytest.fixture
def filled_action_form_text():
    return """<FORM>
    <THOUGHTS>
    I think I should go to the store and buy some milk.
    </THOUGHTS>

    <GOALS>
        <GOAL>Earn money</GOAL>
        <GOAL>Buy milk</GOAL>
    </GOALS>

    <ACTION>
    Go to the store
    </ACTION>
</FORM>"""


def test_form_structure(form_template):
    template = parse_template(form_template)
    assert template.children.keys() == {"THOUGHTS", "GOALS", "ACTION"}

    assert template.__class__ == DictionaryTemplate
    assert template.children["THOUGHTS"].__class__ == TextTemplate
    assert template.children["GOALS"].__class__ == ArrayTemplate
    assert template.children["GOALS"].child_template.name == "GOAL"
    assert template.children["GOALS"].child_template.__class__ == TextTemplate
    assert template.children["ACTION"].__class__ == TextTemplate


def test_form_filling(form_template, filled_action_form_text):
    filler = FormFiller(form_template)
    filled_element = filler.parse(filled_action_form_text)

    assert filled_element == {
        "THOUGHTS": "I think I should go to the store and buy some milk.",
        "GOALS": ["Earn money", "Buy milk"],
        "ACTION": "Go to the store",
    }
