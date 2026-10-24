# COSC 520 Assignment 2: Advanced Search Trees

This project compares three self-implemented ordered search trees: an AVL tree, a splay tree, and a treap. Each supports insertion and membership lookup for unique integer keys. No library tree implementation is used.

## Setup

Use Python 3.10 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

From the repository root:

```sh
python -m pytest -q
python -m scripts.benchmark --profile quick --prefix quick_example
python -m scripts.benchmark --profile full --prefix my_full_run
python -m scripts.plot_results --input results/my_full_run_summary.csv --prefix my_full_run
python -m scripts.generate_dataset --n 10000000 --seed 520
```

The full profile measures `n = 1,000, 10,000, 100,000, 1,000,000, 10,000,000` for all three trees. It runs three independently built trials per tree and size, with 20,000 membership queries per trial. Use `--sizes`, `--queries`, and `--repetitions` to change the workload. The full run may take tens of minutes and needs substantial RAM. The scripts refuse to overwrite an existing output prefix.

For each `n`, a seeded shuffle of the **even** integers `0, 2, ..., 2n-2` produces one common insertion order. The same seeded query list is used by all trees: half present even keys and half absent odd keys, interleaved across the same range. Dataset generation occurs before timing. Each trial builds a fresh tree; build time and lookup time are measured separately. This also resets the splay tree, whose lookups change its shape.

The dataset uses seed 520 by default; treap priorities use seed 521 so their random stream is separate from the insertion-order shuffle.
Method order rotates across the three trials so each tree runs first, second, and third once at each size.

`results/` contains raw trial CSVs, median summary CSVs, and reproducibility metadata. `plots/` contains PNG and PDF figures. `data/` contains the concrete compressed dataset and a JSON manifest with its SHA-256 checksum. To regenerate that dataset, run the command above with seed 520; use a different output directory or remove the existing copy first. The dataset is included in this repository.

To regenerate the included final plots from the saved CSV:

```sh
python -m scripts.plot_results --input results/final_20261023_seed520_rotated_summary.csv --prefix final
```

## Files

- `src/avl_tree.py`: height-balanced BST, worst-case `O(log n)` lookup and insertion.
- `src/splay_tree.py`: self-adjusting BST, amortized `O(log n)` operations; a single operation can be `O(n)`.
- `src/treap.py`: BST with seeded random priorities, expected `O(log n)` operations.
- `src/dataset.py`: compact seeded key and query workloads.
- `scripts/`: dataset export, benchmark, and plotting commands.
- `tests/`: correctness, invariant, and benchmark smoke tests.
