from typing import List
import pytest
from token_world.llm.message_tree import MessageTree, MessageNode, MessageTreeTraversal


def assert_tree_root(tree: MessageTree):
    assert tree.root is not None
    assert tree.root.tree is not None
    assert tree.root.message == "ROOT"
    assert tree.root.is_root()


def assert_leaf_node(node: MessageNode, tree: MessageTree, message: str, parent: MessageNode):
    assert node.tree is tree
    assert node.parent is parent
    assert node.message == message
    assert node.children == []


def assert_children(node: MessageNode, children: List[MessageNode]):
    assert len(node.children) == len(children)
    assert all(child1 is child2 for child1, child2 in zip(node.children, children))
    assert all(child.parent is node for child in node.children)


def test_tree_initialization():
    tree = MessageTree()
    assert_tree_root(tree)
    assert tree.root.children == []


def test_message_node_add_child():
    tree = MessageTree()
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
    tree = MessageTree()
    root = tree.root
    assert root.is_root()
    child_node = root.add_child("child_message")
    assert not child_node.is_root()


def test_message_node_parent_property():
    tree = MessageTree()
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


def test_message_tree_traversal_go_to_new_child():
    tree = MessageTree()
    traversal = MessageTreeTraversal(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.node is tree.root.children[0]
    assert traversal.go_to_new_child("grandchild_message") is traversal
    assert traversal.node is tree.root.children[0].children[0]


def test_message_tree_traversal_go_to_parent():
    tree = MessageTree()
    traversal = MessageTreeTraversal(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.go_to_parent() is traversal
    assert traversal.node is tree.root


def test_message_tree_traversal_go_to_child():
    tree = MessageTree()
    traversal = MessageTreeTraversal(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    with pytest.raises(IndexError):
        traversal.go_to_child(0)
    assert traversal.go_to_parent() is traversal
    with pytest.raises(IndexError):
        traversal.go_to_child(1)
    assert traversal.go_to_child(0) is traversal
    assert traversal.node is tree.root.children[0]


def test_message_tree_traversal_go_to_root():
    tree = MessageTree()
    traversal = MessageTreeTraversal(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.go_to_new_child("grandchild_message") is traversal
    assert traversal.go_to_root() is traversal
    assert traversal.node is tree.root
    assert traversal.go_to_root() is traversal
    assert traversal.node is tree.root


def test_message_tree_traversal_get_current_message():
    tree = MessageTree()
    traversal = MessageTreeTraversal(tree)
    assert traversal.get_current_message() == "ROOT"
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.get_current_message() == "child_message"
