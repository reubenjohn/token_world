from token_world.person import person_entity
from token_world.entity import Entity


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
    assert entity.properties["is_person"]
