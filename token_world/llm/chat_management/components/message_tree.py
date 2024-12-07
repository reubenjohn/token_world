from typing import Optional
import streamlit as st
from token_world.llm.chat_management.components.message import display_node
from token_world.llm.chat_management.resources import get_message_tree_db, ChildSelections
from token_world.llm.chat_management.message_db import (
    MessageNodeT,
    MessageTreeDB,
    MessageTreeT,
    TreeEntry,
)


def message_tree_header(entry: TreeEntry, message_tree_db: MessageTreeDB):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Number of Nodes", value=entry.tree.count_nodes())

    with col2:
        if st.button("🔄 Reload Tree"):
            message_tree_db.load()

    with col3:
        if st.button("🗑️ Delete Messages"):
            message_tree_db.delete_nodes(entry.tree)
            st.rerun()
            return

    with col4:
        if st.button("❌ Delete Tree"):
            message_tree_db.delete_tree(entry.tree)
            # Redirect to message trees page
            st.switch_page("unlisted_pages/message_trees.py")
            return


def display_tree(
    tree: MessageTreeT, child_selections: Optional[ChildSelections] = None
) -> MessageNodeT:
    if child_selections is None:
        child_selections = st.session_state.child_selections

    message_tree_db = get_message_tree_db()

    current_node = tree.root
    while True:
        display_node(current_node, message_tree_db, child_selections)

        if not current_node.children:
            break
        current_node = current_node.children[child_selections.get(current_node.id, 0)]
    return current_node
