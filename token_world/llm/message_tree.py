from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar
import uuid


TreeId = str
MessageNodeId = str
Message = TypeVar("Message")


@dataclass
class MessageNode(Generic[Message]):
    tree: "MessageTree"
    id: MessageNodeId = field(default_factory=lambda: MessageNodeId(uuid.uuid4()))
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


@dataclass
class MessageTree(Generic[Message]):
    root: MessageNode[Message]
    id: TreeId = field(default_factory=lambda: TreeId(uuid.uuid4()))

    @staticmethod
    def new(
        root: Optional[MessageNode[Message]] = None, id: Optional[TreeId] = None
    ) -> "MessageTree[Message]":
        tree: MessageTree = None  # type: ignore
        if root is None:
            root = MessageNode[Message](tree=tree, _message=None, _parent=None, children=[])
        root.tree = MessageTree(root=root)
        if id is not None:
            root.tree.id = id
        return root.tree

    def count_nodes(self) -> int:
        count = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            stack.extend(node.children)
            count += 1
        return count


@dataclass
class MessageTreeTraversal(Generic[Message]):
    node: MessageNode[Message]

    @staticmethod
    def new(node: Optional[MessageNode[Message]] = None) -> "MessageTreeTraversal[Message]":
        if node is None:
            node = MessageTree[Message].new().root
        return MessageTreeTraversal[Message](node)

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
        self.node = self.node.tree.root
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
