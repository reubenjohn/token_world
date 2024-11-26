from token_world.llm.form_filling.template import (
    TextTemplate,
    DictionaryTemplate,
    ArrayTemplate,
)


def test_get_hint_filled_form_with_text_template():
    template = TextTemplate(name="TEXT", hint="Sample hint", min_word_count=5, max_word_count=10)
    result = template.get_hint_filled_form()
    assert result == """<TEXT>\n  Sample hint (5-10 words)\n</TEXT>"""


def test_get_hint_filled_form_with_text_template_no_limits():
    template = TextTemplate(name="TEXT", hint="Sample hint")
    result = template.get_hint_filled_form()
    assert result == """<TEXT>\n  Sample hint\n</TEXT>"""


def test_get_hint_filled_form_with_dictionary_template():
    template = DictionaryTemplate(
        name="FORM",
        hint="Form hint",
        children={
            "TEXT": TextTemplate(
                name="TEXT", hint="Sample hint", min_word_count=5, max_word_count=10
            )
        },
    )
    result = template.get_hint_filled_form()
    assert (
        result
        == """<FORM>
  Form hint
  <TEXT>
    Sample hint (5-10 words)
  </TEXT>
</FORM>"""
    )


def test_get_hint_filled_form_with_array_template():
    template = ArrayTemplate(
        name="ARRAY",
        hint="Array hint",
        child_template=TextTemplate(name="TEXT", hint="Sample hint", min_word_count=5),
    )
    result = template.get_hint_filled_form()
    assert (
        result
        == """<ARRAY>
  Array hint
  <TEXT>
    Sample hint (at least 5 words)
  </TEXT>
</ARRAY>"""
    )


def test_get_hint_filled_form_with_complex_template():
    template = DictionaryTemplate(
        name="COMPLEX_FORM",
        hint="Complex form hint",
        children={
            "TEXT": TextTemplate(name="TEXT", hint="Sample hint", max_word_count=10),
            "NESTED_FORM": DictionaryTemplate(
                name="NESTED_FORM",
                hint="Nested form hint",
                children={
                    "NESTED_TEXT": TextTemplate(
                        name="NESTED_TEXT",
                        hint="Nested sample hint",
                        min_word_count=3,
                        max_word_count=8,
                    ),
                    "NESTED_ARRAY": ArrayTemplate(
                        name="NESTED_ARRAY",
                        hint="Nested array hint",
                        child_template=TextTemplate(
                            name="ARRAY_TEXT",
                            hint="Array sample hint",
                            min_word_count=2,
                            max_word_count=5,
                        ),
                    ),
                },
            ),
        },
    )
    result = template.get_hint_filled_form()
    assert (
        result
        == """<COMPLEX_FORM>
  Complex form hint
  <TEXT>
    Sample hint (at most 10 words)
  </TEXT>
  <NESTED_FORM>
    Nested form hint
    <NESTED_TEXT>
      Nested sample hint (3-8 words)
    </NESTED_TEXT>
    <NESTED_ARRAY>
      Nested array hint
      <ARRAY_TEXT>
        Array sample hint (2-5 words)
      </ARRAY_TEXT>
    </NESTED_ARRAY>
  </NESTED_FORM>
</COMPLEX_FORM>"""
    )
