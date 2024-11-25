from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import uuid
import sqlite3

EntityId = str


@dataclass
class Entity:
    id: EntityId
    name: str
    properties: Dict[str, Any]

    @staticmethod
    def new(name: str, id: Optional[str] = None, **kwargs):
        return Entity(id or str(uuid.uuid4()), name, kwargs)

    def properties_json(self) -> str:
        return json.dumps(self.properties)


EntityDict = Dict[EntityId, Entity]


def physical_entity(
    name: str, id: Optional[str] = None, x: float = 0.0, y: float = 0.0, z: float = 0.0, **kwargs
) -> Entity:
    return Entity.new(name, id, is_physical=True, x=x, y=y, z=z, **kwargs)


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
            cursor.executemany(
                """
                INSERT OR REPLACE INTO entities (id, name, properties) VALUES (?, ?, ?)
                """,
                [
                    (entity.id, entity.name, entity.properties_json())
                    for entity in self.entities.values()
                ],
            )
            inserted_count = cursor.rowcount
            logging.info(f"Inserted {inserted_count} out of {len(self.entities)} entities")
            conn.commit()

    def load(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(id) FROM entities")
            count = cursor.fetchone()
            logging.info(f"Loading {count[0]} entities")
            cursor.execute("SELECT id, name, properties FROM entities")
            for row in cursor.fetchall():
                entity_id, entity_name, data = row
                data = json.loads(data)
                entity = Entity.new(id=entity_id, name=entity_name, **data)
                self.entities[entity.id] = entity
