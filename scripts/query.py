import csv
import sys
import shutil
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def pick_file() -> Path:
    return DATA_DIR / "uk_all_1000plus.csv"


def read(file: Path) -> list[dict]:
    with open(file, newline="") as f:
        return list(csv.DictReader(f))


def fmt(rows: list[dict], cols: Optional[list[str]] = None):
    if not rows:
        print("No results.")
        return
    if cols is None:
        cols = list(rows[0].keys())
    col_widths = {c: max(len(c), max(len(r[c]) for r in rows)) for c in cols}
    sep = "  "
    header = sep.join(c.ljust(col_widths[c]) for c in cols)
    print(header)
    print("-" * len(header))
    for r in rows:
        print(sep.join(r[c].ljust(col_widths[c]) for c in cols))


def main():
    file = pick_file()
    if not file.exists():
        print(f"Data file not found: {file}", file=sys.stderr)
        return 1

    rows = read(file)

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/query.py <search-term>")
        print()
        fmt(rows[:10], ["University", "Category", "Email", "QS 2026 Rank"])
        print(f"\nShowing 10 of {len(rows)} entries. Provide a search term to filter.")
        return 0

    q = sys.argv[1].lower()
    matched = [r for r in rows if q in r["University"].lower() or q in r["Category"].lower() or q in r["Email"].lower()]

    fmt(matched, ["University", "Category", "Email", "QS 2026 Rank"])
    print(f"\n{len(matched)} result(s) for {q!r} (of {len(rows)} total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
