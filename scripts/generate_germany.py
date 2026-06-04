"""Generate German university admissions email datasets,
incorporating real scraped emails where available."""

import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "germany"
DATA.mkdir(parents=True, exist_ok=True)

UNIVERSITIES: list[tuple[str, str, str, str, str, str]] = [
    ("22",  "Technical University of Munich (TUM)",                "tum.de",                "Munich",       "Bavaria",       "CS, AI, ML, Robotics, Data Science"),
    ("58",  "Ludwig Maximilian University of Munich (LMU)",        "lmu.de",                "Munich",       "Bavaria",       "CS, AI, ML, Data Science, Media Informatics"),
    ("80",  "Heidelberg University",                               "uni-heidelberg.de",     "Heidelberg",   "Baden-Württemberg", "CS, AI, Data Science, Scientific Computing"),
    ("88",  "Freie Universität Berlin",                            "fu-berlin.de",          "Berlin",       "Berlin",        "CS, AI, Data Science, Bioinformatics"),
    ("98",  "Karlsruhe Institute of Technology (KIT)",             "kit.edu",               "Karlsruhe",    "Baden-Württemberg", "CS, AI, ML, Data Science, Cyber Security"),
    ("105", "RWTH Aachen University",                              "rwth-aachen.de",        "Aachen",       "North Rhine-Westphalia", "CS, AI, ML, Data Science, Software Engineering"),
    ("130", "Humboldt University of Berlin",                       "hu-berlin.de",          "Berlin",       "Berlin",        "CS, AI, Data Science"),
    ("145", "Technical University of Berlin (TU Berlin)",          "tu-berlin.de",          "Berlin",       "Berlin",        "CS, AI, ML, Data Science, Cyber Security"),
    ("193", "University of Hamburg",                               "uni-hamburg.de",        "Hamburg",      "Hamburg",       "CS, AI, Data Science, Language Technology"),
    ("201", "University of Freiburg",                              "uni-freiburg.de",       "Freiburg",     "Baden-Württemberg", "CS, AI, Data Science, Embedded Systems"),
    ("207", "University of Bonn",                                  "uni-bonn.de",           "Bonn",         "North Rhine-Westphalia", "CS, AI, ML, Data Science, Cyber Security"),
    ("215", "University of Tübingen",                              "uni-tuebingen.de",      "Tübingen",     "Baden-Württemberg", "CS, AI, ML, Data Science, Cognitive Science"),
    ("218", "Technical University of Dresden (TU Dresden)",        "tu-dresden.de",         "Dresden",      "Saxony",        "CS, AI, ML, Data Science, Computational Engineering"),
    ("232", "FAU Erlangen-Nuremberg",                              "fau.de",                "Erlangen",     "Bavaria",       "CS, AI, Data Science, Medical Informatics"),
    ("243", "University of Göttingen",                             "uni-goettingen.de",     "Göttingen",    "Lower Saxony",  "CS, AI, Data Science, Applied Informatics"),
    ("253", "Technical University of Darmstadt (TU Darmstadt)",    "tu-darmstadt.de",       "Darmstadt",    "Hesse",         "CS, AI, ML, Data Science, Cyber Security"),
    ("272", "University of Cologne",                               "uni-koeln.de",          "Cologne",      "North Rhine-Westphalia", "CS, AI, Data Science"),
    ("310", "University of Stuttgart",                             "uni-stuttgart.de",      "Stuttgart",    "Baden-Württemberg", "CS, AI, ML, Data Science, Software Technology"),
    ("316", "Goethe University Frankfurt",                         "uni-frankfurt.de",      "Frankfurt",    "Hesse",         "CS, AI, Data Science, Bioinformatics"),
    ("350", "University of Münster",                               "uni-muenster.de",       "Münster",      "North Rhine-Westphalia", "CS, AI, Data Science, Geoinformatics"),
    ("395", "Ruhr University Bochum",                              "ruhr-uni-bochum.de",    "Bochum",       "North Rhine-Westphalia", "CS, AI, Cyber Security, Data Science"),
    ("416", "University of Würzburg",                              "uni-wuerzburg.de",      "Würzburg",     "Bavaria",       "CS, AI, Data Science, Human-Computer Interaction"),
    ("416", "University of Mannheim",                              "uni-mannheim.de",       "Mannheim",     "Baden-Württemberg", "CS, AI, Data Science, Business Informatics"),
    ("433", "Leibniz University Hannover",                         "uni-hannover.de",       "Hannover",     "Lower Saxony",  "CS, AI, Data Science, Computational Engineering"),
    ("440", "University of Konstanz",                              "uni-konstanz.de",       "Konstanz",     "Baden-Württemberg", "CS, AI, Data Science"),
    ("448", "University of Bayreuth",                              "uni-bayreuth.de",       "Bayreuth",     "Bavaria",       "CS, AI, Data Science, Sports Informatics"),
    ("452", "Johannes Gutenberg University Mainz",                 "uni-mainz.de",          "Mainz",        "Rhineland-Palatinate", "CS, AI, Data Science"),
    ("477", "University of Potsdam",                               "uni-potsdam.de",        "Potsdam",      "Brandenburg",   "CS, AI, Data Science, Computational Science"),
    ("487", "TU Bergakademie Freiberg",                            "tu-freiberg.de",        "Freiberg",     "Saxony",        "CS, AI, Data Science, Computational Materials"),
    ("496", "Justus Liebig University Giessen",                    "uni-giessen.de",        "Giessen",      "Hesse",         "CS, AI, Data Science"),
    ("530", "University of Bremen",                                "uni-bremen.de",         "Bremen",       "Bremen",        "CS, AI, Data Science, Digital Media"),
    ("535", "Leipzig University",                                  "uni-leipzig.de",        "Leipzig",      "Saxony",        "CS, AI, Data Science, Computational Humanities"),
    ("546", "Ulm University",                                      "uni-ulm.de",            "Ulm",          "Baden-Württemberg", "CS, AI, ML, Data Science, Cognitive Systems"),
    ("575", "Friedrich Schiller University Jena",                  "uni-jena.de",           "Jena",         "Thuringia",     "CS, AI, Data Science, Bioinformatics"),
    ("618", "Kiel University",                                     "uni-kiel.de",           "Kiel",         "Schleswig-Holstein", "CS, AI, Data Science, Digital Humanities"),
    ("635", "Saarland University",                                 "uni-saarland.de",       "Saarbrücken",  "Saarland",      "CS, AI, ML, Data Science, Cyber Security, Visual Computing"),
    ("673", "TU Dortmund University",                              "tu-dortmund.de",        "Dortmund",     "North Rhine-Westphalia", "CS, AI, Data Science, Software Engineering"),
    ("691", "University of Regensburg",                            "uni-regensburg.de",     "Regensburg",   "Bavaria",       "CS, AI, Data Science"),
    ("711", "Technical University of Braunschweig",                "tu-braunschweig.de",    "Braunschweig", "Lower Saxony",  "CS, AI, Data Science, Computational Engineering"),
    ("711", "University of Hohenheim",                             "uni-hohenheim.de",      "Stuttgart",    "Baden-Württemberg", "CS, AI, Data Science (Agricultural focus)"),
    ("751", "Martin Luther University Halle-Wittenberg",           "uni-halle.de",          "Halle",        "Saxony-Anhalt", "CS, AI, Data Science"),
    ("771", "University of Marburg",                               "uni-marburg.de",        "Marburg",      "Hesse",         "CS, AI, Data Science, Bioinformatics"),
    ("801", "University of Duisburg-Essen",                        "uni-due.de",            "Essen",        "North Rhine-Westphalia", "CS, AI, Data Science, Cyber Security"),
    ("851", "University of Rostock",                               "uni-rostock.de",        "Rostock",      "Mecklenburg-Vorpommern", "CS, AI, Data Science"),
    ("851", "Heinrich Heine University Düsseldorf",                 "hhu.de",                "Düsseldorf",   "North Rhine-Westphalia", "CS, AI, Data Science, Computational Linguistics"),
    ("1001","Bielefeld University",                                "uni-bielefeld.de",      "Bielefeld",    "North Rhine-Westphalia", "CS, AI, Data Science, Cognitive Robotics"),
    ("1201","University of Siegen",                                "uni-siegen.de",         "Siegen",       "North Rhine-Westphalia", "CS, AI, Data Science, HCI"),
    ("1201","RPTU Kaiserslautern-Landau",                          "rptu.de",               "Kaiserslautern", "Rhineland-Palatinate", "CS, AI, Data Science, Software Engineering"),
    ("N/A", "Ilmenau University of Technology",                    "tu-ilmenau.de",         "Ilmenau",      "Thuringia",     "CS, AI, Data Science, Media Technology"),
    ("N/A", "University of Passau",                                "uni-passau.de",         "Passau",       "Bavaria",       "CS, AI, Data Science, Digital Business"),
    ("N/A", "Paderborn University",                                "uni-paderborn.de",      "Paderborn",    "North Rhine-Westphalia", "CS, AI, Data Science, HCI"),
    ("N/A", "Constructor University Bremen",                       "constructor.university","Bremen",       "Bremen",        "CS, AI, Data Science, Robotics"),
    ("N/A", "University of Greifswald",                            "uni-greifswald.de",     "Greifswald",   "Mecklenburg-Vorpommern", "CS, AI, Data Science, Digital Humanities"),
    ("N/A", "Leuphana University Lüneburg",                        "leuphana.de",           "Lüneburg",     "Lower Saxony",  "CS, AI, Data Science, Digital Media"),
    ("N/A", "University of Wuppertal",                             "uni-wuppertal.de",      "Wuppertal",    "North Rhine-Westphalia", "CS, AI, Data Science, Cyber Security"),
    ("N/A", "Hamburg University of Technology (TUHH)",             "tuhh.de",               "Hamburg",      "Hamburg",       "CS, AI, Data Science, Computational Engineering"),
    ("N/A", "Otto von Guericke University Magdeburg",              "ovgu.de",               "Magdeburg",    "Saxony-Anhalt", "CS, AI, Data Science, Digital Engineering"),
    ("N/A", "University of Kassel",                                "uni-kassel.de",         "Kassel",       "Hesse",         "CS, AI, Data Science, Smart Systems"),
    ("N/A", "University of Oldenburg",                             "uni-oldenburg.de",      "Oldenburg",    "Lower Saxony",  "CS, AI, Data Science, Hearing Technology"),
    ("N/A", "University of Augsburg",                              "uni-augsburg.de",       "Augsburg",     "Bavaria",       "CS, AI, Data Science, Information Systems"),
    ("N/A", "University of Lübeck",                                "uni-luebeck.de",        "Lübeck",       "Schleswig-Holstein", "CS, AI, Data Science, Medical Informatics"),
]

