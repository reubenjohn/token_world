from typing import Optional

from token_world.entity import Entity, physical_entity


def person_entity(
    name: str, id: Optional[str] = None, x: float = 0.0, y: float = 0.0, z: float = 0.0, **kwargs
) -> Entity:
    return physical_entity(name, id, is_person=True, x=x, y=y, z=z, **kwargs)
