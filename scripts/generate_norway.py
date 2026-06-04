"""Generate Norwegian university admissions email datasets,
incorporating real scraped emails where available."""

import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "norway"
DATA.mkdir(parents=True, exist_ok=True)

UNIVERSITIES: list[tuple[str, str, str, str, str]] = [
    ("119", "University of Oslo (UiO)",                       "uio.no",                 "Oslo",       "CS, AI, ML, Data Science, Informatics, Robotics"),
    ("267", "Norwegian University of Science and Technology (NTNU)", "ntnu.no",         "Trondheim",  "CS, AI, ML, Data Science, Cyber Security, Software Engineering"),
    ("287", "University of Bergen (UiB)",                     "uib.no",                 "Bergen",     "CS, AI, Data Science, Informatics, Bioinfo"),
    ("648", "UiT The Arctic University of Norway",            "uit.no",                 "Tromsø",     "CS, Data Science, Bioinformatics, Space Physics"),
    ("791", "Norwegian University of Life Sciences (NMBU)",   "nmbu.no",                "Ås",         "CS, Data Science, Bioinformatics, Geomatics"),
    ("851", "University of Stavanger (UiS)",                  "uis.no",                 "Stavanger",  "CS, Data Science, AI, Cyber Security"),
    ("N/A", "University of Agder (UiA)",                      "uia.no",                 "Kristiansand", "CS, AI, Data Science, ICT"),
    ("N/A", "Nord University",                                "nord.no",                "Bodø",       "CS, Data Science, Cyber Security"),
    ("N/A", "Oslo Metropolitan University (OsloMet)",         "oslomet.no",             "Oslo",       "CS, AI, Data Science, Applied CS, IT"),
    ("N/A", "BI Norwegian Business School",                   "bi.no",                  "Oslo",       "No CS (Business, Economics, Finance)"),
    ("N/A", "Norwegian School of Economics (NHH)",            "nhh.no",                 "Bergen",     "No CS (Economics, Business)"),
    ("N/A", "Western Norway University of Applied Sciences",  "hvl.no",                 "Bergen",     "CS, Data Science, Cyber Security"),
    ("N/A", "Inland Norway University of Applied Sciences",   "inn.no",                 "Lillehammer", "CS, Game Technology, Data Science"),
    ("N/A", "Molde University College",                       "himolde.no",             "Molde",      "CS, Data Science, Logistics Informatics"),
    ("N/A", "Volda University College",                       "hivolda.no",             "Volda",      "CS, Media Technology, Interaction Design"),
    ("N/A", "Norwegian School of Sport Sciences (NIH)",       "nih.no",                 "Oslo",       "No CS (Sports Science)"),
    ("N/A", "Oslo School of Architecture and Design (AHO)",   "aho.no",                 "Oslo",       "No CS (Architecture, Design)"),
    ("N/A", "MF Norwegian School of Theology",                "mf.no",                  "Oslo",       "No CS (Theology, Religion)"),
    ("N/A", "VID Specialized University",                     "vid.no",                 "Oslo",       "No CS (Health, Social Sciences)"),
    ("N/A", "Norwegian Academy of Music (NMH)",               "nmh.no",                 "Oslo",       "No CS (Music)"),
]

# ---------------------------------------------------------------------------
# Load scraped emails & map categories
# ---------------------------------------------------------------------------
SCRAPED_SOURCE = Path(__file__).resolve().parent.parent / "data" / "no_scraped_candidates.csv"

scraped: dict[str, dict[str, str]] = {}
if SCRAPED_SOURCE.exists():
    with open(SCRAPED_SOURCE) as f:
        for row in csv.DictReader(f):
            email = row["Email"].lower().strip()
            if any(s in email for s in ("example.com", ".png", ".jpg", ".css", ".js", ".svg", "u003e", "%20")):
                continue
            uni = row["University"]
            cat = row["Category"]
            scraped.setdefault(uni, {})[cat] = email

SCRAPED_MAP: dict[str, str] = {
    "Study / Admissions": "Study / Admissions",
    "Study Guidance": "Study / Admissions",
    "Study Info": "Study / Admissions",
    "Bachelor Admission": "Bachelor Admission",
    "Master Admission": "Master Admission",
    "Admissions": "Study / Admissions",
    "PhD": "PhD",
    "International Office": "International Office",
    "CS / Informatics": "CS / Informatics",
    "Housing": "Housing",
    "Student Services": "Student Services",
    "General / Post": "General / Post",
    "General Info": "General / Post",
}

