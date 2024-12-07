import os
from dotenv import load_dotenv
import streamlit as st
from token_world.llm.chat_management.resources import get_message_tree_db


def show_admin_console():
    load_dotenv()
    st.title("Admin Console")

    with st.expander("Environment Variables"):
        st.table(os.environ.items())

    st.subheader("Database Information")
    st.write(f"World Directory: {os.getenv('WORLD_DIR')}")
    message_tree_db = get_message_tree_db()
    st.write(f"Database Path: {message_tree_db.db_path}")
    st.metric(label="Number of Trees", value=len(message_tree_db.entries))
    if st.button("🔄 Reload DB"):
        get_message_tree_db.clear()


show_admin_console()
