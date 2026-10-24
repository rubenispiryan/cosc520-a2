"""Reproducibility checks for the dataset and measured workload."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.benchmark import run_trial
from src.dataset import make_keys, make_queries


def test_dataset_is_unique_reproducible_and_interleaved():
    first = list(make_keys(101, 520))
    assert first == list(make_keys(101, 520))
    assert set(first) == set(range(0, 202, 2))
    assert first != list(make_keys(101, 521))
    assert list(make_keys(1, 520)) == [0]


def test_queries_have_known_membership_and_seed():
    queries, positives = make_queries(101, 11, 520)
    assert positives == 5
    assert sum(key % 2 == 0 for key in queries) == positives
    assert all(0 <= key < 202 for key in queries)
    assert (queries, positives) == make_queries(101, 11, 520)


def test_parameter_validation():
    with pytest.raises(ValueError):
        make_keys(0, 520)
    with pytest.raises(ValueError):
        make_queries(1, 1, 520)


def test_exported_dataset_is_byte_reproducible(tmp_path):
    root = Path(__file__).resolve().parents[1]
    outputs = []
    for name in ("first", "second"):
        folder = tmp_path / name
        subprocess.run(
            [sys.executable, "-m", "scripts.generate_dataset", "--n", "101",
             "--seed", "520", "--output-dir", str(folder)],
            cwd=root, check=True, capture_output=True,
        )
        outputs.append(folder)
    dataset_name = "keys_n101_seed520.txt.gz"
    assert (outputs[0] / dataset_name).read_bytes() == (outputs[1] / dataset_name).read_bytes()
    manifest = json.loads((outputs[0] / "keys_n101_seed520.json").read_text())
    assert manifest["n"] == 101
    assert len(manifest["sha256"]) == 64


@pytest.mark.parametrize("name", ["avl", "splay", "treap"])
def test_smoke_trial(name):
    queries, positives = make_queries(100, 200, 521)
    row = run_trial(name, make_keys(100, 520), 520, queries, positives)
    assert row["status"] == "ok"
    assert row["size"] == 100
    assert row["query_count"] == 200
    assert row["build_ns"] > 0
    assert row["lookup_ns"] > 0
