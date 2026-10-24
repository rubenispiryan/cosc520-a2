"""Deterministic shuffled integer workloads shared by all three trees."""

from array import array
import random


def make_keys(n: int, seed: int) -> array:
    """Return n unique even keys in seeded shuffled order using four bytes per key."""
    if n < 1 or n > 10_000_000:
        raise ValueError("n must be between 1 and 10,000,000")
    keys = array("I", range(0, 2 * n, 2))
    random.Random(seed).shuffle(keys)
    return keys


def make_queries(n: int, count: int, seed: int) -> tuple[list[int], int]:
    """Return shuffled 50/50 present/absent keys and the positive count."""
    if n < 1 or count < 2:
        raise ValueError("n must be positive and count must be at least 2")
    rng = random.Random(seed)
    positives = count // 2
    queries = [2 * rng.randrange(n) for _ in range(positives)]
    queries.extend(2 * rng.randrange(n) + 1 for _ in range(count - positives))
    rng.shuffle(queries)
    return queries, positives
