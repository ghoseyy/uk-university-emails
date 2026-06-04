# UK University Admissions Emails Dataset

A comprehensive, structured dataset of UK university admissions contact emails, ranked by **QS World University Rankings 2026**.

## Datasets

| File | Entries | Description |
|------|---------|-------------|
| `data/uk_all_1000plus.csv` | **1,293** | Full dataset: UG/PGT/PGR/International/CS dept/CAS/Finance admissions emails per university, QS-ranked |
| `data/uk_uni_cs_masters_ranked.csv` | **124** | Filtered: universities offering MSc in CS/AI/ML/Cyber Security, ranked |
| `data/uk_university_admissions_emails.csv` | **162** | Quick reference: one primary admissions email per UK university |

## Features

- **QS 2026 World Rankings** included for every institution
- **Multiple contact categories** per university: General, UG, PGT, PGR, CS Dept, Engineering, International, CAS, Finance, Accommodation
- **MSc programme coverage** noted for CS, AI, ML, Cyber Security, Data Science, Computer Vision
- **Region-tagged**: England, Scotland, Wales, Northern Ireland
- **Verified domains**: all emails use official `ac.uk` (or institutional) domains

## Schema

### `uk_all_1000plus.csv`
```
University, Category, Email, QS 2026 Rank
```

### `uk_uni_cs_masters_ranked.csv`
```
QS 2026 Rank, University, Admissions Email, Website, Region, Relevant MSc Programs
```

### `uk_university_admissions_emails.csv`
```
University, Admissions Email, Website, Region
```

## Data Sources

- **QS World University Rankings 2026** (`topuniversities.com`)
- **UCAS** (official UK university list)
- Individual university websites (verified admissions contact pages)
- Official `.ac.uk` domain registry

## Usage (uv)

This project uses [uv](https://docs.astral.sh/uv/) — the fast Python package and project manager.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Query the dataset

```bash
# Clone
git clone https://github.com/bimqllabs/uk-university-emails.git
cd uk-university-emails

# Search for a university or keyword
uv run scripts/query.py cambridge

# Search by category
uv run scripts/query.py "CS Dept"

# Search by email domain
uv run scripts/query.py "ac.uk"

# Validate all emails
uv run scripts/validate.py
```

### Install dependencies & use interactively

```bash
uv sync
uv run python -c "
import csv
with open('data/uk_all_1000plus.csv') as f:
    for row in csv.DictReader(f):
        print(f\"{row['University']:40s} {row['Category']:25s} {row['Email']}\")
"
```

### Use csvkit for quick analysis

```bash
uv run csvstat data/uk_all_1000plus.csv
uv run csvcut -c University,Email data/uk_all_1000plus.csv | uv run csvlook
```

## Licence

This project is licensed under the **MIT License** — see [LICENSE](LICENSE).

## Contributing

Contributions are welcome! Please read [CONTRIBUTING](CONTRIBUTING.md) first.

- **Add missing emails** — submit a PR with your additions
- **Report broken emails** — open an issue
- **Suggest new categories** — start a discussion

## Disclaimer

Email addresses were collected from publicly available university websites and FOI disclosure logs. Addresses may change over time. Please verify before using for critical communications. This dataset is intended for legitimate educational outreach and research purposes only.
