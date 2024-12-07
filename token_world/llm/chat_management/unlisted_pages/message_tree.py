from time import sleep
import streamlit as st
from swarm import Agent  # type: ignore[import]
from token_world.llm.chat_management.components.message import display_node
from token_world.llm.chat_management.components.message_tree import (
    display_tree,
    message_tree_header,
)
from token_world.llm.chat_management.resources import (
    get_base_model_name,
    get_message_tree_db,
    get_swarm_client,
)
from token_world.llm.chat_management.message_db import MessageTreeDB, MessageNodeT
from token_world.llm.stream_processing import MessageStream, parse_streaming_response


def data_streamer():
    for word in ["Hello", "world", "!"]:
        yield word + " "
        sleep(0.5)  # Simulate delay


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

    message_tree_header(entry, message_tree_db)
    leaf_node = display_tree(entry.tree)
    user_input(leaf_node, message_tree_db)


def user_input(leaf_node: MessageNodeT, message_tree_db: MessageTreeDB):
    if prompt := st.chat_input("Type your message:"):
        user_node = leaf_node.add_child({"role": "user", "content": prompt})
        message_tree_db.add_subtree(user_node)
        display_node(user_node, message_tree_db)

        messages = user_node.get_message_chain()
        with st.chat_message("assistant"):
            client = get_swarm_client()
            try:
                agent = Agent(model=get_base_model_name())

                response = client.run(agent=agent, messages=messages, stream=True)
                response = parse_streaming_response(response)
                for element in response:
                    if isinstance(element, MessageStream):
                        if element.role != "assistant":
                            st.error(
                                f"MessageStream has unexpected role: '{element.role}'"
                                " (expected 'assistant')"
                            )
                        text = st.write_stream(element.content_stream)
                        assistant_node = user_node.add_child(
                            {"role": element.role, "content": text}
                        )
                        message_tree_db.add_subtree(assistant_node)
                    else:
                        st.write(element)
                st.rerun()
                return
            except Exception as e:
                st.error(f"Error processing response: {e}")
                get_swarm_client.clear()  # type: ignore[attr-defined]


main()
