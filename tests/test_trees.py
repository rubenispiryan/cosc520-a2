"""Correctness and structural-invariant tests for the three trees."""

import random

import pytest

from src.avl_tree import AVLTree
from src.splay_tree import SplayTree
from src.treap import Treap


@pytest.mark.parametrize("factory", [AVLTree, SplayTree, Treap])
def test_membership_duplicates_and_build(factory):
    tree = factory()
    assert tree.size == 0
    assert not tree.contains(4)
    assert tree.insert(4)
    assert not tree.insert(4)
    assert tree.size == 1
    assert tree.contains(4)
    assert not tree.contains(5)
    tree.build([7, -3, 7, 0])
    assert tree.size == 3
    assert all(tree.contains(key) for key in (7, -3, 0))
    assert not tree.contains(4)
    tree.build([])
    assert tree.size == 0
    assert not tree.contains(7)


@pytest.mark.parametrize("factory", [AVLTree, SplayTree, Treap])
@pytest.mark.parametrize("order", ["ascending", "descending", "random"])
def test_matches_set_oracle(factory, order):
    values = list(range(-100, 100))
    if order == "descending":
        values.reverse()
    elif order == "random":
        random.Random(520).shuffle(values)
    tree = factory()
    oracle = set()
    for value in values:
        assert tree.insert(value) == (value not in oracle)
        oracle.add(value)
    assert tree.size == len(oracle)
    for value in range(-110, 110):
        assert tree.contains(value) == (value in oracle)


def _check_avl(node, lower=None, upper=None):
    if node is None:
        return 0
    if lower is not None:
        assert lower < node.key
    if upper is not None:
        assert node.key < upper
    left = _check_avl(node.left, lower, node.key)
    right = _check_avl(node.right, node.key, upper)
    assert abs(left - right) <= 1
    assert node.height == 1 + max(left, right)
    return node.height


@pytest.mark.parametrize("values", [
    [3, 2, 1], [1, 2, 3], [3, 1, 2], [1, 3, 2],
    list(range(500)), list(range(499, -1, -1)),
])
def test_avl_rotations_and_heights(values):
    tree = AVLTree()
    for value in values:
        tree.insert(value)
        _check_avl(tree._root)


def _check_bst(node, lower=None, upper=None):
    if node is None:
        return 0
    if lower is not None:
        assert lower < node.key
    if upper is not None:
        assert node.key < upper
    return 1 + _check_bst(node.left, lower, node.key) + _check_bst(node.right, node.key, upper)


def test_splay_moves_accessed_key_to_root():
    tree = SplayTree()
    tree.build([5, 2, 8, 1, 3, 7, 9])
    assert tree.contains(2)
    assert tree._root.key == 2
    assert not tree.contains(6)
    assert _check_bst(tree._root) == tree.size
    assert tree.contains(9)
    assert tree._root.key == 9
    assert _check_bst(tree._root) == tree.size


def test_splay_preserves_bst_after_many_accesses():
    tree = SplayTree()
    values = list(range(500))
    random.Random(18).shuffle(values)
    tree.build(values)
    rng = random.Random(19)
    queries = [rng.randrange(-100, 600) for _ in range(200)]
    for index, key in enumerate(queries):
        assert tree.contains(key) == (0 <= key < 500)
        if index % 20 == 0:
            assert _check_bst(tree._root) == 500


def _check_treap(node, lower=None, upper=None):
    if node is None:
        return 0
    if lower is not None:
        assert lower < node.key
    if upper is not None:
        assert node.key < upper
    if node.left is not None:
        assert node.priority <= node.left.priority
    if node.right is not None:
        assert node.priority <= node.right.priority
    return 1 + _check_treap(node.left, lower, node.key) + _check_treap(node.right, node.key, upper)


def test_treap_heap_order_and_seed_reproducibility():
    values = list(range(400))
    random.Random(30).shuffle(values)
    first = Treap(seed=42)
    second = Treap(seed=42)
    first.build(values)
    second.build(values)
    assert _check_treap(first._root) == len(values)
    assert _check_treap(second._root) == len(values)
    assert _treap_priorities(first._root) == _treap_priorities(second._root)
    first.insert(values[0])  # Duplicate insertion must not consume a priority.
    assert first.insert(1000)
    assert second.insert(1000)
    assert _treap_priorities(first._root) == _treap_priorities(second._root)


def _treap_priorities(node):
    if node is None:
        return {}
    priorities = _treap_priorities(node.left)
    priorities[node.key] = node.priority
    priorities.update(_treap_priorities(node.right))
    return priorities
