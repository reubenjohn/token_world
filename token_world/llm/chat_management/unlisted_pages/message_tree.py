from time import sleep
from typing import Dict, Optional
import streamlit as st
from token_world.llm.chat_management.resources import get_message_tree_db
from token_world.llm.chat_management.message_db import (
    MessageNodeId,
    MessageNodeT,
    MessageTreeDB,
    MessageTreeT,
)

ChildSelections = Dict[MessageNodeId, int]


def data_streamer():
    for word in ["Hello", "world", "!"]:
        yield word + " "
        sleep(0.5)  # Simulate delay


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


def display_node(
    current_node: MessageNodeT,
    message_tree_db: MessageTreeDB,
    child_selections: Optional[ChildSelections] = None,
):
    if child_selections is None:
        child_selections = st.session_state.child_selections

    if current_node.is_root():
        return

    siblings = current_node.parent.children
    self_index = child_selections.get(current_node.parent.id, 0)
    with st.chat_message(current_node.message["role"]):

        # draw navigation arrows side-by-side and right justify
        col1, col2, col3, col4 = st.columns([6, 1, 1, 1])

        with col1:
            preview, edit = st.tabs(
                [
                    "Preview",
                    "Edit",
                ]
            )

        with col2:
            if self_index > 0:
                if st.button("⬅️", key=f"<{current_node.id}"):
                    child_selections[current_node.parent.id] = self_index - 1
                    st.rerun()
        with col3:
            if self_index < len(siblings) - 1:
                if st.button("➡️", key=f">{current_node.id}"):
                    child_selections[current_node.parent.id] = self_index + 1
                    st.rerun()
        with col4:
            if st.button("🗑️", key=f"delete-{current_node.id}"):
                message_tree_db.delete_node(current_node)
                if self_index == 1:
                    child_selections.pop(current_node.parent.id)
                else:
                    child_selections[current_node.parent.id] = max(0, self_index - 1)
                st.rerun()

        with preview:
            st.markdown(current_node.message["content"])
        with edit:
            content = st.text_area(
                "Edit message",
                current_node.message["content"],
                key=f"content-{current_node.id}",
            )
            col1, col2 = st.columns(2)
            with col1:
                edit_in_place = st.checkbox("Edit in place", key=f"edit-in-place-{current_node.id}")
            with col2:
                if st.button("Save", key=f"save-{current_node.id}"):
                    if edit_in_place:
                        current_node.message["content"] = content
                        message_tree_db.update_node(current_node)
                        st.write("Message updated in place.")
                    else:
                        edit_node = current_node.parent.add_child(
                            {**current_node.message, "content": content}
                        )
                        message_tree_db.add_message_node(edit_node)
                        child_selections[current_node.parent.id] = (
                            len(current_node.parent.children) - 1
                        )
                        st.write("New edit node added.")
                        st.rerun()


def main():
    st.title("Message Tree")

    message_tree_db = get_message_tree_db()
    if (tree_id := st.query_params.get("tree_id", None)) is None:
        st.error("Query parameter tree_id is missing.")
        return

    if (entry := message_tree_db.entries.get(tree_id, None)) is None:
        st.error(f"No message tree found with ID: {tree_id}")
        return

    # Initialize chat history
    if "child_selections" not in st.session_state:
        st.session_state.child_selections = {}

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

    leaf_node = display_tree(entry.tree)

    # Get user input
    if prompt := st.chat_input("Type your message:"):
        user_node = leaf_node.add_child({"role": "user", "content": prompt})
        message_tree_db.add_message_node(user_node)
        # Display user message
        display_node(user_node, message_tree_db)

        # Generate assistant response (echoing user input in this example)
        with st.chat_message("assistant"):
            text = st.write_stream(data_streamer())
            assistant_node = user_node.add_child({"role": "assistant", "content": text})
            message_tree_db.add_message_node(assistant_node)
            st.rerun()
            return


main()
