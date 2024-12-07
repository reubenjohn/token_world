import os
import streamlit as st
from token_world.llm.chat_management.resources import get_message_tree_db


def show_database_info_page():
    st.title("Database Info")
    st.write(f"World Directory: {os.getenv('WORLD_DIR')}")
    message_tree_db = get_message_tree_db()
    st.write(f"Database Path: {message_tree_db.db_path}")
    st.write(f"Number of Trees: {len(message_tree_db.entries)}")


show_database_info_page()
