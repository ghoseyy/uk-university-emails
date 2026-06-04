# University Admissions Emails Dataset

A comprehensive, structured dataset of **UK**, **German**, and **Norwegian** university admissions contact emails, ranked by **QS World University Rankings 2026**.

## Datasets

### United Kingdom

| File | Entries | Description |
|------|---------|-------------|
| `data/uk_all_1000plus.csv` | **1,293** | Full dataset: UG/PGT/PGR/International/CS dept/CAS/Finance admissions emails per university, QS-ranked |
| `data/uk_uni_cs_masters_ranked.csv` | **124** | Filtered: UK universities offering MSc in CS/AI/ML/Cyber Security, ranked |
| `data/uk_university_admissions_emails.csv` | **162** | Quick reference: one primary admissions email per UK university |

### Germany

| File | Entries | Description |
|------|---------|-------------|
| `data/germany/de_admissions.csv` | **671** | Full dataset: Studienberatung/Bachelor/Master/PhD/International/CS dept/Finance/Accommodation contacts per university, QS-ranked |
| `data/germany/de_cs_masters_ranked.csv` | **61** | Filtered: German universities offering CS/AI/ML/Data Science MSc programmes, ranked |
| `data/germany/de_university_admissions.csv` | **61** | Quick reference: one primary admissions email per German university |

### Norway

| File | Entries | Description |
|------|---------|-------------|
| `data/norway/no_admissions.csv` | **200** | Full dataset: Study/Admissions/Bachelor/Master/PhD/International/CS dept/Housing/Finance contacts per university, QS-ranked |
| `data/norway/no_cs_masters_ranked.csv` | **20** | Filtered: Norwegian universities offering CS/AI/Data Science MSc programmes, ranked |
| `data/norway/no_university_admissions.csv` | **20** | Quick reference: one primary admissions email per Norwegian university |

## Schema

### Multi-category files (`uk_all_1000plus.csv`, `de_admissions.csv`)
```
University, Category, Email, QS 2026 Rank
```

### CS Masters filtered (`uk_uni_cs_masters_ranked.csv`, `de_cs_masters_ranked.csv`)
```
QS 2026 Rank, University, Admissions Email, Website, Region/State, Relevant MSc Programs
```

### Quick reference (`uk_university_admissions_emails.csv`, `de_university_admissions.csv`)
```
University, Admissions Email, Website, Region/State
```

## Data Sources

- **QS World University Rankings 2026** (`topuniversities.com`)
- **UCAS** (official UK university list)
- **Hochschulkompass** and individual German university websites
- Individual university websites (verified admissions contact pages)
- Official `.ac.uk` and `.de` domain registries
- **Web scraping** — `scripts/scrape.py` crawls university contact pages to discover and verify admissions emails

## How emails were collected

The initial dataset was compiled through:
1. Web research across official university websites
2. Known email patterns (`admissions@*.ac.uk`, `studium@uni-*.de`, etc.)
3. FOI disclosure logs and public contact directories
4. The `scripts/scrape.py` tool can be re-run to verify existing emails and discover new ones

To re-scrape and verify:

```bash
uv run scripts/scrape.py
```

This crawls each university's admissions/contact pages and scores extracted emails by relevance. Results are saved for review before merging.

## Usage (uv)

This project uses [uv](https://docs.astral.sh/uv/) — the fast Python package and project manager.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Query the UK dataset

```bash
# Clone
git clone https://github.com/ghoseyy/uk-university-emails.git
cd uk-university-emails

# Search for a university or keyword
uv run scripts/query.py cambridge

# Search by category
uv run scripts/query.py "CS Dept"

# Search by country (Germany)
uv run scripts/query.py "studium@" data/germany/de_admissions.csv
```

### Query the German dataset

```bash
uv run scripts/query.py "TUM" data/germany/de_admissions.csv
uv run scripts/query.py "Informatik" data/germany/de_cs_masters_ranked.csv
```

### Validate all emails

```bash
uv run scripts/validate.py
```

### Use csvkit for quick analysis

```bash
uv run csvstat data/uk_all_1000plus.csv
uv run csvstat data/germany/de_admissions.csv
uv run csvcut -c University,Email data/germany/de_university_admissions.csv | uv run csvlook
```

## Licence

This project is licensed under the **MIT License** — see [LICENSE](LICENSE).

## Contributing

Contributions are welcome! Please read [CONTRIBUTING](CONTRIBUTING.md) first.

- **Add missing emails** — submit a PR with your additions
- **Report broken emails** — open an issue
- **Suggest new categories or countries** — start a discussion

## Disclaimer

Email addresses were collected from publicly available university websites and FOI disclosure logs. Addresses may change over time. Please verify before using for critical communications. This dataset is intended for legitimate educational outreach and research purposes only.
