import pytest
from dataclasses import dataclass
from typing import List, Dict, Any
from xml.etree.ElementTree import ParseError


from token_world.llm.form_filling.form_filler import FormFiller, FormFillingException
from token_world.llm.message_tree import MessageTreeTraversal
from token_world.llm.form_filling.agentic import (
    extract_form_content,
    get_default_feedback_message,
    fill_form,
    Message,
)


@dataclass
class MockAgentResponse:
    messages: List[Message]


@pytest.fixture
def simple_form_filler():
    return FormFiller(
        template_text="""
<FORM>
    Form hint goes here...
    <TEXT minWordCount="5" maxWordCount="10">Sample hint</TEXT>
</FORM>
    """
    )


@pytest.fixture
def simple_reminder():
    return """An example of a compliant response is:
<FORM>
  Form hint goes here...
  <TEXT>
    Sample hint (5-10 words)
  </TEXT>
</FORM>"""


def test_get_default_feedback_message_parse_error(simple_form_filler, simple_reminder):
    exception = ParseError("Test exception")
    agent_response = None  # AgentResponse is not used in the default implementation

    expected_message = {
        "role": "system",
        "sender": "System",
        "content": f"""Error filling form: {exception}
**The filled form is not valid XML.**

{simple_reminder}""",
    }

    feedback_message = get_default_feedback_message(simple_form_filler, exception, agent_response)
    assert feedback_message["role"] == expected_message["role"]
    assert feedback_message["sender"] == expected_message["sender"]
    assert feedback_message["content"] == expected_message["content"]
    assert feedback_message == expected_message


def test_get_default_feedback_message_form_filling_exception(simple_form_filler, simple_reminder):
    exception = FormFillingException("Test exception")
    agent_response = None  # AgentResponse is not used in the default implementation

    expected_message = {
        "role": "system",
        "sender": "System",
        "content": f"""Error filling form: {exception}
**The filled form is valid XML but does not match the template.**

{simple_reminder}""",
    }

    feedback_message = get_default_feedback_message(simple_form_filler, exception, agent_response)
    assert feedback_message["role"] == expected_message["role"]
    assert feedback_message["sender"] == expected_message["sender"]
    assert feedback_message["content"] == expected_message["content"]
    assert feedback_message == expected_message


def test_extract_form_content_valid():
    content = """<FORM>
        <TEXT>Sample content</TEXT>
    </FORM>"""
    text = f"""
    Some text before
    {content}
    Some text after
    """
    assert extract_form_content(text) == content


def test_extract_form_content_missing_opening_tag():
    text = """
    Some text before
    <TEXT>Sample content</TEXT>
    </FORM>
    Some text after
    """
    with pytest.raises(ValueError, match="<FORM> tag not found in text"):
        extract_form_content(text)


def test_extract_form_content_missing_closing_tag():
    text = """
    Some text before
    <FORM>
        <TEXT>Sample content</TEXT>
    Some text after
    """
    with pytest.raises(ValueError, match="</FORM> tag not found in text"):
        extract_form_content(text)


def test_extract_form_content_nested_form():
    content = """<FORM>
        <TEXT>Sample content</TEXT>
        <FORM>
            <TEXT>Nested content</TEXT>
        </FORM>
    </FORM>"""
    text = f"""
    Some text before
    {content}
    Some text after
    """
    assert extract_form_content(text) == content


def test_fill_form_success(simple_form_filler):
    def mock_run_inference(messages: List[Message]) -> MockAgentResponse:
        return MockAgentResponse([{"content": "<FORM><TEXT>Filled content</TEXT></FORM>"}])

    traversal = MessageTreeTraversal.new()

    filled_form = fill_form(
        run_inference=mock_run_inference,
        traversal=traversal,
        form_filler=simple_form_filler,
        form_fill_retry_limit=3,
    )

    assert filled_form.form_data == {"TEXT": "Filled content"}
    assert filled_form.successful_response == MockAgentResponse(
        [{"content": "<FORM><TEXT>Filled content</TEXT></FORM>"}]
    )


