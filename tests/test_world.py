import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from token_world.drawable.base import DrawableEntityHandler
from token_world.world import World
from token_world.entity import Entity, EntityManager
from token_world.world import persistent_world
from token_world.person.person import PeopleManager
import tempfile
import shutil


@pytest.fixture
def drawable_handler() -> DrawableEntityHandler:
    mock_handler = MagicMock(spec=DrawableEntityHandler)
    mock_handler.id = "test_handler"
    mock_handler.is_applicable.return_value = True
    mock_handler.new_draw_callback.return_value = "draw_callback"
    return mock_handler


@pytest.fixture
@patch("token_world.world.Window")
def world(MockWindow, temp_dir):
    world = World(temp_dir, PeopleManager(client=MagicMock(), environment=MagicMock()), [])
    return world


@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield Path(dirpath)
    shutil.rmtree(dirpath)


def test_init(world: World, temp_dir):
    assert (temp_dir / World.DB_FILE).exists()
    assert world._entity_manager.entities == {}
    assert world._drawable_entity_handler == {}
    assert world._draw_callbacks == []


def test_add_drawable_callback_factory(world: World, drawable_handler: DrawableEntityHandler):
    world.add_drawable_callback_factory(drawable_handler)
    assert "test_handler" in world._drawable_entity_handler
    assert world._drawable_entity_handler["test_handler"] == drawable_handler


def test_save(world: World, temp_dir):
    test_entity = Entity.new("test_entity")
    world.add_entity(test_entity)
    world.save()

    entity_manager = EntityManager(temp_dir / World.DB_FILE)
    entity_manager.load()
    assert entity_manager.entities == {test_entity.id: test_entity}


def test_load(world: World, temp_dir):
    entity_manager = EntityManager(temp_dir / World.DB_FILE)
    test_entity = Entity.new("test_entity")
    entity_manager.add_entity(test_entity)
    entity_manager.save()

    world.load()
    assert world._entity_manager.entities == {test_entity.id: test_entity}


def test_add_entity(world: World, drawable_handler: MagicMock):
    test_entity = Entity.new("test_entity")
    result = world.add_entity(test_entity)
    assert result == test_entity
    assert world._entity_manager.entities == {test_entity.id: test_entity}

    world.add_drawable_callback_factory(drawable_handler)

    test_entity2 = Entity.new("test_entity2")
    drawable_handler.is_applicable.return_value = False
    result = world.add_entity(test_entity2)
    assert test_entity2.id in world._entity_manager.entities
    world._draw_callbacks == []

    test_entity3 = Entity.new("test_entity3")
    drawable_handler.is_applicable.return_value = True
    result = world.add_entity(test_entity3)
    assert test_entity3.id in world._entity_manager.entities
    assert drawable_handler.new_draw_callback.called_once_with(test_entity)
    assert world._draw_callbacks == [drawable_handler.new_draw_callback.return_value]


def test_add_non_person_entity(world: World, drawable_handler: MagicMock):
    non_person = Entity.new("mock_entity", is_person=False)

    world.add_drawable_callback_factory(drawable_handler)

    result = world.add_entity(non_person)
    assert result == non_person
    assert non_person.id in world._entity_manager.entities
    assert non_person.id not in world._people_manager._person_handlers
    assert world._draw_callbacks == [drawable_handler.new_draw_callback.return_value]


def test_add_person_entity(world: World, drawable_handler: MagicMock):
    person = Entity.new("mock_entity", is_person=True)

    world.add_drawable_callback_factory(drawable_handler)

    result = world.add_entity(person)
    assert result == person
    assert person.id in world._entity_manager.entities
    assert person.id in world._people_manager._person_handlers
    assert world._draw_callbacks == [drawable_handler.new_draw_callback.return_value]


def test_persisted_world_load_and_save(temp_dir):
    mock_handler = MagicMock()
    mock_people_manager = MagicMock(spec=PeopleManager)
    with persistent_world(temp_dir, mock_people_manager, [mock_handler]) as world:
        assert len(world._entity_manager.entities) == 0
        mock_entity = Entity.new("mock_entity")
        world.add_entity(mock_entity)
        assert len(world._entity_manager.entities) == 1

    with persistent_world(temp_dir, mock_people_manager, [mock_handler]) as world:
        assert len(world._entity_manager.entities) == 1
        assert world._entity_manager.entities[mock_entity.id] == mock_entity
