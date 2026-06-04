# Contributing to UK University Emails Dataset

Thanks for your interest in contributing! This project thrives on community updates to keep email addresses current.

## Project Setup (uv)

This project uses [uv](https://docs.astral.sh/uv/) for Python project management.

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/uk-university-emails.git
cd uk-university-emails

# Sync dependencies
uv sync

# Validate your changes
uv run scripts/validate.py
```

## How to Contribute

### 1. Add or Update Emails

- Fork the repo
- Edit the relevant CSV file(s) in `data/`
- Follow the existing schema (same columns, quote all fields)
- Use the official university `.ac.uk` domain where possible
- Include the QS 2026 rank if known (use `N/A` if unranked)
- Run `uv run scripts/validate.py` to verify your changes

### 2. Report Issues

Open an issue for:
- Broken/returned email addresses
- Missing universities
- Incorrect QS rankings
- New category suggestions

### 3. Submit a Pull Request

1. Create a feature branch: `git checkout -b add-uni-emails`
2. Commit your changes with a clear message
3. Push to your fork and open a PR

### Format Rules

- All fields must be quoted: `"University Name","Category","email@ac.uk","Rank"`
- No trailing whitespace
- One entry per line
- Deduplicate — check if the email already exists for that category

### Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and collaborative.

## Questions?

Open a discussion or issue — we're happy to help.
