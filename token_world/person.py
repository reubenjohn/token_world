from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import json
import logging

from swarm import Swarm, Agent  # type: ignore[import]
from swarm.repl.repl import (  # type: ignore[import]
    process_and_print_streaming_response,
)


from time import sleep
from typing import Dict, Iterator, List, Optional

from token_world.entity import Entity, physical_entity, EntityId
from token_world.environment import Environment


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


def person_entity(
    name: str, id: Optional[str] = None, x: float = 0.0, y: float = 0.0, z: float = 0.0, **kwargs
) -> Entity:
    return physical_entity(name, id, is_person=True, x=x, y=y, z=z, **kwargs)


class PersonHandler:
    def __init__(self, entity: Entity):
        self._entity = entity
        self.agent = Agent(
            name="Worldly Person",
            model="llama3.1:8b",
            tool_choice="required",
            instructions="""
Interact with your environment
            """,
        )

        # code_classifier_agent.functions.append(file_contains_code)
        # code_register_agent.functions.append(register_element)

        self.messages: List[dict] = []

    def act(self, client: Swarm):
        logging.info(f"🤔 Person {self._entity.id} is acting 🤔")
        while True:
            response = client.run(agent=self.agent, messages=self.messages, stream=True)

            print(flush=True)
            response = process_and_print_streaming_response(response)
            print(flush=True)

            if (
                len(response.messages) == 0
                or "content" not in response.messages[-1]
                or response.messages[-1]["content"] == ""
            ):
                self.messages.extend(response.messages)
                feedback = {
                    "role": "system",
                    "sender": "System",
                    "content": "You must produce an output response. Please try again.",
                }
                pretty_print_messages([feedback])
                self.messages.append(feedback)
                logging.info(f"❌ Failed to generate response {response=} ❌")
                continue
            break
        self.messages.extend(response.messages)
        logging.info(f"✅ Person {self._entity.id} has acted ✅")


class PeopleManager:
    def __init__(self, client: Swarm, environment: Environment):
        self._person_handlers: Dict[EntityId, PersonHandler] = {}
        self._is_running = False
        self._client = client
        self._environment = environment

    @staticmethod
    def is_person(entity: Entity) -> bool:
        return entity.properties.get("is_person", False)

    def add_entity(self, entity: Entity):
        self._person_handlers[entity.id] = PersonHandler(entity)

    def act(self):
        for handler in self._person_handlers.values():
            handler.act(self._client)
            self._environment.react(handler.messages)

    def start_person_loop(self):
        self._is_running = True
        while self._is_running:
            try:
                self.act()
            except Exception as e:
                logging.error(f"Error in person loop: {e}", exc_info=True)
            sleep(1)

    def stop_person_loop(self):
        logging.info("Stopping person loop requested")
        self._is_running = False


@contextmanager
def people_manager_executor(client: Swarm, environment: Environment) -> Iterator[PeopleManager]:
    with ThreadPoolExecutor(max_workers=1) as executor:
        people_manager = PeopleManager(client, environment)
        executor.submit(people_manager.start_person_loop)
        yield people_manager
        people_manager.stop_person_loop()
