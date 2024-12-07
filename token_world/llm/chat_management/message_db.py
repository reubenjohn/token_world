from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, Iterable, List, NamedTuple, Optional
import sqlite3


from token_world.llm.message_tree import MessageNode, MessageTree, MessageTreeTraversal
from token_world.llm.llm import Message

TreeId = str
MessageNodeId = str

MessageT = Message
MessageNodeT = MessageNode[MessageT]
MessageTreeT = MessageTree[MessageT]
MessageTreeTraversalT = MessageTreeTraversal[MessageT]


class _NodeQueryRow(NamedTuple):
    id: MessageNodeId
    parent_id: Optional[MessageNodeId]
    role: str
    content: str


class TreeReconstructor:
    def __init__(self, tree: MessageTreeT, row_iter: Iterable[_NodeQueryRow]):
        self._row_iter = row_iter
        self._tree = tree
        self._children_map: Dict[Optional[MessageNodeId], List[_NodeQueryRow]] = defaultdict(list)

    def reconstruct(self) -> MessageTreeT:
        for row in self._row_iter:
            self._children_map[row.parent_id].append(row)

        if len(self._children_map) == 0:
            return self._tree

        roots = self._children_map[None]
        if len(roots) != 1:
            raise ValueError(f"No unique root node found. Expected 1, found {len(roots)} roots")
        self._tree.root = self._reconstruct_node(roots[0], None)

        self._reconstruct_children(self._tree.root)

        return self._tree

    def _reconstruct_children(self, root: MessageNodeT):
        stack = [root]
        while stack:
            node = stack.pop()
            children = self._children_map[node.id]
            node.children = [self._reconstruct_node(child, node) for child in children]
            stack.extend(node.children)

    def _reconstruct_node(self, row: _NodeQueryRow, parent: Optional[MessageNodeT]) -> MessageNodeT:
        return MessageNodeT(
            tree=self._tree,
            id=row.id,
            _message={"role": row.role, "content": row.content},
            _parent=parent,
            children=[],
        )


@dataclass
class TreeEntry:
    tree: MessageTreeT
    created_at: datetime


class MessageTreeDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.entries: Dict[TreeId, TreeEntry] = {}
        print(f"Connecting to database at {db_path}")
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self._conn.cursor()
        sqls = """
CREATE TABLE IF NOT EXISTS message_tree (
id TEXT PRIMARY KEY,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS message_node (
id TEXT PRIMARY KEY,
tree_id TEXT,
parent_id TEXT,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
role TEXT,
content TEXT,
FOREIGN KEY (tree_id) REFERENCES message_tree(id),
FOREIGN KEY (parent_id) REFERENCES message_node(id)
);
"""
        cursor.executescript(sqls)

        self._conn.commit()

    def add_tree(self, tree: MessageTreeT):
        if tree.id in self.entries:
            raise ValueError(f"Tree with id {tree.id} already exists")
        entry = TreeEntry(tree=tree, created_at=datetime.now())
        self.entries[tree.id] = entry
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO message_tree (id, created_at) VALUES (?, ?)",
            (entry.tree.id, entry.created_at),
        )
        self._conn.commit()
        self.add_message_node(tree.root)

    def add_message_node(self, node: MessageNodeT):
        if node.tree.id not in self.entries:
            raise ValueError(f"Tree with id {node.tree.id} does not exist")
        cursor = self._conn.cursor()
        if node.is_root():
            role, content = "root", "root"
        else:
            role, content = node.message["role"], node.message["content"]
        cursor.execute(
            """
            INSERT INTO message_node (id, tree_id, parent_id, role, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                node.id,
                node.tree.id,
                None if node.is_root() else node.parent.id,
                role,
                content,
            ),
        )
        self._conn.commit()

    def load(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT count(id) FROM message_tree")
        count = cursor.fetchone()
        logging.info(f"Loading {count[0]} message trees")
        cursor.execute("SELECT id, created_at FROM message_tree")
        for tree_id, created_at in cursor.fetchall():
            entry = TreeEntry(
                tree=MessageTreeT.new(id=tree_id), created_at=datetime.fromisoformat(created_at)
            )
            self._load_tree(entry.tree)
            self.entries[tree_id] = entry

    def _load_tree(self, tree: MessageTreeT) -> MessageTreeT:
        cursor = self._conn.cursor()
        cursor.execute(
            """SELECT id, parent_id, role, content
            FROM message_node
            WHERE tree_id = ?
            ORDER BY created_at""",
            (tree.id,),
        )
        nodes = cursor.fetchall()
        row_iter: Iterable[_NodeQueryRow] = (_NodeQueryRow(*row) for row in nodes)
        tree_reconstructor = TreeReconstructor(tree, row_iter)
        return tree_reconstructor.reconstruct()

    def wipe(self):
        self.entries.clear()
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM message_tree")
        cursor.execute("DELETE FROM message_node")
        self._conn.commit()

    def delete_tree(self, tree: MessageTreeT):
        if tree.id not in self.entries:
            raise ValueError(f"Tree with id {tree.id} does not exist")
        del self.entries[tree.id]
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM message_tree WHERE id = ?", (tree.id,))
        cursor.execute("DELETE FROM message_node WHERE tree_id = ?", (tree.id,))
        self._conn.commit()
