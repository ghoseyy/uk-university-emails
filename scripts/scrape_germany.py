import asyncio
import csv
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "germany"
OUT_DIR = DATA_DIR.parent

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

GERMAN_KEYWORDS = re.compile(
    r"studium|bewerbung|zulassung|promotion|international"
    r"|studienberatung|studierendensekretariat|kontakt|info"
    r"|admissions|apply|application|enquiries|study|graduate|phd"
    r"|campus|service|beratung|prüfungsamt|auslandsamt",
    re.IGNORECASE,
)

KNOWN_PATHS = [
    "/impressum",
    "/studium",
    "/bewerbung",
    "/studieninteressierte",
    "/studienberatung",
    "/studierendensekretariat",
    "/promotion",
    "/international",
    "/international-office",
    "/kontakt",
    "/service",
    "/studium/bewerbung",
    "/studium/studienangebot",
    "/campus",
    "/ueber-uns/kontakt",
]


def _admission_score(email: str) -> int:
    local = email.split("@")[0].lower()
    domain = email.split("@")[-1].lower() if "@" in email else ""
    score = 0

    if "studium" in local:
        score += 8
    if "bewerbung" in local or "apply" in local:
        score += 9
    if "zulassung" in local or "admissions" in local:
        score += 10
    if "promotion" in local or "phd" in local:
        score += 5
    if "international" in local:
        score += 6
    if "studienberatung" in local:
        score += 7
    if "studierendensekretariat" in local or "campus" in local:
        score += 4
    if "info" in local:
        score += 2
    if "kontakt" in local or "contact" in local:
        score += 2
    if "service" in local:
        score += 3
    if "master" in local:
        score += 4
    if "bachelor" in local:
        score += 4
    if "beratung" in local:
        score += 4
    if "auslands" in local or "international" in local:
        score += 4
    if "pruefungs" in local or "examination" in local:
        score += 2
    if "stud" in local:
        score += 1
    if "sekretariat" in local:
        score += 2

    if domain.endswith((".de", ".eu")):
        score += 1

    return score


def _categorise(email: str) -> str:
    local = email.split("@")[0].lower()

    if "bewerbung" in local or "zulassung" in local:
        if "master" in local:
            return "Bewerbung Master"
        if "bachelor" in local:
            return "Bewerbung Bachelor"
        if "international" in local:
            return "International Office"
        return "Bewerbung/Zulassung"
    if "promotion" in local or "phd" in local:
        return "Promotion/PhD"
    if "international" in local or "auslands" in local:
        return "International Office"
    if "studienberatung" in local:
        return "Studienberatung"
    if "studierendensekretariat" in local or ("campus" in local and "office" not in local):
        return "Studentensekretariat"
    if "pruefungs" in local:
        return "Prüfungsamt"
    if "studium" in local or "stud" in local:
        if "master" in local:
            return "Bewerbung Master"
        if "bachelor" in local:
            return "Bewerbung Bachelor"
        return "Studium/Allgemein"
    if "info" in local or "kontakt" in local or "contact" in local:
        return "Allgemeiner Kontakt"
    if "service" in local:
        return "Service"
    if "admissions" in local:
        if "graduate" in local or "pg" in local:
            return "Bewerbung Master"
        if "ug" in local or "undergrad" in local:
            return "Bewerbung Bachelor"
        if "international" in local:
            return "International Office"
        return "Bewerbung/Zulassung"
    if "apply" in local:
        return "Bewerbung/Zulassung"
    if "graduate" in local:
        return "Bewerbung Master"
    if "sekretariat" in local:
        return "Sekretariat"

    return "Sonstiges"


async def fetch_page(client: httpx.AsyncClient, url: str, timeout: float = 4.0) -> str | None:
    try:
        resp = await asyncio.wait_for(
            client.get(url, follow_redirects=True, timeout=timeout),
            timeout=timeout + 1,
        )
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


