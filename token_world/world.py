import argparse
from concurrent.futures import thread
from contextlib import contextmanager
import logging
from pathlib import Path
from time import sleep
from typing import List
import numpy as np
from pyglet.app import run  # type: ignore[import]
from pyglet.window import Window  # type: ignore[import]
from pyglet.gl import glClearColor  # type: ignore[import]

from token_world.drawable.base import DrawableEntityHandler, DrawableEntityHandlerDict, DrawCallable
from token_world.drawable.physical import PhysicalEntityHandler
from token_world.entity import Entity, EntityManager, physical_entity


class World:
    DB_FILE = "world.db"

    def __init__(self, root_dir: Path, handlers: List[DrawableEntityHandler] = []):
        root_dir.mkdir(exist_ok=True, parents=True)
        self._entity_manager = EntityManager(root_dir / self.DB_FILE)
        self._drawable_entity_handler: DrawableEntityHandlerDict = {}
        self._draw_callbacks: List[DrawCallable] = []

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
            self.add_entity(entity)

    def save(self):
        self._entity_manager.save()

    def add_entity(self, entity: Entity):
        self._entity_manager.add_entity(entity)
        for handler in self._drawable_entity_handler.values():
            if handler.is_applicable(entity):
                self._draw_callbacks.append(handler.new_draw_callback(entity))
        return entity


@contextmanager
def persistent_world(root_dir: Path, handlers: List[DrawableEntityHandler]):
    world = World(root_dir, handlers)
    world.load()
    try:
        yield world
    finally:
        world.save()


def main():
    parser = argparse.ArgumentParser(prog="token-world", usage="%(prog)s [options] root_dir")
    parser.add_argument("--root-dir", type=Path)
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    root_dir = args.root_dir

    physical_entity_handler = PhysicalEntityHandler()
    with persistent_world(root_dir, [physical_entity_handler]) as world:
        if not world._entity_manager.entities:
            [
                world.add_entity(physical_entity(f"Entity {i}", x=100 + i * 5, y=350 + i))
                for i in range(50)
            ]

        running = True

        def update_y():
            vels = np.array([0.0] * 50)
            while running:
                vels -= 9.8
                for i, entity in enumerate(world._entity_manager.entities.values()):
                    if not physical_entity_handler.is_applicable(entity):
                        continue
                    entity.properties["y"] += vels[i]
                    if entity.properties["y"] < 0:
                        entity.properties["y"] = -entity.properties["y"]
                        vels[i] = -vels[i] * 0.9
                sleep(0.1)

        with thread.ThreadPoolExecutor() as executor:
            executor.submit(update_y)
            run()
            running = False


if __name__ == "__main__":
    main()
