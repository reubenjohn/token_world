import streamlit as st
from token_world.llm.chat_management.resources import get_message_tree_db, get_tree_link
from token_world.llm.chat_management.message_db import MessageTreeT
import pandas as pd


def count_nodes(tree: MessageTreeT) -> int:
    count = 0
    stack = [tree.root]
    while stack:
        node = stack.pop()
        stack.extend(node.children)
        count += 1
    return count


def get_first_message(tree: MessageTreeT) -> str:
    if len(tree.root.children) == 0:
        return "<Tree Empty>"
    message = tree.root.children[0].message
    return f"{message['role']}: {message['content']}"


def show_message_trees():
    st.title("Message Trees")

    message_tree_db = get_message_tree_db()
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Number of Trees", value=len(message_tree_db.entries))

    with col2:
        if st.button("🔄 Reload Trees"):
            message_tree_db.load()

    data = [
        {
            "Tree Link": get_tree_link(entry.tree.id),
            "Tree ID": entry.tree.id,
            "Nodes": count_nodes(entry.tree),
            "Created At (UTC)": entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "First Message": get_first_message(entry.tree),
        }
        for entry in message_tree_db.entries.values()
    ]
    st.dataframe(
        pd.DataFrame(data),
        column_config={
            "Tree Link": st.column_config.LinkColumn(
                display_text="Open",
            )
        },
    )

    # if st.button("Delete All Trees"):
    #   message_tree_db.clear_trees()

    if st.button("Create Empty Tree"):
        message_tree_db.add_tree(MessageTreeT.new())
        st.rerun()


show_message_trees()
