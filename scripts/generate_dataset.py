"""Write an uploadable compressed copy of the deterministic benchmark dataset."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import platform

from src.dataset import make_keys


def main() -> None:
    """Parse CLI options and write the integer dataset plus its manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=520)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    if not 1 <= args.n <= 10_000_000:
        parser.error("--n must be between 1 and 10,000,000")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / f"keys_n{args.n}_seed{args.seed}.txt.gz"
    manifest_path = args.output_dir / f"keys_n{args.n}_seed{args.seed}.json"
    if path.exists() or manifest_path.exists():
        parser.error("output already exists; choose another size/seed or remove it explicitly")

    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0,
                           compresslevel=6) as output:
            for key in make_keys(args.n, args.seed):
                output.write(f"{key}\n".encode("ascii"))
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    manifest = {
        "n": args.n,
        "seed": args.seed,
        "python": platform.python_version(),
        "generation": "random.Random(seed).shuffle(array('I', range(0, 2*n, 2)))",
        "queries": "seeded 50/50 mix of present even keys and absent odd keys in [0, 2n)",
        "file": path.name,
        "sha256": digest.hexdigest(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path} and {manifest_path}")


if __name__ == "__main__":
    main()
