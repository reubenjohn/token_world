import re
from typing import List
import pytest
from token_world.llm.message_tree import MessageTree, MessageNode, MessageTreeTraversal

MessageTreeStr = MessageTree[str]
MessageNodeStr = MessageNode[str]
MessageTreeTraversalStr = MessageTreeTraversal[str]


def assert_tree_root(tree: MessageTreeStr):
    assert tree.root is not None
    assert tree.root.tree is not None
    with pytest.raises(ValueError, match="Root node has no parent"):
        _ = tree.root.parent
    with pytest.raises(ValueError, match="Root node has no message"):
        _ = tree.root.message
    assert tree.root.is_root()


def assert_node(node: MessageNodeStr, tree: MessageTreeStr, message: str, parent: MessageNodeStr):
    assert node.tree is tree
    assert node.parent is parent
    assert node.message == message


def assert_leaf_node(
    node: MessageNodeStr, tree: MessageTreeStr, message: str, parent: MessageNodeStr
):
    assert_node(node, tree, message, parent)


def assert_children(node: MessageNodeStr, children: List[MessageNodeStr]):
    assert len(node.children) == len(children)
    assert all(child1 is child2 for child1, child2 in zip(node.children, children))
    assert all(child.parent is node for child in node.children)


def test_tree_initialization():
    tree = MessageTreeStr.new()
    assert_tree_root(tree)
    assert tree.root.children == []


def test_message_node_add_child():
    tree = MessageTreeStr.new()
    root = tree.root
    child_message = "child_message"
    child_node = root.add_child(child_message)
    assert_tree_root(tree)
    assert_children(root, [child_node])
    assert_leaf_node(child_node, tree, child_message, root)

    # Adding another child to the root
    another_child_message = "another_child_message"
    another_child_node = root.add_child(another_child_message)
    assert_tree_root(tree)
    assert_children(root, [child_node, another_child_node])
    assert_leaf_node(child_node, tree, child_message, root)
    assert_leaf_node(another_child_node, tree, another_child_message, root)

    # Adding a child to the first child node
    grandchild_message = "grandchild_message"
    grandchild_node = child_node.add_child(grandchild_message)
    assert_tree_root(tree)
    assert_children(root, [child_node, another_child_node])
    assert_children(child_node, [grandchild_node])
    assert_leaf_node(another_child_node, tree, another_child_message, root)
    assert_leaf_node(grandchild_node, tree, grandchild_message, child_node)


def test_message_node_is_root():
    tree = MessageTreeStr.new()
    root = tree.root
    assert root.is_root()
    child_node = root.add_child("child_message")
    assert not child_node.is_root()


def test_message_node_parent_property():
    tree = MessageTreeStr.new()
    root = tree.root

    # Root node should raise ValueError when accessing parent
    with pytest.raises(ValueError):
        _ = root.parent

    # Child node should return correct parent
    child_message = "child_message"
    child_node = root.add_child(child_message)
    assert child_node.parent == root

    # Grandchild node should return correct parent
    grandchild_message = "grandchild_message"
    grandchild_node = child_node.add_child(grandchild_message)
    assert grandchild_node.parent == child_node


def test_message_node_get_message_chain():
    tree = MessageTreeStr.new()
    root = tree.root

    # Root node should have an empty message chain
    assert root.get_message_chain() == []

    # Adding a child to the root
    child_message = "child_message"
    child_node = root.add_child(child_message)
    assert child_node.get_message_chain() == [child_message]

    # Adding a grandchild to the child node
    grandchild_message = "grandchild_message"
    grandchild_node = child_node.add_child(grandchild_message)
    assert grandchild_node.get_message_chain() == [child_message, grandchild_message]

    # Adding another child to the root
    another_child_message = "another_child_message"
    another_child_node = root.add_child(another_child_message)
    assert another_child_node.get_message_chain() == [another_child_message]

    # Adding a child to the new child node
    another_grandchild_message = "another_grandchild_message"
    another_grandchild_node = another_child_node.add_child(another_grandchild_message)
    assert another_grandchild_node.get_message_chain() == [
        another_child_message,
        another_grandchild_message,
    ]


