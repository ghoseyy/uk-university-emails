"""Scrape Norwegian university websites for real admissions emails."""

import asyncio
import csv
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "norway"
OUT_DIR = DATA_DIR.parent

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
KEYWORD_RE = re.compile(
    r"studie|opptak|søknad|admissions?|apply|international|exchange|master|phd"
    r"|postmottak|kontakt|contact|info|informasjon|studieveiledning|veiledning"
    r"|informatikk|data|cs|ifi|studieadmin|bolig|housing",
    re.IGNORECASE,
)

KNOWN_PATHS = [
    "/kontakt",
    "/om",
    "/studier",
    "/studietilbud",
    "/opptak",
    "/admissions",
    "/international",
    "/exchange",
    "/phd",
    "/forskning",
    "/for-studenter",
    "/studieveiledning",
    "/contact",
    "/about",
    "/study",
    "/apply",
    "/master",
    "/studieinfo",
]


def _score(email: str) -> int:
    local = email.split("@")[0].lower()
    score = 0
    if "opptak" in local or "admissions" in local:
        score += 10
    if "søknad" in local or "apply" in local:
        score += 9
    if "studie" in local or "study" in local:
        score += 7
    if "master" in local:
        score += 5
    if "phd" in local or "ph.d" in local:
        score += 5
    if "international" in local or "exchange" in local:
        score += 6
    if "postmottak" in local or "post" in local:
        score += 4
    if "veiledning" in local or "info" in local:
        score += 3
    if "informatikk" in local or "data" in local or "cs" in local or "ifi" in local:
        score += 4
    if "kontakt" in local or "contact" in local:
        score += 2
    if "bolig" in local or "housing" in local:
        score += 3
    if "studieadmin" in local:
        score += 4
    domain = email.split("@")[-1] if "@" in email else ""
    if domain.endswith((".no", ".com", ".org")):
        score += 1
    return score


def _cat(email: str) -> str:
    local = email.split("@")[0].lower()
    if "opptak" in local or "søknad" in local:
        return "Admissions"
    if "admissions" in local:
        if "graduate" in local or "master" in local:
            return "Master Admission"
        if "ug" in local or "undergrad" in local or "bachelor" in local:
            return "Bachelor Admission"
        if "international" in local:
            return "International Office"
        return "Admissions"
    if "international" in local or "exchange" in local:
        return "International Office"
    if "master" in local:
        return "Master Admission"
    if "phd" in local or "ph.d" in local or "phd" in local:
        return "PhD"
    if "informatikk" in local or "data" in local or "cs" in local or "ifi" in local:
        return "CS / Informatics"
    if "studie" in local:
        if "admin" in local:
            return "Student Services"
        if "veiledning" in local:
            return "Study Guidance"
        if "info" in local:
            return "Study Info"
        return "Study / Admissions"
    if "bolig" in local or "housing" in local:
        return "Housing"
    if "postmottak" in local or "post" in local or "kontakt" in local:
        return "General / Post"
    if "info" in local:
        return "General Info"
    return "Other"


async def fetch(client: httpx.AsyncClient, url: str, timeout: float = 4.0) -> str | None:
    try:
        resp = await asyncio.wait_for(client.get(url, follow_redirects=True, timeout=timeout), timeout=timeout + 1)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


async def scrape_emails(client: httpx.AsyncClient, base_url: str, uni_name: str) -> list[dict]:
    found = []
    seen: set[str] = set()

    for path in KNOWN_PATHS:
        url = base_url.rstrip("/") + path
        html = await fetch(client, url)
        if html is None:
            continue

        for m in EMAIL_RE.finditer(html):
            email = m.group(0).lower().strip()
            domain = email.split("@")[-1] if "@" in email else ""
            if not domain:
                continue
            if any(s in email for s in ("example.com", ".png", ".jpg", ".css", ".js", ".svg")):
                continue
            if email in seen:
                continue
            seen.add(email)

            s = _score(email)
            if s < 2:
                continue

            found.append({
                "University": uni_name,
                "Category": _cat(email),
                "Email": email,
                "Score": str(s),
                "Source": url,
            })

    found.sort(key=lambda r: int(r["Score"]), reverse=True)
    dedup = []
    seen2: set[str] = set()
    for r in found:
        if r["Email"] not in seen2:
            seen2.add(r["Email"])
            dedup.append(r)
    return dedup


def load_uni() -> dict[str, str]:
    path = DATA_DIR / "no_university_admissions.csv"
    if not path.exists():
        return {}
    urls = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            u = row.get("University", "").strip()
            w = row.get("Website", "").strip().rstrip("/")
            if u and w:
                urls[u] = w
    return urls


def load_known() -> set[str]:
    known = set()
    for f in DATA_DIR.glob("*.csv"):
        with open(f) as fh:
            for row in csv.DictReader(fh):
                e = (row.get("Email") or row.get("Admissions Email") or "").strip().lower()
                if e:
                    known.add(e)
    return known


async def main():
    import time

    known = load_known()
    known_before = known.copy()
    print(f"Loaded {len(known)} known emails", flush=True)

    urls = load_uni()
    if not urls:
        print("No Norwegian university data found")
        return

    print(f"Scraping {len(urls)} universities\n", flush=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; UniScraper/NO; +https://github.com/ghoseyy/university-admissions-emails)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "nb-NO,nb;q=0.9,en;q=0.8",
    }
    limits = httpx.Limits(max_keepalive_connections=6, max_connections=6)

    all_found = []
    start = time.monotonic()

    async with httpx.AsyncClient(headers=headers, limits=limits, timeout=10) as client:
        sem = asyncio.Semaphore(3)

        async def scrape_one(uni, url):
            async with sem:
                return uni, await scrape_emails(client, url, uni)

        tasks = [scrape_one(u, w) for u, w in urls.items()]
        for coro in asyncio.as_completed(tasks):
            uni, result = await coro
            new = sum(1 for r in result if r["Email"] not in known)
            t = time.monotonic() - start
            print(f"{'✓' if result else ' '} {uni:55s} {len(result):3d} emails ({new} new) — {t:5.1f}s", flush=True)
            all_found.extend(result)
            known.update(r["Email"] for r in result)

    if not all_found:
        print("\nNo results")
        return

    out = OUT_DIR / "no_scraped_candidates.csv"
    seen: set[str] = set()
    rows = []
    for r in all_found:
        if r["Email"] not in seen:
            seen.add(r["Email"])
            rows.append(r)

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["University", "Category", "Email", "Score", "Source"])
        w.writeheader()
        w.writerows(rows)

    new_rows = [r for r in rows if r["Email"] not in known_before]
    elapsed = time.monotonic() - start
    print(f"\n{'='*60}")
    print(f"Total scraped: {len(rows)} unique emails, {len(new_rows)} new")
    print(f"Duration: {elapsed:.0f}s")
    if new_rows:
        print(f"\nTop new:")
        for r in sorted(new_rows, key=lambda x: int(x["Score"]), reverse=True)[:20]:
            print(f"  [{r['Score']:2s}] {r['Email']:50s} ({r['Category']:25s}) — {r['University']}")
    print(f"\nSaved to: {out}")


if __name__ == "__main__":
    asyncio.run(main())
