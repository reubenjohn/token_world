import logging
import os
from pathlib import Path
import argparse
from dotenv import load_dotenv

from pyglet.app import run  # type: ignore[import]

from token_world.drawable.physical import PhysicalEntityHandler
from token_world.environment import Environment
from token_world.person.person import people_manager_executor, person_entity
from token_world.world import persistent_world

from openai import OpenAI
from swarm import Swarm  # type: ignore[import]


def main():
    load_dotenv()  # Load environment variables from .env file

    parser = argparse.ArgumentParser(description="Simulate a world with persons")
    parser.add_argument(
        "--world_dir",
        type=Path,
        help="Path to the folder in which to persist world data.",
        required=True,
    )
    parser.add_argument(
        "--openai_base_url",
        type=str,
        default=os.getenv("OPENAI_BASE_URL"),
        help="The base URL for the Swarm API",
    )
    parser.add_argument(
        "--openai_api_key",
        type=str,
        default=os.getenv("OPENAI_API_KEY"),
        help="The API key for the Swarm API",
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level.upper(), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if args.openai_base_url is None:
        raise ValueError("The --openai_base_url argument is required")

    if args.openai_api_key is None:
        raise ValueError("The --openai_api_key argument is required")

    logging.info(f"Connecting to Swarm at {args.openai_base_url}")
    openai_client = OpenAI(base_url=args.openai_base_url, api_key=args.openai_api_key)
    client = Swarm(client=openai_client)

    physical_entity_handler = PhysicalEntityHandler()
    environment = Environment(client)
    with people_manager_executor(client, environment) as people_manager, persistent_world(
        args.world_dir, people_manager, [physical_entity_handler]
    ) as world:
        if not world._entity_manager.entities:
            world.add_entity(person_entity("Alice", x=100, y=350))
        run()


if __name__ == "__main__":
    main()
