from contextlib import contextmanager
from pathlib import Path
from typing import List
from pyglet.window import Window  # type: ignore[import]
from pyglet.gl import glClearColor  # type: ignore[import]

from token_world.drawable.base import DrawableEntityHandler, DrawableEntityHandlerDict, DrawCallable
from token_world.entity import Entity, EntityManager
from token_world.person import PeopleManager


class World:
    DB_FILE = "world.db"

    def __init__(
        self,
        root_dir: Path,
        people_manager: PeopleManager,
        handlers: List[DrawableEntityHandler] = [],
    ):
        root_dir.mkdir(exist_ok=True, parents=True)
        self._entity_manager = EntityManager(root_dir / self.DB_FILE)
        self._drawable_entity_handler: DrawableEntityHandlerDict = {}
        self._draw_callbacks: List[DrawCallable] = []
        self._people_manager = people_manager

        self._window = Window(width=800, height=600)

        # Set a different clear color (e.g., white)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        @self._window.event
        def on_draw():
            for callback in self._draw_callbacks:
                callback()

            self._window.clear()
            for handler in self._drawable_entity_handler.values():
                handler.draw()

        for handler in handlers:
            self.add_drawable_callback_factory(handler)

    def add_drawable_callback_factory(self, handler: DrawableEntityHandler):
        self._drawable_entity_handler[handler.id] = handler

    def load(self):
        self._entity_manager.load()
        for entity in self._entity_manager.entities.values():
            self._on_add_entity(entity)

    def save(self):
        self._entity_manager.save()

    def add_entity(self, entity: Entity) -> Entity:
        self._entity_manager.add_entity(entity)
        self._on_add_entity(entity)
        return entity

    def _on_add_entity(self, entity: Entity):
        if self._people_manager.is_person(entity):
            self._people_manager.add_entity(entity)

        for handler in self._drawable_entity_handler.values():
            if handler.is_applicable(entity):
                self._draw_callbacks.append(handler.new_draw_callback(entity))
        return entity


@contextmanager
def persistent_world(
    root_dir: Path, people_manager: PeopleManager, handlers: List[DrawableEntityHandler]
):
    world = World(root_dir, people_manager, handlers)
    world.load()
    try:
        yield world
    finally:
        world.save()