async def scrape_emails(
    client: httpx.AsyncClient,
    base_url: str,
    uni_name: str,
) -> list[dict]:
    found = []
    seen: set[str] = set()

    for path in KNOWN_PATHS:
        url = base_url.rstrip("/") + path
        page_text = await fetch_page(client, url)
        if page_text is None:
            continue

        for match in EMAIL_RE.finditer(page_text):
            email = match.group(0).lower().strip()
            domain = email.split("@")[-1] if "@" in email else ""

            if not domain:
                continue
            if any(skip in email for skip in ("example.com", ".png", ".jpg", ".css", ".js", ".svg")):
                continue
            if email in seen:
                continue
            seen.add(email)

            score = _admission_score(email)
            if score < 2:
                continue

            cat = _categorise(email)
            found.append({
                "University": uni_name,
                "Category": cat,
                "Email": email,
                "Score": str(score),
                "Source": url,
            })

    found.sort(key=lambda r: int(r["Score"]), reverse=True)
    deduped = []
    dedup_seen: set[str] = set()
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


def load_uni_urls() -> dict[str, str]:
    urls = {}
    path = DATA_DIR / "de_university_admissions.csv"
    if not path.exists():
        return urls
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            uni = row.get("University", "").strip()
            url = row.get("Website", "").strip().rstrip("/")
            if uni and url:
                urls[uni] = url
    return urls


async def main():
    import time
    import sys

    known = load_known_emails()
    known_before = known.copy()
    print(f"Loaded {len(known)} known emails from dataset", flush=True)

    uni_urls = load_uni_urls()
    if not uni_urls:
        print("No German university websites found in data/germany/")
        return 1

    print(f"Will scrape {len(uni_urls)} German university websites\n", flush=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; UniEmailScraper/2.0; +https://github.com/ghoseyy/university-admissions-emails)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    limits = httpx.Limits(max_keepalive_connections=8, max_connections=8)

    all_found = []
    errors = []
    start = time.monotonic()

    async with httpx.AsyncClient(headers=headers, limits=limits, timeout=10) as client:
        sem = asyncio.Semaphore(4)

        async def scrape_one(uni, url):
            async with sem:
                result = await scrape_emails(client, url, uni)
                return uni, result

        tasks = [scrape_one(uni, url) for uni, url in uni_urls.items()]
        for coro in asyncio.as_completed(tasks):
            uni, result = await coro
            new_count = sum(1 for r in result if r["Email"] not in known)
            elapsed = time.monotonic() - start
            print(f"{'✓' if result else ' '} {uni:50s} {len(result):3d} emails ({new_count} new) — {elapsed:5.1f}s", flush=True)
            all_found.extend(result)
            known.update(r["Email"] for r in result)

    print(f"\nBatch done: {len(all_found)} total", flush=True)

    if not all_found:
        print("\nNo emails scraped — websites may block automated requests.")
        return

    out_path = OUT_DIR / "de_scraped_candidates.csv"
    seen_final: set[str] = set()
    rows = []
    for r in all_found:
        if r["Email"] not in seen_final:
            seen_final.add(r["Email"])
            rows.append(r)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["University", "Category", "Email", "Score", "Source"])
        writer.writeheader()
        writer.writerows(rows)

    new_emails = [r for r in rows if r["Email"] not in known_before]
    total_elapsed = time.monotonic() - start
    print(f"\n{'='*60}")
    print(f"Total scraped: {len(rows)} unique emails")
    print(f"New (not in dataset): {len(new_emails)}")
    print(f"Duration: {total_elapsed:.0f}s")
    if new_emails:
        print(f"\nTop new candidates (by relevance score):")
        for r in sorted(new_emails, key=lambda x: int(x["Score"]), reverse=True)[:25]:
            print(f"  [{int(r['Score']):2d}] {r['Email']:50s} ({r['Category']:25s}) — {r['University']}")
    print(f"\nFull results saved to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
