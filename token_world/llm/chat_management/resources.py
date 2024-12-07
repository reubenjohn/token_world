import logging
import os
from pathlib import Path
from typing import Dict
from urllib.parse import urlencode
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from swarm import Swarm  # type: ignore[import]

from token_world.llm.chat_management.message_db import MessageTreeDB, TreeId, MessageNodeId
from token_world.world import World


ChildSelections = Dict[MessageNodeId, int]


@st.cache_resource
def get_message_tree_db() -> MessageTreeDB:
    load_dotenv()
    world_dir = os.getenv("WORLD_DIR")
    if not world_dir:
        raise ValueError("WORLD_DIR environment variable not set")
    db = MessageTreeDB(Path(world_dir) / World.DB_FILE)
    try:
        db.load()
    except Exception as e:
        st.error(f"Error loading database: {e}", icon="🛡️")
    return db


@st.cache_resource
def get_swarm_client():
    load_dotenv()
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_base_url:
        raise ValueError("OPENAI_BASE_URL environment variable not set")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    logging.info(f"Connecting to OpenAI at {openai_base_url}")
    openai_client = OpenAI(base_url=openai_base_url, api_key=openai_api_key)
    return Swarm(openai_client)


def get_tree_link(tree_id: TreeId) -> str:
    query_params = urlencode({"tree_id": tree_id})
    return f"/message_tree?{query_params}"


def get_base_model_name() -> str:
    model = os.getenv("OPENAI_BASE_MODEL")
    if model is None:
        raise ValueError("OPENAI_BASE_MODEL environment variable not set")
    return model
