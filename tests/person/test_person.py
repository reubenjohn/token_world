from dataclasses import dataclass
from typing import List
from unittest.mock import Mock
from swarm import Agent, Swarm  # type: ignore[import]
from tests.person.test_person_response_form import filled_action_form_text  # noqa: F401
from token_world.llm.llm import Message
from token_world.person.person import (
    PersonHandler,
    person_entity,
    get_person_action_form,
    get_person_action_form_template,
    get_person_action_form_filler,
)
from token_world.entity import Entity
from token_world.llm.form_filling.template import DictionaryTemplate
from token_world.llm.form_filling.form_filler import FormFiller


def assert_person_action_form(form_text: str):
    assert "THOUGHTS" in form_text
    assert "GOALS" in form_text
    assert "ACTION" in form_text


def test_person_entity_default():
    entity = person_entity("John Doe")
    assert isinstance(entity, Entity)
    assert entity.name == "John Doe"
    assert entity.properties["is_person"]
    assert entity.properties["x"] == 0.0
    assert entity.properties["y"] == 0.0
    assert entity.properties["z"] == 0.0


def test_person_entity_with_coordinates():
    entity = person_entity("Jane Doe", x=1.0, y=2.0, z=3.0)
    assert isinstance(entity, Entity)
    assert entity.name == "Jane Doe"
    assert entity.properties["is_person"]
    assert entity.properties["x"] == 1.0
    assert entity.properties["y"] == 2.0
    assert entity.properties["z"] == 3.0


def test_person_entity_with_id():
    entity = person_entity("John Smith", id="12345")
    assert isinstance(entity, Entity)
    assert entity.name == "John Smith"
    assert entity.id == "12345"


def test_get_person_action_form():
    assert_person_action_form(get_person_action_form())


def test_get_person_action_form_template():
    template = get_person_action_form_template()
    assert isinstance(template, DictionaryTemplate)
    assert template.children.keys() == {"THOUGHTS", "GOALS", "ACTION"}


def test_get_person_action_form_filler():
    form_filler = get_person_action_form_filler()
    assert isinstance(form_filler, FormFiller)
    assert_person_action_form(form_filler.template_text)


def test_person_handler_initialization():
    entity = person_entity("John Doe")
    handler = PersonHandler(entity)
    assert handler._entity == entity
    assert isinstance(handler.agent, Agent)
    assert handler.agent.name == "John Doe"
    assert handler.agent.model == "llama3.1:8b"
    assert handler.message_traversal.node.is_root()
    assert handler.message_traversal.node.children == []
    assert "ACTION" in handler._reaction_filler.template_text


@dataclass
class MockAgentResponse:
    messages: List[Message]


@dataclass
class MockStreamingAgentResponse:
    messages: List[Message]

    def __iter__(self):
        return iter([{"response": MockAgentResponse(self.messages)}])


def test_person_handler_act(filled_action_form_text):  # noqa: F811
    entity = person_entity("John Doe")
    handler = PersonHandler(entity)
    # create mock client
    client = Mock(spec=Swarm)
    client.run.return_value = MockStreamingAgentResponse([{"content": filled_action_form_text}])
    action = handler.act(client)
    assert action == "Go to the store"
    assert handler.message_traversal.node.message["content"] == filled_action_form_text
