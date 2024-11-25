import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from token_world.world import World
from token_world.entity import Entity


@pytest.fixture
@patch("token_world.world.EntityManager")
@patch("token_world.world.Window")
def world_fixture(MockWindow, MockEntityManager):
    mock_root_dir = MagicMock(spec=Path)
    mock_entity_manager = MockEntityManager.return_value
    mock_window = MockWindow.return_value
    world = World(mock_root_dir)
    return world, mock_root_dir, MockEntityManager, mock_entity_manager, mock_window


def test_init(world_fixture):
    world, mock_root_dir, MockEntityManager, _, _ = world_fixture
    mock_root_dir.mkdir.assert_called_once_with(exist_ok=True, parents=True)
    MockEntityManager.assert_called_once_with(mock_root_dir / World.DB_FILE)
    assert world._drawable_entity_handler == {}
    assert world._draw_callbacks == []


def test_add_drawable_callback_factory(world_fixture):
    world, _, _, _, _ = world_fixture
    mock_handler = MagicMock()
    mock_handler.id = "test_handler"
    world.add_drawable_callback_factory(mock_handler)
    assert "test_handler" in world._drawable_entity_handler
    assert world._drawable_entity_handler["test_handler"] == mock_handler


def test_load(world_fixture):
    world, _, _, mock_entity_manager, _ = world_fixture
    mock_entity = MagicMock(spec=Entity)
    mock_entity_manager.entities = {"entity_1": mock_entity}
    world.add_entity = MagicMock()
    world.load()
    mock_entity_manager.load.assert_called_once()
    world.add_entity.assert_called_once_with(mock_entity)


def test_save(world_fixture):
    world, _, _, mock_entity_manager, _ = world_fixture
    world.save()
    mock_entity_manager.save.assert_called_once()


def test_add_entity(world_fixture):
    world, _, _, mock_entity_manager, _ = world_fixture
    mock_entity = MagicMock(spec=Entity)
    mock_handler = MagicMock()
    mock_handler.is_applicable.return_value = True
    mock_handler.new_draw_callback.return_value = "draw_callback"
    world._drawable_entity_handler = {"test_handler": mock_handler}
    result = world.add_entity(mock_entity)
    mock_entity_manager.add_entity.assert_called_once_with(mock_entity)
    assert "draw_callback" in world._draw_callbacks
    assert result == mock_entity