def test_message_node_create_twin():
    tree = MessageTreeStr.new()
    root = tree.root

    # Adding a child to the root
    child_message = "child_message"
    child_node = root.add_child(child_message)

    # Cloning the child node
    new_child_message1 = "new_child_message1"
    twin1 = child_node.create_twin(new_child_message1, lambda x: x)
    assert_children(root, [child_node, twin1])
    assert_leaf_node(child_node, tree, child_message, root)
    assert_leaf_node(twin1, tree, new_child_message1, root)

    # Adding a grandchild to the child node
    grandchild_message = "grandchild_message"
    grandchild_node = child_node.add_child(grandchild_message)

    # Cloning the child node with a grandchild
    new_child_message2 = "new_child_message2"
    twin2 = child_node.create_twin(new_child_message2, lambda x: x)
    assert_children(root, [child_node, twin1, twin2])

    assert_node(child_node, tree, child_message, root)
    assert_children(child_node, [grandchild_node])
    assert_leaf_node(grandchild_node, tree, grandchild_message, child_node)

    assert_leaf_node(twin1, tree, new_child_message1, root)

    assert_node(twin2, tree, new_child_message2, root)
    assert_children(twin2, [twin2.children[0]])
    assert_leaf_node(twin2.children[0], tree, grandchild_message, twin2)


def test_message_node_create_twin_root():
    tree = MessageTreeStr.new()
    root = tree.root

    # Root node should raise ValueError when cloning
    with pytest.raises(ValueError, match="Root node cannot be cloned"):
        _ = root.create_twin("child_message", lambda x: x)


def test_message_tree_count_nodes():
    tree = MessageTreeStr.new()
    assert tree.count_nodes() == 1

    # Add a child to the root
    child_node = tree.root.add_child("child_message")
    assert tree.count_nodes() == 2

    # Add a grandchild to the child node
    child_node.add_child("grandchild_message")
    assert tree.count_nodes() == 3

    # Add another child to the root
    another_child_node = tree.root.add_child("another_child_message")
    assert tree.count_nodes() == 4

    # Add a child to the new child node
    another_child_node.add_child("another_grandchild_message")
    assert tree.count_nodes() == 5


def test_message_tree_traversal_go_to_new_child():
    traversal = MessageTreeTraversalStr.new()
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.node is traversal.node.tree.root.children[0]
    assert traversal.go_to_new_child("grandchild_message") is traversal
    assert traversal.node is traversal.node.tree.root.children[0].children[0]


def test_message_tree_traversal_go_to_new_descendant():
    traversal = MessageTreeTraversalStr.new()

    # Test going to a new descendant
    descendant_chain = ["child_message", "grandchild_message", "great_grandchild_message"]
    assert traversal.go_to_new_descendant(descendant_chain) is traversal

    # Verify the traversal node is at the last descendant
    assert traversal.node.message == "great_grandchild_message"
    assert traversal.node.parent.message == "grandchild_message"
    assert traversal.node.parent.parent.message == "child_message"
    assert traversal.node.parent.parent.parent is traversal.node.tree.root

    # Verify the message chain
    assert traversal.node.get_message_chain() == descendant_chain

    # Test going to another new descendant from the root
    traversal.go_to_root()
    another_descendant_chain = ["another_child_message", "another_grandchild_message"]
    assert traversal.go_to_new_descendant(another_descendant_chain) is traversal

    # Verify the traversal node is at the last descendant
    assert traversal.node.message == "another_grandchild_message"
    assert traversal.node.parent.message == "another_child_message"
    assert traversal.node.parent.parent is traversal.node.tree.root

    # Verify the message chain
    assert traversal.node.get_message_chain() == another_descendant_chain


