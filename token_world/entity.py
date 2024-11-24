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

    def to_dict(self):
        return {"id": self.id, "name": self.name, **self.properties}

    def to_json(self):
        return json.dumps(self.to_dict())


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
                    data TEXT
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
                    INSERT OR REPLACE INTO entities (id, data) VALUES (?, ?)
                """,
                    (entity.id, entity.to_json()),
                )
            conn.commit()
