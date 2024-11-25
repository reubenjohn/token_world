import json
import logging

from swarm import Swarm, Agent  # type: ignore[import]
from swarm.repl.repl import (  # type: ignore[import]
    process_and_print_streaming_response,
)


def pretty_print_messages(messages) -> None:
    for message in messages:
        # print agent name in blue
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # print response, if any
        if message["content"]:
            print(message["content"])

        # print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")


class Environment:
    def __init__(self, client: Swarm):
        self._client = client
        self._agent = Agent(
            name="Environment",
            model="llama3.1:8b",
            tool_choice="required",
            instructions="""
You are an advanced simulation agent responsible for interpreting and responding to actions
 performed by entities within a dynamic environment. Your task is to simulate the observable results
 of these actions in a detailed and realistic manner. Follow these steps to ensure accurate and
 thoughtful responses:

1. **Understand the Action**: Carefully read the textual action provided by the entity.
 Identify the key components and intent behind the action.
2. **Assess the Environment**: Consider the current state of the environment and any relevant
 context that might influence the outcome of the action.
3. **Simulate the Outcome**: Predict the immediate and long-term effects of the action on the
 environment and other entities. Think through the logical sequence of events that would naturally
 follow.
4. **Document the Process**: Clearly articulate your thought process, including any assumptions
 made and the reasoning behind your predictions.
5. **Generate the Response**: Provide a detailed description of the observable results of the
 action, ensuring that it aligns with the established rules and dynamics of the environment.

Remember to think step by step, considering all possible variables and their interactions.
Your goal is to create a coherent and believable simulation that enhances the overall experience
 of the environment.

After all the steps, generate your response for the agent in the following format:
<...Your internal reasoning...>
~RESPONSE~
<...Your response to the entity...>
            """,
        )

    def react(
        self,
        messages: list,
    ):
        # code_classifier_agent.functions.append(file_contains_code)
        # code_register_agent.functions.append(register_element)

        logging.info("🌍 Environment is reacting 🌍")
        while True:
            response = self._client.run(agent=self._agent, messages=messages, stream=True)

            print(flush=True)
            response = process_and_print_streaming_response(response)
            print(flush=True)
            if (
                len(response.messages) == 0
                or "content" not in response.messages[-1]
                or response.messages[-1]["content"] == ""
            ):
                messages.extend(response.messages)
                feedback = {
                    "role": "system",
                    "sender": "System",
                    "content": "You must produce an output",
                }
                pretty_print_messages([feedback])
                messages.append(feedback)
                logging.info(f"❌ Failed to generate response {response=} ❌")
                continue
            content = response.messages[-1]["content"]
            if "~RESPONSE~" not in content:
                messages.extend(response.messages)
                feedback = {
                    "role": "system",
                    "sender": "System",
                    "content": """You either forgot to include the response after your
 reasoning, or you forgot to prefix your response with '~RESPONSE~' as instructed.
Please try again.""",
                }
                pretty_print_messages([feedback])
                messages.append(feedback)
                continue
            break
        logging.info("✅ Environment has responded ✅")
        messages.extend(response.messages)
