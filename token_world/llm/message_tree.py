from dataclasses import dataclass, field
from typing import Any, List, Optional


Message = Any


@dataclass
class MessageNode:
    tree: "MessageTree"
    message: Message
    _parent: Optional["MessageNode"] = None
    children: List["MessageNode"] = field(default_factory=list)

    def add_child(self, message: Message) -> "MessageNode":
        child = MessageNode(tree=self.tree, message=message, _parent=self, children=[])
        self.children.append(child)
        return child

    def is_root(self) -> bool:
        return self._parent is None

    @property
    def parent(self) -> "MessageNode":
        if self._parent is None:
            raise ValueError("Cannot go to parent of root node")
        return self._parent


class MessageTree:
    def __init__(self, root: Optional[MessageNode] = None):
        self.root = (
            root
            if root is not None
            else MessageNode(tree=self, message="ROOT", _parent=None, children=[])
        )


@dataclass
class MessageTreeTraversal:
    tree: MessageTree
    node: MessageNode

    def __init__(self, tree: MessageTree):
        self.tree = tree
        self.node = tree.root

    def go_to_new_child(self, message: Message) -> "MessageTreeTraversal":
        self.node = self.node.add_child(message)
        return self

    def go_to_parent(self) -> "MessageTreeTraversal":
        self.node = self.node.parent
        return self

    def go_to_child(self, index: int) -> "MessageTreeTraversal":
        self.node = self.node.children[index]
        return self

    def go_to_root(self) -> "MessageTreeTraversal":
        self.node = self.tree.root
        return self

    def get_current_message(self) -> Message:
        return self.node.message
