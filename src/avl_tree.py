"""AVL tree: a binary search tree with height-balanced nodes."""

from collections.abc import Iterable


class _Node:
    __slots__ = ("key", "left", "right", "height")

    def __init__(self, key: int) -> None:
        """Create a leaf holding ``key``; return nothing."""
        self.key = key
        self.left: _Node | None = None
        self.right: _Node | None = None
        self.height = 1


def _height(node: _Node | None) -> int:
    """Return ``node``'s stored height, or zero for an empty subtree."""
    return 0 if node is None else node.height


def _rotate_left(node: _Node) -> _Node:
    """Rotate ``node`` left and return the new subtree root."""
    pivot = node.right
    assert pivot is not None
    node.right = pivot.left
    pivot.left = node
    node.height = 1 + max(_height(node.left), _height(node.right))
    pivot.height = 1 + max(_height(pivot.left), _height(pivot.right))
    return pivot


def _rotate_right(node: _Node) -> _Node:
    """Rotate ``node`` right and return the new subtree root."""
    pivot = node.left
    assert pivot is not None
    node.left = pivot.right
    pivot.right = node
    node.height = 1 + max(_height(node.left), _height(node.right))
    pivot.height = 1 + max(_height(pivot.left), _height(pivot.right))
    return pivot


class AVLTree:
    """Store unique integer keys with O(log n) worst-case lookup and insertion."""

    def __init__(self) -> None:
        """Create an empty AVL tree; return nothing."""
        self._root: _Node | None = None
        self.size = 0

    def build(self, keys: Iterable[int]) -> None:
        """Replace the tree with the unique keys from ``keys``; return nothing."""
        self._root = None
        self.size = 0
        for key in keys:
            self.insert(key)

    def insert(self, key: int) -> bool:
        """Insert ``key``; return True if it was new, otherwise False."""
        old_size = self.size
        self._root = self._insert(self._root, key)
        return self.size != old_size

    def _insert(self, node: _Node | None, key: int) -> _Node:
        """Insert ``key`` below ``node`` and return the rebalanced root."""
        if node is None:
            self.size += 1
            return _Node(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node

        node.height = 1 + max(_height(node.left), _height(node.right))
        balance = _height(node.left) - _height(node.right)
        if balance > 1:
            assert node.left is not None
            if key > node.left.key:
                node.left = _rotate_left(node.left)
            return _rotate_right(node)
        if balance < -1:
            assert node.right is not None
            if key < node.right.key:
                node.right = _rotate_right(node.right)
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
