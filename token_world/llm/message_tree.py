from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar


Message = TypeVar("Message")


@dataclass
class MessageNode(Generic[Message]):
    tree: "MessageTree"
    _message: Optional[Message] = None
    _parent: Optional["MessageNode"] = None
    children: List["MessageNode"] = field(default_factory=list)

    def add_child(self, message: Message) -> "MessageNode":
        child = MessageNode(tree=self.tree, _message=message, _parent=self, children=[])
        self.children.append(child)
        return child

    def is_root(self) -> bool:
        return self._parent is None

    @property
    def parent(self) -> "MessageNode":
        if self._parent is None:
            raise ValueError("Root node has no parent")
        return self._parent

    @property
    def message(self) -> Message:
        if self._message is None:
            raise ValueError("Root node has no message")
        return self._message

    def get_message_chain(self) -> List[Message]:
        chain = []
        node = self
        while not node.is_root():
            chain.append(node.message)
            node = node.parent
        chain.reverse()
        return chain


class MessageTree(Generic[Message]):
    def __init__(self, root: Optional[MessageNode[Message]] = None):
        self.root = (
            root
            if root is not None
            else MessageNode[Message](tree=self, _message=None, _parent=None, children=[])
        )


@dataclass
class MessageTreeTraversal(Generic[Message]):
    tree: MessageTree[Message]
    node: MessageNode[Message]

    def __init__(self, tree: MessageTree[Message]):
        self.tree = tree
        self.node = tree.root

    def go_to_new_child(self, message: Message) -> "MessageTreeTraversal[Message]":
        self.node = self.node.add_child(message)
        return self

    def go_to_new_descendant(
        self, descendant_chain: List[Message]
    ) -> "MessageTreeTraversal[Message]":
        for message in descendant_chain:
            self.go_to_new_child(message)
        return self

    def go_to_parent(self) -> "MessageTreeTraversal[Message]":
        self.node = self.node.parent
        return self

    def go_to_child(self, index: int) -> "MessageTreeTraversal[Message]":
        self.node = self.node.children[index]
        return self

    def go_to_root(self) -> "MessageTreeTraversal[Message]":
        self.node = self.tree.root
        return self

    def go_to_ancestor(self, ancestor: MessageNode[Message]) -> "MessageTreeTraversal[Message]":
        node = self.node
        while node is not ancestor and not node.is_root():
            node = node.parent

        if node is not ancestor:
            raise ValueError("Ancestor not found in the path to the root")

        self.node = ancestor
        return self

    def get_current_message(self) -> Message:
        return self.node.message
