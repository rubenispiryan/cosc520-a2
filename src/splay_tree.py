"""Splay tree: every lookup moves its last visited node to the root."""

from collections.abc import Iterable


class _Node:
    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        """Create a leaf holding ``key``; return nothing."""
        self.key = key
        self.left: _Node | None = None
        self.right: _Node | None = None


def _splay(root: _Node, key: int) -> _Node:
    """Return the root after searching for ``key`` with top-down splaying."""
    header = _Node(0)
    left_tail = header
    right_tail = header

    while True:
        if key < root.key:
            if root.left is None:
                break
            if key < root.left.key:  # A left-left access needs a right rotation.
                pivot = root.left
                root.left = pivot.right
                pivot.right = root
                root = pivot
                if root.left is None:
                    break
            right_tail.left = root
            right_tail = root
            root = root.left
        elif key > root.key:
            if root.right is None:
                break
            if key > root.right.key:  # A right-right access needs a left rotation.
                pivot = root.right
                root.right = pivot.left
                pivot.left = root
                root = pivot
                if root.right is None:
                    break
            left_tail.right = root
            left_tail = root
            root = root.right
        else:
            break

    left_tail.right = root.left
    right_tail.left = root.right
    root.left = header.right
    root.right = header.left
    return root


class SplayTree:
    """Store unique integer keys with amortized O(log n) operations."""

    def __init__(self) -> None:
        """Create an empty splay tree; return nothing."""
        self._root: _Node | None = None
        self.size = 0

    def build(self, keys: Iterable[int]) -> None:
        """Replace the tree with the unique keys from ``keys``; return nothing."""
        self._root = None
        self.size = 0
        for key in keys:
            self.insert(key)

    def insert(self, key: int) -> bool:
        """Insert ``key`` and splay it to the root; return whether it was new."""
        if self._root is None:
            self._root = _Node(key)
            self.size = 1
            return True
        root = _splay(self._root, key)
        if key == root.key:
            self._root = root
            return False
        new_root = _Node(key)
        if key < root.key:
            new_root.left = root.left
            new_root.right = root
            root.left = None
        else:
            new_root.left = root
            new_root.right = root.right
            root.right = None
        self._root = new_root
        self.size += 1
        return True

    def contains(self, key: int) -> bool:
        """Return whether ``key`` is present, splaying the last visited node."""
        if self._root is None:
            return False
        self._root = _splay(self._root, key)
        return self._root.key == key