# ---------------------------------------------------------------------------
# Load scraped (real) emails to use as overrides
# ---------------------------------------------------------------------------
SCRAPED_SOURCE = Path(__file__).resolve().parent.parent / "data" / "de_scraped_candidates.csv"

scraped_overrides: dict[str, dict[str, str]] = {}
if SCRAPED_SOURCE.exists():
    with open(SCRAPED_SOURCE) as f:
        for row in csv.DictReader(f):
            email = row["Email"].lower().strip()
            domain = email.split("@")[-1] if "@" in email else ""
            # skip garbage
            if domain in ("swfr.de", "parrot-media.de", "pluswerk.digital", "international.uni"):
                continue
            if email.startswith("u003e"):
                continue
            uni = row["University"]
            cat = row["Category"]
            scraped_overrides.setdefault(uni, {})[cat] = email

# ---------------------------------------------------------------------------
# Email builders (same as before)
# ---------------------------------------------------------------------------

CS_SPECIAL: dict[str, str] = {
    "tum.de": "studium@in.tum.de",
    "lmu.de": "studium@informatik.uni-muenchen.de",
    "kit.edu": "studium@informatik.kit.edu",
    "fau.de": "studium@informatik.fau.de",
    "tu-darmstadt.de": "studium@informatik.tu-darmstadt.de",
    "tu-dresden.de": "studium@informatik.tu-dresden.de",
    "tu-berlin.de": "studium@informatik.tu-berlin.de",
    "tu-dortmund.de": "studium@informatik.tu-dortmund.de",
    "tu-braunschweig.de": "studium@informatik.tu-braunschweig.de",
    "tu-freiberg.de": "studium@informatik.tu-freiberg.de",
    "tuhh.de": "studium@tuhh.de",
    "rptu.de": "studium@informatik.rptu.de",
    "ovgu.de": "studium@informatik.ovgu.de",
    "tu-ilmenau.de": "studium@informatik.tu-ilmenau.de",
    "hhu.de": "studium@cs.hhu.de",
    "constructor.university": "cs@constructor.university",
    "uni-hannover.de": "studium@informatik.uni-hannover.de",
    "uni-stuttgart.de": "studium@informatik.uni-stuttgart.de",
}

