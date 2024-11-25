import argparse
from concurrent.futures import thread
import logging
from pathlib import Path
from time import sleep
import numpy as np
from pyglet.app import run  # type: ignore[import]

from token_world.drawable.physical import PhysicalEntityHandler
from token_world.entity import physical_entity
from token_world.world import persistent_world


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
