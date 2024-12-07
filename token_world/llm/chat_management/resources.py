import os
from pathlib import Path
from urllib.parse import urlencode
from dotenv import load_dotenv
import streamlit as st

from token_world.llm.chat_management.message_db import MessageTreeDB, TreeId
from token_world.world import World


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


def get_tree_link(tree_id: TreeId) -> str:
    query_params = urlencode({"tree_id": tree_id})
    return f"/message_tree?{query_params}"