def email_cs(domain: str, name: str = "") -> str:
    if domain in CS_SPECIAL:
        return CS_SPECIAL[domain]
    if domain.startswith("uni-"):
        city = domain.removeprefix("uni-").removesuffix(".de")
        return f"studium@informatik.uni-{city}.de"
    return f"informatik@{domain}"

def email_general(domain: str, name: str = "") -> str:
    return "study@constructor.university" if domain == "constructor.university" else f"studium@{domain}"

def email_ug(domain: str, name: str = "") -> str:
    return f"bewerbung-bachelor@{domain}"

def email_pgt(domain: str, name: str = "") -> str:
    return f"bewerbung-master@{domain}"

def email_phd(domain: str, name: str = "") -> str:
    return f"promotion@{domain}"

def email_international(domain: str, name: str = "") -> str:
    return f"international@{domain}"

def email_student_services(domain: str, name: str = "") -> str:
    return f"studierendensekretariat@{domain}"

def email_finance(domain: str, name: str = "") -> str:
    return f"studienfinanzierung@{domain}"

def email_accommodation(domain: str, name: str = "") -> str:
    return f"wohnen@{domain}"

def email_engineering(domain: str, name: str = "") -> str:
    return f"ingenieurwesen@{domain}"

def email_cas(domain: str, name: str = "") -> str:
    return f"studium@{domain}"

