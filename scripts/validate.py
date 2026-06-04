import csv
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

EXPECTED_SCHEMAS = {
    "uk_all_1000plus.csv": ["University", "Category", "Email", "QS 2026 Rank"],
    "uk_uni_cs_masters_ranked.csv": [
        "QS 2026 Rank", "University", "Admissions Email", "Website", "Region", "Relevant MSc Programs",
    ],
    "uk_university_admissions_emails.csv": [
        "University", "Admissions Email", "Website", "Region",
    ],
    "germany/de_admissions.csv": ["University", "Category", "Email", "QS 2026 Rank"],
    "germany/de_cs_masters_ranked.csv": [
        "QS 2026 Rank", "University", "Admissions Email", "Website", "State", "Relevant MSc Programs",
    ],
    "germany/de_university_admissions.csv": [
        "University", "Admissions Email", "Website", "State",
    ],
    "norway/no_admissions.csv": ["University", "Category", "Email", "QS 2026 Rank"],
    "norway/no_cs_masters_ranked.csv": [
        "QS 2026 Rank", "University", "Admissions Email", "Website", "City", "Relevant MSc Programs",
    ],
    "norway/no_university_admissions.csv": [
        "University", "Admissions Email", "Website", "City",
    ],
}


def check_file(path: Path, expected_cols: list[str]) -> list[str]:
    errors = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != expected_cols:
            errors.append(f"  Header mismatch: got {reader.fieldnames}, expected {expected_cols}")
            return errors
        for i, row in enumerate(reader, start=2):
            email = (row.get("Email") or row.get("Admissions Email") or "").strip()
            if not EMAIL_PATTERN.match(email):
                errors.append(f"  Line {i}: invalid email {email!r}")
            for key, val in row.items():
                if key and not val.strip():
                    errors.append(f"  Line {i}: empty field {key!r}")
    return errors


def main():
    all_ok = True
    for fname, cols in EXPECTED_SCHEMAS.items():
        path = DATA_DIR / fname
        if not path.exists():
            print(f"[FAIL] {fname} — file not found")
            all_ok = False
            continue
        errors = check_file(path, cols)
        if errors:
            print(f"[FAIL] {fname} — {len(errors)} issue(s):")
            for e in errors:
                print(e)
            all_ok = False
        else:
            print(f"[PASS] {fname}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
