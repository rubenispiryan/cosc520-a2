"""Plot measured build and lookup times from a benchmark summary CSV."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LABELS = {"avl": "AVL tree", "splay": "Splay tree", "treap": "Treap"}


def plot_metric(rows: list[dict], field: str, scale: float, ylabel: str,
                title: str, output: Path, log_y: bool) -> None:
    """Plot one measured metric by data size and save PNG and PDF copies."""
    fig, axis = plt.subplots(figsize=(7.2, 4.8))
    for name, label in LABELS.items():
        points = sorted(
            ((int(row["n"]), float(row[field]) * scale) for row in rows
             if row["algorithm"] == name and row["status"] == "ok")
        )
        if points:
            axis.plot([x for x, _ in points], [y for _, y in points],
                      marker="o", linewidth=1.8, label=label)
    axis.set_xscale("log")
    if log_y:
        axis.set_yscale("log")
    axis.set_title(title)
    axis.set_xlabel("Number of stored keys (n)")
    axis.set_ylabel(ylabel)
    axis.grid(True, which="both", alpha=0.25)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output.with_suffix(".png"), dpi=180)
    fig.savefig(output.with_suffix(".pdf"))
    plt.close(fig)


def main() -> None:
    """Read the selected summary CSV and write report-ready plots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("plots"))
    parser.add_argument("--prefix", default="final")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        parser.error("input CSV has no measurements")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_metric(rows, "median_build_ns", 1e-9, "Median build time (seconds)",
                "Tree construction time", args.output_dir / f"{args.prefix}_build", True)
    plot_metric(rows, "median_ns_per_query", 1e-3, "Median lookup time (microseconds/query)",
                "Membership lookup time", args.output_dir / f"{args.prefix}_lookup_log", True)
    plot_metric(rows, "median_ns_per_query", 1e-3, "Median lookup time (microseconds/query)",
                "Membership lookup time", args.output_dir / f"{args.prefix}_lookup_linear", False)
    print(f"Saved PNG and PDF plots in {args.output_dir}")


if __name__ == "__main__":
    main()
