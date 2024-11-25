from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union
from xml.etree.ElementTree import ParseError
from swarm import Swarm, Agent  # type: ignore[import]
from swarm.repl.repl import (  # type: ignore[import]
    process_and_print_streaming_response,
)
from token_world.llm.form_filling.form_filler import FilledElement, FormFiller, FormFillingException
from token_world.llm.message_tree import MessageTreeTraversal

Message = Dict[str, Any]
AgentResponse = Any
FormFillingExceptions = Union[ParseError, FormFillingException]

RunInference = Callable[[List[Message]], AgentResponse]
GetFeedback = Callable[[FormFiller, FormFillingExceptions, AgentResponse], Message]


def swarm_inference_fn(
    client: Swarm, agent: Agent, messages: List[Message], stream: bool = True
) -> AgentResponse:
    response = client.run(agent=agent, messages=messages, stream=stream)
    print(flush=True)
    if stream:
        response = process_and_print_streaming_response(response)
    else:
        print(response)
    print(flush=True)
    return response


def get_default_feedback_message(
    form_filler: FormFiller, e: FormFillingExceptions, _: AgentResponse
) -> Message:
    reminder_feedback = f"""Here is the form template again:
{form_filler.template_text}

An example of a compliant response is:
{form_filler.get_hint_filled_form()}"""

    if isinstance(e, ParseError):
        feedback_text = f"""Error filling form: {e}
**The filled form is not valid XML.**"""

    elif isinstance(e, FormFillingException):
        feedback_text = f"""Error filling form: {e}
**The filled form is valid XML but does not match the template.**"""

    else:
        feedback_text = f"Error filling form: {e}"

    return {
        "role": "system",
        "sender": "System",
        "message": f"""{feedback_text}

{reminder_feedback}""",
    }


class FilledForm(NamedTuple):
    form_data: FilledElement
    successful_response: AgentResponse


def fill_form(
    run_inference: RunInference,
    traversal: MessageTreeTraversal[Message],
    form_filler: FormFiller,
    form_fill_retry_limit: int,
    get_feedback_message: GetFeedback = get_default_feedback_message,
    keep_only_succcessful_attempt: bool = True,
) -> FilledForm:
    feedback: Optional[Message] = None
    starting_node = traversal.node
    for _ in range(form_fill_retry_limit):
        try:
            response = run_inference(traversal.node.get_message_chain())
            filled_form = _attempt_form_filling(response, traversal, form_filler)
            if keep_only_succcessful_attempt:
                traversal.go_to_ancestor(starting_node).go_to_new_descendant(
                    filled_form.successful_response.messages
                )
            return filled_form

        except ParseError as e:
            # Provide feedback to the agent on the error
            feedback = get_feedback_message(form_filler, e, response)
            traversal.go_to_new_child(feedback)

        except FormFillingException as e:
            # Provide feedback to the agent on the error
            feedback = get_feedback_message(form_filler, e, response)
            traversal.go_to_new_child(feedback)

    raise FormFillingException(
        "Failed to fill the form after multiple attempts. "
        f"Last feedback: {feedback and feedback['message']}"
    )


def _attempt_form_filling(
    response: AgentResponse,
    traversal: MessageTreeTraversal[Message],
    form_filler: FormFiller,
) -> FilledForm:
    traversal.go_to_new_descendant(response.messages)

    # Attempt to parse the filled form
    return FilledForm(form_filler.parse(traversal.get_current_message()["content"]), response)
