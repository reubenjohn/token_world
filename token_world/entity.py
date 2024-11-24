import json
from typing import Optional
import uuid
import sqlite3


ID = str


class Entity:
    def __init__(self, name: str, id: Optional[str] = None, **kwargs):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.properties = kwargs

    def properties_json(self) -> str:
        return json.dumps(self.properties)


class EntityManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.entities = {}
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
