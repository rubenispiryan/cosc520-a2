"""Treap: binary-search ordering on keys and heap ordering on priorities."""

from collections.abc import Iterable
import random


class _Node:
    __slots__ = ("key", "priority", "left", "right")

    def __init__(self, key: int, priority: int) -> None:
        """Create a leaf with ``key`` and ``priority``; return nothing."""
        self.key = key
        self.priority = priority
        self.left: _Node | None = None
        self.right: _Node | None = None


def _rotate_left(node: _Node) -> _Node:
    """Rotate ``node`` left and return the new subtree root."""
    pivot = node.right
    assert pivot is not None
    node.right = pivot.left
    pivot.left = node
    return pivot


def _rotate_right(node: _Node) -> _Node:
    """Rotate ``node`` right and return the new subtree root."""
    pivot = node.left
    assert pivot is not None
    node.left = pivot.right
    pivot.right = node
    return pivot


class Treap:
    """Store unique integer keys with expected O(log n) operations."""

    def __init__(self, seed: int = 520) -> None:
        """Create an empty treap with deterministic ``seed``; return nothing."""
        self.seed = seed
        self._random = random.Random(seed)
        self._root: _Node | None = None
        self.size = 0

    def build(self, keys: Iterable[int]) -> None:
        """Replace the tree with the unique keys from ``keys``; return nothing."""
        self._root = None
        self.size = 0
        self._random.seed(self.seed)
        for key in keys:
            self.insert(key)

    def insert(self, key: int) -> bool:
        """Insert ``key`` with a seeded priority; return whether it was new."""
        old_size = self.size
        self._root = self._insert(self._root, key)
        return self.size != old_size

    def _insert(self, node: _Node | None, key: int) -> _Node:
        """Insert ``key`` below ``node`` and return the heap-ordered root."""
        if node is None:
            self.size += 1
            return _Node(key, self._random.getrandbits(64))
        if key < node.key:
            node.left = self._insert(node.left, key)
            if node.left.priority < node.priority:
                return _rotate_right(node)
        elif key > node.key:
            node.right = self._insert(node.right, key)
            if node.right.priority < node.priority:
                return _rotate_left(node)
        return node

    def contains(self, key: int) -> bool:
        """Return whether ``key`` is stored in the tree."""
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return True
        return False
