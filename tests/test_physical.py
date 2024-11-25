import pytest
from unittest.mock import MagicMock
from pyglet.graphics import Batch  # type: ignore[import]
from token_world.entity import Entity
from token_world.drawable.physical import PhysicalEntityHandler


@pytest.fixture
def entity_fixture():
    entity = MagicMock(spec=Entity)
    entity.properties = {"x": 10, "y": 20, "is_physical": True}
    return entity


@pytest.fixture
def batch_fixture():
    return MagicMock(spec=Batch)


def test_is_applicable(entity_fixture):
    handler = PhysicalEntityHandler()
    assert handler.is_applicable(entity_fixture) is True
    entity_fixture.properties["is_physical"] = False
    assert handler.is_applicable(entity_fixture) is False


def test_new_draw_callback(entity_fixture, batch_fixture):
    handler = PhysicalEntityHandler()
    handler._batch = batch_fixture
    callback = handler.new_draw_callback(entity_fixture)
    assert callable(callback)
    assert isinstance(callback, handler.Callback)
    assert callback.entity == entity_fixture
    assert callback.shape.batch == batch_fixture


def test_callback_call(entity_fixture, batch_fixture):
    handler = PhysicalEntityHandler()
    handler._batch = batch_fixture
    callback = handler.new_draw_callback(entity_fixture)
    entity_fixture.properties["x"] = 30
    entity_fixture.properties["y"] = 40
    callback()
    assert callback.shape.x == 30
    assert callback.shape.y == 40


def test_draw(batch_fixture):
    handler = PhysicalEntityHandler()
    handler._batch = batch_fixture
    handler.draw()
    batch_fixture.draw.assert_called_once()
