from time import sleep
from typing import Dict
import streamlit as st
from token_world.llm.chat_management.resources import get_message_tree_db
from token_world.llm.chat_management.message_db import MessageNodeId, MessageNodeT, MessageTreeT

ChildSelections = Dict[MessageNodeId, int]


def data_streamer():
    for word in ["Hello", "world", "!"]:
        yield word + " "
        sleep(0.5)  # Simulate delay


def display_tree(tree: MessageTreeT, child_selections: ChildSelections) -> MessageNodeT:
    current_node = tree.root
    while True:
        if not current_node.is_root():
            with st.chat_message(current_node.message["role"]):
                st.markdown(current_node.message["content"])
        if not current_node.children:
            break
        selected_index = child_selections.get(current_node.id, 0)
        current_node = current_node.children[selected_index]
    return current_node


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

    leaf_node = display_tree(entry.tree, st.session_state.child_selections)

    # Get user input
    if prompt := st.chat_input("Type your message:"):
        message_tree_db.add_message_node(leaf_node.add_child({"role": "user", "content": prompt}))
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response (echoing user input in this example)
        with st.chat_message("assistant"):
            text = st.write_stream(data_streamer())
            if isinstance(text, str):
                message_tree_db.add_message_node(
                    leaf_node.add_child({"role": "assistant", "content": text})
                )


main()
