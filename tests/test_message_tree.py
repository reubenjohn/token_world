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


def assert_leaf_node(
    node: MessageNodeStr, tree: MessageTreeStr, message: str, parent: MessageNodeStr
):
    assert node.tree is tree
    assert node.parent is parent
    assert node.message == message
    assert node.children == []


def assert_children(node: MessageNodeStr, children: List[MessageNodeStr]):
    assert len(node.children) == len(children)
    assert all(child1 is child2 for child1, child2 in zip(node.children, children))
    assert all(child.parent is node for child in node.children)


def test_tree_initialization():
    tree = MessageTreeStr()
    assert_tree_root(tree)
    assert tree.root.children == []


def test_message_node_add_child():
    tree = MessageTreeStr()
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
    tree = MessageTreeStr()
    root = tree.root
    assert root.is_root()
    child_node = root.add_child("child_message")
    assert not child_node.is_root()


def test_message_node_parent_property():
    tree = MessageTreeStr()
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
    tree = MessageTreeStr()
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


def test_message_tree_traversal_go_to_new_child():
    tree = MessageTreeStr()
    traversal = MessageTreeTraversalStr.new(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.node is tree.root.children[0]
    assert traversal.go_to_new_child("grandchild_message") is traversal
    assert traversal.node is tree.root.children[0].children[0]


def test_message_tree_traversal_go_to_new_descendant():
    tree = MessageTreeStr()
    traversal = MessageTreeTraversalStr.new(tree)

    # Test going to a new descendant
    descendant_chain = ["child_message", "grandchild_message", "great_grandchild_message"]
    assert traversal.go_to_new_descendant(descendant_chain) is traversal

    # Verify the traversal node is at the last descendant
    assert traversal.node.message == "great_grandchild_message"
    assert traversal.node.parent.message == "grandchild_message"
    assert traversal.node.parent.parent.message == "child_message"
    assert traversal.node.parent.parent.parent is tree.root

    # Verify the message chain
    assert traversal.node.get_message_chain() == descendant_chain

    # Test going to another new descendant from the root
    traversal.go_to_root()
    another_descendant_chain = ["another_child_message", "another_grandchild_message"]
    assert traversal.go_to_new_descendant(another_descendant_chain) is traversal

    # Verify the traversal node is at the last descendant
    assert traversal.node.message == "another_grandchild_message"
    assert traversal.node.parent.message == "another_child_message"
    assert traversal.node.parent.parent is tree.root

    # Verify the message chain
    assert traversal.node.get_message_chain() == another_descendant_chain


def test_message_tree_traversal_go_to_parent():
    tree = MessageTreeStr()
    traversal = MessageTreeTraversalStr.new(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.go_to_parent() is traversal
    assert traversal.node is tree.root


def test_message_tree_traversal_go_to_child():
    tree = MessageTreeStr()
    traversal = MessageTreeTraversalStr.new(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    with pytest.raises(IndexError):
        traversal.go_to_child(0)
    assert traversal.go_to_parent() is traversal
    with pytest.raises(IndexError):
        traversal.go_to_child(1)
    assert traversal.go_to_child(0) is traversal
    assert traversal.node is tree.root.children[0]


def test_message_tree_traversal_go_to_root():
    tree = MessageTreeStr()
    traversal = MessageTreeTraversalStr.new(tree)
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.go_to_new_child("grandchild_message") is traversal
    assert traversal.go_to_root() is traversal
    assert traversal.node is tree.root
    assert traversal.go_to_root() is traversal
    assert traversal.node is tree.root


def test_message_tree_traversal_get_current_message():
    tree = MessageTreeStr()
    traversal = MessageTreeTraversalStr.new(tree)
    with pytest.raises(ValueError, match="Root node has no message"):
        _ = traversal.get_current_message()
    assert traversal.go_to_new_child("child_message") is traversal
    assert traversal.get_current_message() == "child_message"


def test_message_tree_traversal_go_to_ancestor():
    tree = MessageTreeStr()
    traversal = MessageTreeTraversalStr.new(tree)

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
