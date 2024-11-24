import sqlite3
import pytest
from token_world.entity import Entity, EntityManager
import re


@pytest.fixture
def entity():
    return Entity(name="Test Entity", attribute="value")


@pytest.fixture
def tmp_db_path(tmpdir):
    return tmpdir / "/test_entities.db"


@pytest.fixture
def manager(tmp_db_path):
    return EntityManager(tmp_db_path)


def test_entity_creation(entity):
    assert entity.name == "Test Entity"
    assert entity.properties["attribute"] == "value"
    assert re.match(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", entity.id)


def test_entity_manager_save(entity, manager, tmp_db_path):
    manager.add_entity(entity)
    manager.save()
    with sqlite3.connect(tmp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, properties FROM entities WHERE id = ?", (entity.id,))
        name, properties = cursor.fetchone()
        assert name == "Test Entity"
        assert '{"attribute": "value"}' == properties


def test_entity_manager_load(entity, manager, tmp_db_path):
    manager.add_entity(entity)
    manager.save()
    manager.entities = {}  # Clear the in-memory entities
    manager.load()
    loaded_entity = manager.entities.get(entity.id)
    assert loaded_entity is not None
    assert loaded_entity.name == "Test Entity"
    assert loaded_entity.properties["attribute"] == "value"


if __name__ == "__main__":
    pytest.main()
