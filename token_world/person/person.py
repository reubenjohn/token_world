from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import lru_cache
import logging

from swarm import Swarm, Agent  # type: ignore[import]

from time import sleep
from typing import Dict, Iterator, Optional

from token_world.entity import Entity, physical_entity, EntityId
from token_world.environment import Environment
from token_world.llm.form_filling.agentic import SwarmRunInference, fill_form
from token_world.llm.form_filling.template import Template
from token_world.llm.form_filling.form_filler import FormFiller
from token_world.llm.form_filling.template_parser import parse_template
from token_world.llm.llm import Message
from token_world.llm.message_tree import MessageTreeTraversal


def person_entity(
    name: str, id: Optional[str] = None, x: float = 0.0, y: float = 0.0, z: float = 0.0, **kwargs
) -> Entity:
    return physical_entity(name, id, is_person=True, x=x, y=y, z=z, **kwargs)


@lru_cache
def get_person_action_form() -> str:
    with open("token_world/person/PersonActionForm.xml") as f:
        return f.read()


@lru_cache
def get_person_action_form_template() -> Template:
    return parse_template(get_person_action_form())


@lru_cache
def get_person_action_form_filler() -> FormFiller:
    return FormFiller(get_person_action_form())


PERSON_INSTRUCTIONS = f"""
You are a highly intelligent and autonomous agent living in an open world.
Your primary objective is to interact with the world around you, learn from these interactions,
 and evolve your goals over time.
As you interact with the environment and other entities, continuously reassess and refine your
 goals to adapt to new information and changing circumstances.
Think step by step and always consider the long-term implications of your actions.
Document your thought process and decisions to help improve your future interactions.
Initially, you may have a limited understanding of your environment, so stick to simple actions,
 you may use more sophisticated actions as you learn what actions are valid in the environment.

After you have produced a detailed rundown of your thought process,
 produce our output in the form of a form with the following structure:

{get_person_action_form()}

An example of a compliant response that you can output is:
{get_person_action_form_filler().get_hint_filled_form()}
"""


class PersonHandler:
    def __init__(self, entity: Entity):
        self._entity = entity
        self.agent = Agent(
            name=entity.name,
            model="llama3.1:8b",
            # tool_choice="required",
            instructions=PERSON_INSTRUCTIONS,
        )

        # code_classifier_agent.functions.append(file_contains_code)
        # code_register_agent.functions.append(register_element)

        self.message_traversal = MessageTreeTraversal[Message].new()
        self._reaction_filler = get_person_action_form_filler()

    def act(self, client: Swarm) -> str:
        logging.info(f"🤔 Agent {self._entity.id} is acting 🤔")

        run_inference = SwarmRunInference(client, self.agent, stream=True)
        filled_form = fill_form(
            run_inference,
            self.message_traversal,
            self._reaction_filler,
            3,
        )
        logging.info(f"✅ Agent {self._entity.id} has acted ✅")
        form_data: dict = filled_form.form_data
        return form_data["ACTION"]

        # while True:

        # print(flush=True)
        # response = process_and_print_streaming_response(response)
        # print(flush=True)

        # if (
        #     len(response.messages) == 0
        #     or "content" not in response.messages[-1]
        #     or response.messages[-1]["content"] == ""
        # ):
        #     self.messages.extend(response.messages)
        #     feedback = {
        #         "role": "system",
        #         "sender": "System",
        #         "content": "You must produce an output response. Please try again.",
        #     }
        #     pretty_print_messages([feedback])
        #     self.messages.append(feedback)
        #     logging.info(f"❌ Failed to generate response {response=} ❌")
        #     continue
        #     break
        # self.messages.extend(response.messages)


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
