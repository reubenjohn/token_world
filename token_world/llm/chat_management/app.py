import argparse
from pathlib import Path
import streamlit as st


def parse_args():
    parser = argparse.ArgumentParser(description="Streamlit app for managing message trees.")
    parser.add_argument(
        "--db-path", type=Path, required=True, help="Path to the message tree database."
    )
    return parser.parse_args()


def main():
    message_trees_page = st.Page("unlisted_pages/message_trees.py", title="🌲 Message Trees")
    message_tree = st.Page("unlisted_pages/message_tree.py", title="🌳 Message Tree")
    database_info_page = st.Page(
        "unlisted_pages/database_management.py", title="🛡️ Database Management"
    )

    page = st.navigation([message_trees_page, message_tree, database_info_page])

    page.run()


if __name__ == "__main__":
    main()
