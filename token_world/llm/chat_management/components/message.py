from typing import Optional
import streamlit as st
from token_world.llm.chat_management.resources import ChildSelections
from token_world.llm.chat_management.message_db import (
    MessageNodeT,
    MessageTreeDB,
)


def display_node(
    current_node: MessageNodeT,
    message_tree_db: MessageTreeDB,
    child_selections: Optional[ChildSelections] = None,
):
    if child_selections is None:
        child_selections = st.session_state.child_selections

    if current_node.is_root():
        return

    with st.chat_message(current_node.message["role"]):
        preview, edit = node_header(current_node, message_tree_db, child_selections)

        with preview:
            st.markdown(current_node.message["content"])

        with edit:
            node_edit_tab(current_node, message_tree_db, child_selections)


def node_header(
    node: MessageNodeT, message_tree_db: MessageTreeDB, child_selections: ChildSelections
):
    _, col2, col3, col4 = st.columns([6, 1, 1, 1])

    self_index = child_selections.get(node.parent.id, 0)
    if self_index > 0:
        with col2:
            if st.button("⬅️", key=f"<{node.id}"):
                child_selections[node.parent.id] = self_index - 1
                st.rerun()
                return

    if self_index < len(node.parent.children) - 1:
        with col3:
            if st.button("➡️", key=f">{node.id}"):
                child_selections[node.parent.id] = self_index + 1
                st.rerun()
                return
    with col4:
        if st.button("🗑️", key=f"delete-{node.id}"):
            message_tree_db.delete_node(node)
            if self_index == 1:
                child_selections.pop(node.parent.id)
            else:
                child_selections[node.parent.id] = max(0, self_index - 1)
            st.rerun()
            return

    return st.tabs(["Preview", "Edit"])


def node_edit_tab(
    node: MessageNodeT, message_tree_db: MessageTreeDB, child_selections: ChildSelections
):
    content = st.text_area(
        "Edit message",
        node.message["content"],
        key=f"content-{node.id}",
    )
    col1, col2 = st.columns(2)
    with col1:
        edit_in_place = st.checkbox("Edit in place", key=f"edit-in-place-{node.id}")
    with col2:
        if st.button("Save", key=f"save-{node.id}"):
            if edit_in_place:
                node.message["content"] = content
                message_tree_db.update_node(node)
                st.write("Message updated in place.")
            else:
                edit_node = node.create_twin({**node.message, "content": content}, copy_msg=dict)
                message_tree_db.add_subtree(edit_node)
                child_selections[node.parent.id] = len(node.parent.children) - 1
                st.write("New edit node added.")
                st.rerun()