# Category definitions: (label, builder_fn, scraped_category_key)
CATEGORIES: list[tuple[str, ...]] = [
    ("studienberatung",          email_general,           "Studienberatung"),
    ("Bewerbung Bachelor",       email_ug,                "Bewerbung Bachelor"),
    ("Bewerbung Master",         email_pgt,               "Bewerbung Master"),
    ("Promotion/PhD",            email_phd,               "Promotion/PhD"),
    ("International Office",     email_international,     "International Office"),
    ("Studentensekretariat",     email_student_services,  "Studentensekretariat"),
    ("Studienfinanzierung",      email_finance,           None),
    ("Wohnen/Accommodation",     email_accommodation,     None),
    ("Informatik/Fachbereich",   email_cs,                None),
    ("Ingenieurwissenschaften",  email_engineering,       None),
    ("CAS/Immatrikulation",      email_cas,               None),
]

SCRAPED_CAT_MAP: dict[str, str] = {
    "Studium/Allgemein": "studienberatung",
    "Studienberatung": "studienberatung",
    "International Office": "International Office",
    "Studentensekretariat": "Studentensekretariat",
    "Bewerbung/Zulassung": "Bewerbung Bachelor",  # generic fallback
    "Bewerbung Master": "Bewerbung Master",
    "Service": "Studentensekretariat",
}

def resolve_email(label: str, builder, scraped_key: str | None, domain: str, uni_name: str) -> str:
    scraped = scraped_overrides.get(uni_name, {})
    # Check direct scraped->pattern mapping
    if scraped_key and scraped_key in scraped:
        return scraped[scraped_key]
    # Also map via SCRAPED_CAT_MAP
    for scraped_cat, pattern_cat in SCRAPED_CAT_MAP.items():
        if label == pattern_cat and scraped_cat in scraped:
            return scraped[scraped_cat]
    return builder(domain, uni_name)

# ---------------------------------------------------------------------------
# de_admissions.csv
# ---------------------------------------------------------------------------
header = ["University", "Category", "Email", "QS 2026 Rank"]
all_rows: list[list[str]] = [header]
for rank, name, domain, *_ in UNIVERSITIES:
    for label, builder, scraped_key in CATEGORIES:
        email = resolve_email(label, builder, scraped_key, domain, name)
        all_rows.append([name, label, email, rank])

with open(DATA / "de_admissions.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(all_rows)
print(f"→ de_admissions.csv  -  {len(all_rows) - 1} rows")

# ---------------------------------------------------------------------------
# de_cs_masters_ranked.csv
# ---------------------------------------------------------------------------
cs_header = ["QS 2026 Rank", "University", "Admissions Email", "Website", "State", "Relevant MSc Programs"]
cs_rows: list[list[str]] = [cs_header]
for rank, name, domain, _, state, prog in UNIVERSITIES:
    scraped = scraped_overrides.get(name, {})
    primary = scraped.get("Studienberatung") or scraped.get("Studium/Allgemein") or scraped.get("Bewerbung/Zulassung") or email_general(domain)
    website = f"https://www.{domain}"
    cs_rows.append([rank, name, primary, website, state, prog])

with open(DATA / "de_cs_masters_ranked.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(cs_rows)
print(f"→ de_cs_masters_ranked.csv  -  {len(cs_rows) - 1} rows")

# ---------------------------------------------------------------------------
# de_university_admissions.csv
# ---------------------------------------------------------------------------
simple_header = ["University", "Admissions Email", "Website", "State"]
simple_rows: list[list[str]] = [simple_header]
for rank, name, domain, _, state, _ in UNIVERSITIES:
    scraped = scraped_overrides.get(name, {})
    primary = scraped.get("Studienberatung") or scraped.get("Studium/Allgemein") or scraped.get("Bewerbung/Zulassung") or email_general(domain)
    website = f"https://www.{domain}"
    simple_rows.append([name, primary, website, state])

with open(DATA / "de_university_admissions.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(simple_rows)
print(f"→ de_university_admissions.csv  -  {len(simple_rows) - 1} rows")

print("Done.")
