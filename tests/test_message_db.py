from pathlib import Path
import pytest
import sqlite3
from token_world.llm.chat_management.message_db import MessageTreeDB, MessageTreeT, MessageNodeT
from token_world.llm.chat_management.message_db import TreeReconstructor, _NodeQueryRow


@pytest.fixture
def temp_db_path(tmp_path):
    return tmp_path / "test_message_tree.db"


@pytest.fixture
def message_tree_db(temp_db_path):
    return MessageTreeDB(temp_db_path)


def assert_node(node: MessageNodeT, expected_node: _NodeQueryRow, expected_n_children: int):
    assert node.id == expected_node.id
    if expected_node.parent_id is None:
        assert node.is_root()
    else:
        assert node.parent.id == expected_node.parent_id
    assert node.message["role"] == expected_node.role
    assert node.message["content"] == expected_node.content
    assert len(node.children) == expected_n_children


def test_tree_reconstructor_empty():
    tree = MessageTreeT.new()
    root = tree.root
    reconstructed_tree = TreeReconstructor(tree, iter([])).reconstruct()
    assert reconstructed_tree is tree
    assert reconstructed_tree.root is root
    assert reconstructed_tree.root.children == []


def test_tree_reconstructor_no_root():
    rows = [
        _NodeQueryRow(id="child1", parent_id="root", role="user", content="child1"),
        _NodeQueryRow(id="child2", parent_id="root", role="user", content="child2"),
    ]
    with pytest.raises(ValueError):
        TreeReconstructor(MessageTreeT.new(), iter(rows)).reconstruct()


def test_tree_reconstructor_single_node():
    root_row = _NodeQueryRow(id="root", parent_id=None, role="root", content="root")
    reconstructed_tree = TreeReconstructor(MessageTreeT.new(), iter([root_row])).reconstruct()
    assert_node(reconstructed_tree.root, root_row, expected_n_children=0)


def test_tree_reconstructor_multiple_nodes():
    rows = [
        _NodeQueryRow(id="root", parent_id=None, role="root", content="root"),
        _NodeQueryRow(id="child1", parent_id="root", role="user", content="child1"),
        _NodeQueryRow(id="child2", parent_id="root", role="user", content="child2"),
        _NodeQueryRow(id="child3", parent_id="child1", role="user", content="child3"),
    ]
    reconstructed_tree = TreeReconstructor(MessageTreeT.new(), iter(rows)).reconstruct()
    assert_node(reconstructed_tree.root, rows[0], expected_n_children=2)
    assert_node(reconstructed_tree.root.children[0], rows[1], expected_n_children=1)
    assert_node(reconstructed_tree.root.children[1], rows[2], expected_n_children=0)
    assert_node(reconstructed_tree.root.children[0].children[0], rows[3], expected_n_children=0)


def test_add_tree(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    assert tree.id in message_tree_db.entries


def test_add_tree_already_exists(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    with pytest.raises(ValueError, match=f"Tree with id {tree.id} already exists"):
        message_tree_db.add_tree(tree)


def test_add_message_node(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    tree_id = tree.id
    message_tree_db.add_tree(tree)
    root = tree.root
    root_id = root.id
    child_message = {"role": "user", "content": "child_message"}
    child_node = root.add_child(child_message)
    child_id = child_node.id
    message_tree_db.add_message_node(child_node)

    with sqlite3.connect(message_tree_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, tree_id, parent_id, role, content FROM message_node WHERE id = ?",
            (child_node.id,),
        )
        row = cursor.fetchone()
        assert row == (child_id, tree_id, root_id, "user", "child_message")


def test_add_message_node_tree_does_not_exist(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    root = tree.root
    child_message = {"role": "user", "content": "child_message"}
    child_node = root.add_child(child_message)
    with pytest.raises(ValueError, match=f"Tree with id {tree.id} does not exist"):
        message_tree_db.add_message_node(child_node)


def test_load(message_tree_db: MessageTreeDB, temp_db_path: Path):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    child_message1 = {"role": "user", "content": "child_message1"}
    child_message2 = {"role": "user", "content": "child_message2"}
    child_node1 = tree.root.add_child(child_message1)
    child_node2 = tree.root.add_child(child_message2)
    message_tree_db.add_message_node(child_node1)
    message_tree_db.add_message_node(child_node2)

    # Reload the database
    message_tree_db = MessageTreeDB(temp_db_path)
    message_tree_db.load()
    loaded_tree = message_tree_db.entries[tree.id].tree
    assert loaded_tree.id == tree.id
    assert loaded_tree.root.id == tree.root.id
    assert len(loaded_tree.root.children) == 2
    assert loaded_tree.root.children[0].id == child_node1.id
    assert loaded_tree.root.children[0].tree.id == child_node1.tree.id
    assert loaded_tree.root.children[0].message == child_message1
    assert loaded_tree.root.children[1].id == child_node2.id
    assert loaded_tree.root.children[1].tree.id == child_node2.tree.id
    assert loaded_tree.root.children[1].message == child_message2


def test_wipe(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    message_tree_db.wipe()
    assert len(message_tree_db.entries) == 0
    with sqlite3.connect(message_tree_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(id) FROM message_tree")
        count = cursor.fetchone()[0]
        assert count == 0
        cursor.execute("SELECT count(id) FROM message_node")
        count = cursor.fetchone()[0]
        assert count == 0


def test_delete_tree(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    message_tree_db.delete_tree(tree)
    assert tree.id not in message_tree_db.entries
    with sqlite3.connect(message_tree_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(id) FROM message_tree WHERE id = ?", (tree.id,))
        count = cursor.fetchone()[0]
        assert count == 0
        cursor.execute("SELECT count(id) FROM message_node WHERE tree_id = ?", (tree.id,))
        count = cursor.fetchone()[0]
        assert count == 0


def test_delete_tree_does_not_exist(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    with pytest.raises(ValueError, match=f"Tree with id {tree.id} does not exist"):
        message_tree_db.delete_tree(tree)


def test_delete_nodes(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    child_message = {"role": "user", "content": "child_message"}
    child_node = tree.root.add_child(child_message)
    message_tree_db.add_message_node(child_node)
    message_tree_db.delete_nodes(tree)
    assert len(tree.root.children) == 0
    assert tree.count_nodes() == 1
    with sqlite3.connect(message_tree_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(id) FROM message_node WHERE tree_id = ?", (tree.id,))
        count = cursor.fetchone()[0]
        assert count == 0


def test_delete_node(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    child_message = {"role": "user", "content": "child_message"}
    child_node = tree.root.add_child(child_message)
    message_tree_db.add_message_node(child_node)
    message_tree_db.delete_node(child_node)
    assert len(tree.root.children) == 0
    with sqlite3.connect(message_tree_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(id) FROM message_node WHERE id = ?", (child_node.id,))
        count = cursor.fetchone()[0]
        assert count == 0


def test_delete_node_tree_does_not_exist(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    root = tree.root
    child_message = {"role": "user", "content": "child_message"}
    child_node = root.add_child(child_message)
    with pytest.raises(ValueError, match=f"Tree with id {tree.id} does not exist"):
        message_tree_db.delete_node(child_node)


def test_delete_root_node(message_tree_db: MessageTreeDB):
    tree = MessageTreeT.new()
    message_tree_db.add_tree(tree)
    with pytest.raises(ValueError, match="Cannot delete root node"):
        message_tree_db.delete_node(tree.root)
