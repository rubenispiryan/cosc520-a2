"""Compare construction and membership lookup in three advanced search trees."""

import argparse
import csv
import gc
import json
from pathlib import Path
import platform
from statistics import median
from time import perf_counter_ns

from src.avl_tree import AVLTree
from src.dataset import make_keys, make_queries
from src.splay_tree import SplayTree
from src.treap import Treap


ALGORITHMS = ("avl", "splay", "treap")
SIZES = {
    "quick": (1_000, 10_000),
    "full": (1_000, 10_000, 100_000, 1_000_000, 10_000_000),
}
RAW_FIELDS = (
    "algorithm", "n", "trial", "seed", "query_count", "positive_queries",
    "negative_queries", "build_ns", "lookup_ns", "ns_per_query", "size", "status",
)
SUMMARY_FIELDS = (
    "algorithm", "n", "trials", "seed", "query_count", "positive_queries",
    "negative_queries", "median_build_ns", "median_lookup_ns",
    "median_ns_per_query", "status",
)


def new_tree(name: str, seed: int):
    """Return a fresh tree selected by ``name`` and seeded where needed."""
    if name == "avl":
        return AVLTree()
    if name == "splay":
        return SplayTree()
    if name == "treap":
        return Treap(seed + 1)  # Separate priority stream from the dataset shuffle.
    raise ValueError(f"unknown algorithm: {name}")


def run_trial(name: str, keys, seed: int, queries: list[int], positives: int) -> dict:
    """Build one tree, time one query batch, and return genuine measurements."""
    n = len(keys)
    gc.collect()
    tree = new_tree(name, seed)
    gc.disable()
    try:
        start = perf_counter_ns()
        tree.build(keys)
        build_ns = perf_counter_ns() - start
        if tree.size != n:
            raise AssertionError(f"{name}: built {tree.size} keys, expected {n}")
        start = perf_counter_ns()
        found = sum(tree.contains(key) for key in queries)
        lookup_ns = perf_counter_ns() - start
        if found != positives:
            raise AssertionError(f"{name}: found {found} positive queries, expected {positives}")
        for key in queries:
            if tree.contains(key) != (key % 2 == 0):
                raise AssertionError(f"{name}: incorrect membership answer for {key}")
        return {
            "algorithm": name,
            "n": n,
            "seed": seed,
            "query_count": len(queries),
            "positive_queries": positives,
            "negative_queries": len(queries) - positives,
            "build_ns": build_ns,
            "lookup_ns": lookup_ns,
            "ns_per_query": lookup_ns / len(queries),
            "size": tree.size,
            "status": "ok",
        }
    finally:
        gc.enable()
        del tree
        gc.collect()


def summarize(rows: list[dict], seed: int) -> list[dict]:
    """Return medians for each algorithm and size from completed raw trials."""
    summary = []
    for n in sorted({int(row["n"]) for row in rows}):
        for name in ALGORITHMS:
            group = [row for row in rows if row["algorithm"] == name and int(row["n"]) == n]
            if not group:
                continue
            first = group[0]
            summary.append({
                "algorithm": name,
                "n": n,
                "trials": len(group),
                "seed": seed,
                "query_count": first["query_count"],
                "positive_queries": first["positive_queries"],
                "negative_queries": first["negative_queries"],
                "median_build_ns": median(row["build_ns"] for row in group),
                "median_lookup_ns": median(row["lookup_ns"] for row in group),
                "median_ns_per_query": median(row["ns_per_query"] for row in group),
                "status": "ok",
            })
    return summary


def main() -> None:
    """Run the selected benchmark profile and save raw, summary, and metadata files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=SIZES, default="quick")
    parser.add_argument("--sizes", type=int, nargs="+", help="override profile sizes")
    parser.add_argument("--seed", type=int, default=520)
    parser.add_argument("--queries", type=int, default=20_000)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--prefix", help="output prefix; defaults to profile and seed")
    args = parser.parse_args()
    sizes = sorted(set(args.sizes or SIZES[args.profile]))
    if not sizes or sizes[0] < 1 or sizes[-1] > 10_000_000:
        parser.error("sizes must be between 1 and 10,000,000")
    if args.queries < 2 or args.repetitions < 1:
        parser.error("queries must be at least 2 and repetitions at least 1")
    prefix = args.prefix or f"{args.profile}_seed{args.seed}"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.output_dir / f"{prefix}_raw.csv"
    summary_path = args.output_dir / f"{prefix}_summary.csv"
    metadata_path = args.output_dir / f"{prefix}_metadata.json"
    if any(path.exists() for path in (raw_path, summary_path, metadata_path)):
        parser.error("output already exists; choose another --prefix or remove it explicitly")

    rows = []
    with raw_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=RAW_FIELDS)
        writer.writeheader()
        for n in sizes:
            keys = make_keys(n, args.seed)
            queries, positives = make_queries(n, args.queries, args.seed + n)
            for trial in range(1, args.repetitions + 1):
                offset = (trial - 1) % len(ALGORITHMS)
                order = ALGORITHMS[offset:] + ALGORITHMS[:offset]
                for name in order:
                    row = run_trial(name, keys, args.seed, queries, positives)
                    row["trial"] = trial
                    writer.writerow(row)
                    output.flush()
                    rows.append(row)
                    print(f"n={n:,} {name} trial={trial}: build={row['build_ns']/1e9:.2f}s, "
                          f"lookup={row['ns_per_query']:.1f} ns/query", flush=True)
            del keys

    with summary_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summarize(rows, args.seed))
    metadata = {
        "algorithms": list(ALGORITHMS),
        "sizes": sizes,
        "seed": args.seed,
        "treap_priority_seed": args.seed + 1,
        "query_seed": "seed + n",
        "queries_per_trial": args.queries,
        "positive_queries_per_trial": args.queries // 2,
        "repetitions": args.repetitions,
        "method_order": "rotated across trials to reduce run-order bias",
        "dataset": "n unique even integers shuffled by random.Random(seed); odd integers absent",
        "lookup_timing": "dataset generation and construction excluded; each trial uses a fresh tree",
        "python": platform.python_version(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {raw_path}, {summary_path}, and {metadata_path}")


if __name__ == "__main__":
    main()
