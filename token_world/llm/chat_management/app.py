from dataclasses import dataclass
from time import sleep
from typing import Dict
import streamlit as st

from token_world.llm.message_tree import MessageNode, MessageTree, MessageTreeTraversal

MessageId = int


@dataclass
class Message:
    COUNT = 0

    id: MessageId
    role: str
    message: str

    @classmethod
    def new(cls, role: str, message: str):
        cls.COUNT += 1
        return Message(id=cls.COUNT, role=role, message=message)


ChildSelections = Dict[MessageId, int]
MessageType = Message
MessageNodeT = MessageNode[MessageType]
MessageTreeT = MessageTree[MessageType]

tree_traversal = MessageTreeTraversal[MessageType].new()
tree_traversal.go_to_new_child(Message.new("user", "Hello, how are you?"))
tree_traversal.go_to_new_child(Message.new("assistant", "Hi, I'm good"))
tree_traversal.go_to_parent()
tree_traversal.go_to_new_child(Message.new("assistant", "I'm not feeling well"))
tree = tree_traversal.node.tree


def data_streamer():
    for word in ["Hello", "world", "!"]:
        yield word + " "
        sleep(0.5)  # Simulate delay


st.title("Message Tree")

# Initialize chat history
if "child_selections" not in st.session_state:
    st.session_state.child_selections = {}


def get_message_id(node: MessageNodeT) -> MessageId:
    return 0 if node.is_root() else node.message.id


def display_tree(tree: MessageTreeT, child_selections: ChildSelections) -> MessageNodeT:
    current_node = tree.root
    while True:
        if not current_node.is_root():
            with st.chat_message(current_node.message.role):
                st.markdown(current_node.message.message)
        if not current_node.children:
            break
        selected_index = child_selections.get(get_message_id(current_node), 0)
        current_node = current_node.children[selected_index]
    return current_node


leaf_node = display_tree(tree, st.session_state.child_selections)

# Get user input
if prompt := st.chat_input("Type your message:"):
    leaf_node.add_child(Message.new("user", prompt))
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response (echoing user input in this example)
    response = f"Echo: {prompt}"
    with st.chat_message("assistant"):
        text = st.write_stream(data_streamer())
        if isinstance(text, str):
            leaf_node.add_child(Message.new("system", text))