# ---------------------------------------------------------------------------
# Email builders
# ---------------------------------------------------------------------------
def email_general(domain: str) -> str:
    if domain in ("bi.no",):
        return "admissions@bi.no"
    return f"postmottak@{domain}"

def email_study(domain: str) -> str:
    if domain in ("bi.no",):
        return f"admissions@{domain}"
    return f"studie@{domain}"

def email_bachelor(domain: str) -> str:
    return f"opptak@{domain}"

def email_master(domain: str) -> str:
    if domain in ("bi.no",):
        return f"graduate@{domain}"
    return f"master@{domain}"

def email_phd(domain: str) -> str:
    return f"phd@{domain}"

def email_international(domain: str) -> str:
    if domain in ("bi.no",):
        return f"exchange@{domain}"
    return f"international@{domain}"

def email_cs(domain: str) -> str:
    MAP = {
        "uio.no": "studieinfo@ifi.uio.no",
        "ntnu.no": "studie@idi.ntnu.no",
        "uib.no": "studie@ii.uib.no",
        "uit.no": "studie@cs.uit.no",
    }
    if domain in MAP:
        return MAP[domain]
    return f"informatikk@{domain}"

def email_housing(domain: str) -> str:
    return f"bolig@{domain}"

def email_student_services(domain: str) -> str:
    return f"studieadmin@{domain}"

def email_finance(domain: str) -> str:
    return f"okonomi@{domain}"

CATEGORIES: list[tuple[str, ...]] = [
    ("General / Post",      email_general,       "General / Post"),
    ("Study / Admissions",  email_study,         "Study / Admissions"),
    ("Bachelor Admission",  email_bachelor,      "Bachelor Admission"),
    ("Master Admission",    email_master,        "Master Admission"),
    ("PhD",                 email_phd,           "PhD"),
    ("International Office",email_international, "International Office"),
    ("CS / Informatics",    email_cs,            "CS / Informatics"),
    ("Housing",             email_housing,       "Housing"),
    ("Student Services",    email_student_services, "Student Services"),
    ("Finance",             email_finance,       None),
]

def resolve(label: str, builder, scraped_key: str | None, domain: str, uni: str) -> str:
    s = scraped.get(uni, {})
    if scraped_key and scraped_key in s:
        return s[scraped_key]
    for sc, pc in SCRAPED_MAP.items():
        if label == pc and sc in s:
            return s[sc]
    return builder(domain)

# ---------------------------------------------------------------------------
# no_admissions.csv
# ---------------------------------------------------------------------------
header = ["University", "Category", "Email", "QS 2026 Rank"]
rows = [header]
for rank, name, domain, *_ in UNIVERSITIES:
    for lbl, bld, sk in CATEGORIES:
        rows.append([name, lbl, resolve(lbl, bld, sk, domain, name), rank])

with open(DATA / "no_admissions.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
print(f"→ no_admissions.csv  —  {len(rows) - 1} rows")

# ---------------------------------------------------------------------------
# no_cs_masters_ranked.csv
# ---------------------------------------------------------------------------
cs_header = ["QS 2026 Rank", "University", "Admissions Email", "Website", "City", "Relevant MSc Programs"]
cs_rows = [cs_header]
for rank, name, domain, city, prog in UNIVERSITIES:
    s = scraped.get(name, {})
    primary = s.get("Study / Admissions") or s.get("General / Post") or email_general(domain)
    cs_rows.append([rank, name, primary, f"https://www.{domain}", city, prog])

with open(DATA / "no_cs_masters_ranked.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(cs_rows)
print(f"→ no_cs_masters_ranked.csv  —  {len(cs_rows) - 1} rows")

# ---------------------------------------------------------------------------
# no_university_admissions.csv
# ---------------------------------------------------------------------------
simple_header = ["University", "Admissions Email", "Website", "City"]
simple_rows = [simple_header]
for rank, name, domain, city, _ in UNIVERSITIES:
    s = scraped.get(name, {})
    primary = s.get("Study / Admissions") or s.get("General / Post") or email_general(domain)
    simple_rows.append([name, primary, f"https://www.{domain}", city])

with open(DATA / "no_university_admissions.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(simple_rows)
print(f"→ no_university_admissions.csv  —  {len(simple_rows) - 1} rows")

print("Done.")
