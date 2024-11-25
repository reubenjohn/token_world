import json
from pathlib import Path
from typing import Dict, Optional
import uuid
import sqlite3

EntityId = str


class Entity:

    def __init__(self, name: str, id: Optional[str] = None, **kwargs):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.properties = kwargs

    def properties_json(self) -> str:
        return json.dumps(self.properties)


EntityDict = Dict[EntityId, Entity]


def physical_entity(
    name: str, id: Optional[str] = None, x: float = 0.0, y: float = 0.0, z: float = 0.0, **kwargs
) -> Entity:
    return Entity(name, id, is_physical=True, x=x, y=y, z=z, **kwargs)


class EntityManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.entities: EntityDict = {}
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    properties TEXT
                )
            """
            )
            conn.commit()

    def add_entity(self, entity):
        self.entities[entity.id] = entity

    def save(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for entity in self.entities.values():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO entities (id, name, properties) VALUES (?, ?, ?)
                """,
                    (entity.id, entity.name, entity.properties_json()),
                )
            conn.commit()

    def load(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, properties FROM entities")
            for row in cursor.fetchall():
                entity_id, entity_name, data = row
                data = json.loads(data)
                entity = Entity(id=entity_id, name=entity_name, **data)
                self.entities[entity.id] = entity