def test_message_tree_traversal_go_to_parent():
    traversal = MessageTreeTraversalStr.new()
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.go_to_parent() is traversal
    assert traversal.node is traversal.node.tree.root


def test_message_tree_traversal_go_to_child():
    traversal = MessageTreeTraversalStr.new()
    assert traversal.go_to_new_child("child_message") is traversal
    with pytest.raises(IndexError):
        traversal.go_to_child(0)
    assert traversal.go_to_parent() is traversal
    with pytest.raises(IndexError):
        traversal.go_to_child(1)
    assert traversal.go_to_child(0) is traversal
    assert traversal.node is traversal.node.tree.root.children[0]


def test_message_tree_traversal_go_to_root():
    traversal = MessageTreeTraversalStr.new()
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.go_to_new_child("grandchild_message") is traversal
    assert traversal.go_to_root() is traversal
    assert traversal.node is traversal.node.tree.root
    assert traversal.go_to_root() is traversal
    assert traversal.node is traversal.node.tree.root


def test_message_tree_traversal_get_current_message():
    traversal = MessageTreeTraversalStr.new()
    with pytest.raises(ValueError, match="Root node has no message"):
        _ = traversal.get_current_message()
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.get_current_message() == "child_message"


def test_message_tree_traversal_go_to_ancestor():
    traversal = MessageTreeTraversalStr.new()

    # Create a tree structure
    traversal.go_to_new_child("child_message")
    traversal.go_to_new_child("grandchild_message")
    traversal.go_to_new_child("great_grandchild_message")

    # Test going to ancestor
    great_grandchild_node = traversal.node
    grandchild_node = traversal.go_to_parent().node
    child_node = traversal.go_to_parent().node
    root_node = traversal.go_to_parent().node

    # Go to grandchild from great grandchild
    traversal.node = great_grandchild_node
    assert traversal.go_to_ancestor(grandchild_node) is traversal
    assert traversal.node is grandchild_node

    # Go to child from great grandchild
    traversal.node = great_grandchild_node
    assert traversal.go_to_ancestor(child_node) is traversal
    assert traversal.node is child_node

    # Go to root from great grandchild
    traversal.node = great_grandchild_node
    assert traversal.go_to_ancestor(root_node) is traversal
    assert traversal.node is root_node

    # Test ValueError when ancestor is not in the path
    with pytest.raises(ValueError, match="Ancestor not found in the path to the root"):
        traversal.go_to_ancestor(great_grandchild_node)


def test_message_node_id():
    tree = MessageTreeStr.new()
    root = tree.root

    # Root node should have a unique id
    assert isinstance(root.id, str)
    assert len(root.id) > 0
    # assert matches UUID regex
    regex = r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    assert re.match(regex, root.id)

    # Adding a child to the root
    child_message = "child_message"
    child_node = root.add_child(child_message)
    assert isinstance(child_node.id, str)
    assert len(child_node.id) > 0
    assert child_node.id != root.id

    # Adding another child to the root
    another_child_message = "another_child_message"
    another_child_node = root.add_child(another_child_message)
    assert isinstance(another_child_node.id, str)
    assert len(another_child_node.id) > 0
    assert another_child_node.id != root.id
    assert another_child_node.id != child_node.id

    # Adding a child to the first child node
    grandchild_message = "grandchild_message"
    grandchild_node = child_node.add_child(grandchild_message)
    assert isinstance(grandchild_node.id, str)
    assert len(grandchild_node.id) > 0
    assert grandchild_node.id != root.id
    assert grandchild_node.id != child_node.id
    assert grandchild_node.id != another_child_node.id


def test_message_tree_id():
    tree1 = MessageTreeStr.new()
    tree2 = MessageTreeStr.new()

    # Each tree should have a unique id
    assert isinstance(tree1.id, str)
    assert len(tree1.id) > 0
    assert isinstance(tree2.id, str)
    assert len(tree2.id) > 0
    assert tree1.id != tree2.id

    # Root nodes of different trees should have different ids
    assert tree1.root.id != tree2.root.id
