import asyncio
import csv
import re
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_DIR = DATA_DIR / ".cache"

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
ADMISSION_KEYWORDS = re.compile(
    r"admissions?|apply|application|enquiries?|study|international|ug|pgt|pgr|pg|graduate|undergrad|cas|visa|fees?|finance|student.?recruit|hello|contact|info|enquiry",
    re.IGNORECASE,
)

KNOWN_ADMISSIONS_PATHS = [
    "/admissions",
    "/admissions/contact",
    "/study/admissions",
    "/study/applying",
    "/study/contact",
    "/apply",
    "/contact-us",
    "/contact",
    "/about/contact",
    "/international",
    "/international/admissions",
    "/postgraduate/admissions",
    "/undergraduate/admissions",
]


def _admission_score(email: str) -> int:
    """Score how likely an email is an admissions contact (higher = better)."""
    local = email.split("@")[0].lower()
    score = 0
    if "admissions" in local or "admission" in local:
        score += 10
    if "ug" in local or "undergrad" in local:
        score += 3
    if "pgt" in local or "pg" in local or "postgrad" in local or "graduate" in local:
        score += 3
    if "pgr" in local or "phd" in local or "research" in local or "mres" in local:
        score += 3
    if "international" in local or "int" in local:
        score += 4
    if "cas" in local:
        score += 2
    if "fees" in local or "finance" in local:
        score += 1
    if "accommodation" in local:
        score += 1
    if "study" in local:
        score += 2
    if "apply" in local:
        score += 3
    if "hello" in local or "contact" in local or "info" in local or "enquiries" in local:
        score += 1
    return score


def _categorise(email: str) -> str:
    local = email.split("@")[0].lower()
    if "admissions" in local or "admission" in local:
        if "ug" in local and "pgt" not in local and "pgr" not in local:
            return "UG Admissions"
        if "pgt" in local or "postgrad" in local or ("pg" in local and "pgr" not in local):
            return "PGT Admissions"
        if "pgr" in local or "phd" in local or "research" in local:
            return "PGR Admissions"
        if "international" in local or "int" in local:
            return "International Admissions"
        if "cas" in local:
            return "CAS Queries"
        return "General Admissions"
    if "international" in local or "int" in local:
        return "International Admissions"
    if "cas" in local:
        return "CAS Queries"
    if "fees" in local or "finance" in local:
        return "Student Finance"
    if "accommodation" in local or "housing" in local or "residences" in local:
        return "Accommodation"
    if "ug" in local or "undergrad" in local:
        return "UG Admissions"
    if "pgt" in local or "postgrad" in local or "graduate" in local:
        return "PGT Admissions"
    if "pgr" in local or "phd" in local or "research" in local:
        return "PGR Admissions"
    if "computing" in local or "cs" in local or "informatics" in local or "ecs" in local or "eng" in local:
        return "CS/Computing Dept"
    if "study" in local or "apply" in local:
        return "General Admissions"
    if "hello" in local or "contact" in local or "info" in local or "enquiries" in local:
        return "General Enquiries"
    return "Other Admissions"


async def scrape_emails(
    client: httpx.AsyncClient,
    base_url: str,
    uni_name: str,
    timeout: float = 15.0,
) -> list[dict]:
    found = []
    seen = set()

    for path in KNOWN_ADMISSIONS_PATHS:
        url = base_url.rstrip("/") + path
        try:
            resp = await client.get(url, timeout=timeout, follow_redirects=True)
            resp.raise_for_status()
        except Exception:
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        page_text = resp.text

        for match in EMAIL_RE.finditer(page_text):
            email = match.group(0).lower().strip()
            domain = email.split("@")[-1] if "@" in email else ""

            # Skip non-academic / non-institutional
            if not domain.endswith((".ac.uk", ".uk", ".com", ".org")):
                continue
            if any(skip in email for skip in ("example.com", "domain.com", ".png", ".jpg", ".css")):
                continue
            if email in seen:
                continue
            seen.add(email)

            score = _admission_score(email)
            if score == 0:
                continue

            cat = _categorise(email)
            found.append({
                "University": uni_name,
                "Category": cat,
                "Email": email,
                "Score": str(score),
                "Source": url,
            })

    # Sort by relevance score descending, deduplicate by email
    found.sort(key=lambda r: int(r["Score"]), reverse=True)
    deduped = []
    dedup_seen = set()
    for r in found:
        if r["Email"] not in dedup_seen:
            dedup_seen.add(r["Email"])
            deduped.append(r)
    return deduped


def load_known_emails() -> set[str]:
    known = set()
    for f in DATA_DIR.glob("*.csv"):
        with open(f, newline="") as fh:
            for row in csv.DictReader(fh):
                email = (row.get("Email") or row.get("Admissions Email") or "").strip().lower()
                if email:
                    known.add(email)
    return known


async def main():
    import time

    known = load_known_emails()
    print(f"Loaded {len(known)} known emails from dataset")

    # Build a list of (uni_name, website_url) from our dataset
    uni_urls = {}
    for f in DATA_DIR.glob("*.csv"):
        with open(f, newline="") as fh:
            for row in csv.DictReader(fh):
                uni = row.get("University", "").strip()
                url = row.get("Website", "").strip()
                if uni and url:
                    uni_urls[uni] = url.rstrip("/")

    if not uni_urls:
        # Fallback: known websites
        uni_urls = {
            "University of Cambridge": "https://www.cam.ac.uk",
            "University of Oxford": "https://www.ox.ac.uk",
            "Imperial College London": "https://www.imperial.ac.uk",
        }

    print(f"Will scrape {len(uni_urls)} university websites\n")

    headers = {
        "User-Agent": "university-admissions-emails-scraper/1.0 (dataset maintenance; +https://github.com/ghoseyy/university-admissions-emails)",
        "Accept": "text/html,application/xhtml+xml",
    }
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=10)

    all_found = []
    errors = []

    async with httpx.AsyncClient(headers=headers, limits=limits, timeout=20) as client:
        sem = asyncio.Semaphore(5)

        async def scrape_one(uni, url):
            async with sem:
                result = await scrape_emails(client, url, uni)
                return uni, result

        tasks = [scrape_one(uni, url) for uni, url in uni_urls.items()]
        for coro in asyncio.as_completed(tasks):
            uni, result = await coro
            new_count = sum(1 for r in result if r["Email"] not in known)
            print(f"{'✓' if result else ' '} {uni:45s} {len(result):3d} emails found ({new_count} new)")
            all_found.extend(result)

    if not all_found:
        print("\nNo emails scraped — websites may block automated requests.")
        print("Tip: Try running with a slower rate or use the .ac.uk contact pages directly.")
        return

    # Write results
    out_path = DATA_DIR / "uk_scraped_candidates.csv"
    seen_final = set()
    rows = []
    for r in all_found:
        if r["Email"] not in seen_final:
            seen_final.add(r["Email"])
            rows.append(r)

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["University", "Category", "Email", "Score", "Source"])
        writer.writeheader()
        writer.writerows(rows)

    new_emails = [r for r in rows if r["Email"] not in known]
    print(f"\n{'='*60}")
    print(f"Total scraped: {len(rows)} unique emails")
    print(f"New (not in dataset): {len(new_emails)}")
    if new_emails:
        print(f"\nTop new candidates (by relevance score):")
        for r in sorted(new_emails, key=lambda x: int(x["Score"]), reverse=True)[:20]:
            print(f"  [{r['Score']:2d}] {r['Email']:45s} ({r['Category']}) — {r['University']}")
    print(f"\nFull results saved to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
