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


def test_entity_to_dict(entity):
    entity_dict = entity.to_dict()
    assert entity_dict["name"] == "Test Entity"
    assert entity_dict["attribute"] == "value"


def test_entity_to_json(entity):
    entity_json = entity.to_json()
    assert '"name": "Test Entity"' in entity_json
    assert '"attribute": "value"' in entity_json


def test_entity_manager_save(entity, manager, tmp_db_path):
    manager.add_entity(entity)
    manager.save()
    with sqlite3.connect(tmp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM entities WHERE id = ?", (entity.id,))
        row = cursor.fetchone()
        assert row is not None
        assert '"name": "Test Entity"' in row[0]
        assert '"attribute": "value"' in row[0]


if __name__ == "__main__":
    pytest.main()
