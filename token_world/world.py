import argparse
from pathlib import Path
from pyglet.app import run
from pyglet.shapes import Triangle
from pyglet.graphics import Batch
from pyglet.window import Window
from pyglet.gl import glClearColor

from token_world.entity import Entity, EntityManager, physical_entity


class World:
    DB_FILE = "world.db"

    def __init__(self, root_dir: Path):
        root_dir.mkdir(exist_ok=True, parents=True)
        self.entity_manager = EntityManager(root_dir / self.DB_FILE)

        self.window = Window(width=800, height=600)
        self.batch = Batch()
        # Set a different clear color (e.g., white)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        @self.window.event
        def on_draw():
            self.window.clear()
            self.batch.draw()

    def add_entity(self, entity: Entity):
        self.entity_manager.add_entity(entity)
        if entity.properties.get("is_physical", False):
            self._add_physical_entity(entity)

    def _add_physical_entity(self, entity: Entity):
        props = entity.properties
        x, y = props["x"], props["y"]
        setattr(
            entity,
            "shape",
            Triangle(x, y, x + 10, y, x + 5, y + 10, color=(255, 0, 0), batch=self.batch),
        )


def main():
    parser = argparse.ArgumentParser(prog="token-world", usage="%(prog)s [options] root_dir")
    parser.add_argument("--root-dir", type=Path)
    args = parser.parse_args()

    root_dir = args.root_dir

    world = World(root_dir)
    # Add some entities for demonstration
    world.add_entity(physical_entity("Person A", x=100, y=150))
    world.add_entity(physical_entity("Person B", x=200, y=250))

    run()


if __name__ == "__main__":
    main()