def test_fill_form_inference_error(simple_form_filler):
    def mock_run_inference(messages: List[Dict[str, Any]]) -> MockAgentResponse:
        raise RuntimeError("Inference exception")

    traversal = MessageTreeTraversal.new()

    with pytest.raises(RuntimeError, match="Inference exception"):
        fill_form(
            run_inference=mock_run_inference,
            traversal=traversal,
            form_filler=simple_form_filler,
            form_fill_retry_limit=3,
        )


def test_fill_form_invalid_xml(simple_form_filler):
    def mock_run_inference(messages: List[Dict[str, Any]]) -> MockAgentResponse:
        return MockAgentResponse(
            [
                {
                    "content": """<FORM>
    Form hint...
    <TEXT1 minWordCount='5' maxWordCount='10'>Sample hint</TEXT>
</FORM>"""
                }
            ]
        )

    traversal = MessageTreeTraversal.new()

    with pytest.raises(
        FormFillingException,
        match="Failed to fill the form after multiple attempts. "
        "Last feedback:.*mismatched tag: line 3, column 59\n.*is not valid XML",
    ):
        fill_form(
            run_inference=mock_run_inference,
            traversal=traversal,
            form_filler=simple_form_filler,
            form_fill_retry_limit=3,
        )


def test_fill_form_invalid_template(simple_form_filler):
    def mock_run_inference(messages: List[Dict[str, Any]]) -> MockAgentResponse:
        return MockAgentResponse([{"content": "<FORM><TEXT1>Invalid content</TEXT1></FORM>"}])

    traversal = MessageTreeTraversal.new()

    with pytest.raises(
        FormFillingException,
        match="Failed to fill the form after multiple attempts. "
        "Last feedback:.*unexpected children {'TEXT1'}.*\n"
        ".*valid XML but does not match the template",
    ):
        fill_form(
            run_inference=mock_run_inference,
            traversal=traversal,
            form_filler=simple_form_filler,
            form_fill_retry_limit=3,
        )


def test_fill_form_retry_attempts(simple_form_filler):
    def mock_run_inference(messages: List[Message]) -> MockAgentResponse:
        if len(messages) == 0:
            return MockAgentResponse([{"content": "<FORM>First attempt</FORM>"}])
        else:
            return MockAgentResponse([{"content": "<FORM><TEXT>Second attempt</TEXT></FORM>"}])

    traversal = MessageTreeTraversal.new()

    with pytest.raises(
        FormFillingException,
        match="Failed to fill the form after multiple attempts.",
    ):
        fill_form(
            run_inference=mock_run_inference,
            traversal=traversal,
            form_filler=simple_form_filler,
            form_fill_retry_limit=1,
            keep_only_succcessful_attempt=False,
        )

    traversal = MessageTreeTraversal.new()

    filled_form = fill_form(
        run_inference=mock_run_inference,
        traversal=traversal,
        form_filler=simple_form_filler,
        form_fill_retry_limit=2,
        keep_only_succcessful_attempt=True,
    )

    assert filled_form.form_data == {"TEXT": "Second attempt"}
    assert filled_form.successful_response == MockAgentResponse(
        [{"content": "<FORM><TEXT>Second attempt</TEXT></FORM>"}]
    )

    # Ensure that both attempts are in the tree
    assert traversal.node.message["content"] == "<FORM><TEXT>Second attempt</TEXT></FORM>"
    assert len(traversal.go_to_root().node.children) == 2
    assert traversal.node.children[0].message["content"] == "<FORM>First attempt</FORM>"
    assert (
        traversal.node.children[1].message["content"] == "<FORM><TEXT>Second attempt</TEXT></FORM>"
    )

    traversal = MessageTreeTraversal.new()
    filled_form = fill_form(
        run_inference=mock_run_inference,
        traversal=traversal,
        form_filler=simple_form_filler,
        form_fill_retry_limit=2,
        keep_only_succcessful_attempt=False,
    )

    assert filled_form.form_data == {"TEXT": "Second attempt"}
    assert filled_form.successful_response == MockAgentResponse(
        [{"content": "<FORM><TEXT>Second attempt</TEXT></FORM>"}]
    )

    # Ensure that both attempts are in the tree
    assert traversal.node.message["content"] == "<FORM><TEXT>Second attempt</TEXT></FORM>"
    assert len(traversal.go_to_root().node.children) == 1
    assert traversal.node.children[0].message["content"] == "<FORM>First attempt</FORM>"
