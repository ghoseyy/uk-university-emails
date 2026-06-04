import csv
import os
import re

DATA_DIR = "/Users/ktmmbp019/Documents/uk-uni-emails/data"
FILES = ["uk_all_1000plus.csv", "uk_uni_cs_masters_ranked.csv", "uk_university_admissions_emails.csv"]

NAME_MAP = {
    "Univ of Birmingham": "University of Birmingham",
    "Univ of Glasgow": "University of Glasgow",
    "Univ of Southampton": "University of Southampton",
    "Univ of Sheffield": "University of Sheffield",
    "Univ of Nottingham": "University of Nottingham",
    "Univ of St Andrews": "University of St Andrews",
    "Univ of York": "University of York",
    "Univ of Central Lancashire": "University of Central Lancashire",
    "Univ of Westminster": "University of Westminster",
    "Univ of Bedfordshire": "University of Bedfordshire",
    "Univ of West of Scotland": "University of the West of Scotland",
    "Univ of Sunderland": "University of Sunderland",
    "Univ of Gloucestershire": "University of Gloucestershire",
    "Univ of Bolton": "University of Bolton",
    "Univ of Northampton": "University of Northampton",
    "Univ of Worcester": "University of Worcester",
    "Univ of Roehampton": "University of Roehampton",
    "Univ of Cumbria": "University of Cumbria",
    "Univ of Suffolk": "University of Suffolk",
    "Univ of Chichester": "University of Chichester",
    "Univ of West London": "University of West London",
    "Univ of Winchester": "University of Winchester",
    "Univ of Staffordshire": "University of Staffordshire",
    "Univ of Buckingham": "University of Buckingham",
    "Univ of Wales": "University of Wales",
    "Univ of Hertfordshire": "University of Hertfordshire",
    "Univ of Brighton": "University of Brighton",
    "Univ of Lincoln": "University of Lincoln",
    "Univ of East London": "University of East London",
    "Univ of Wolverhampton": "University of Wolverhampton",
    "Univ of Greenwich": "University of Greenwich",
    "Univ of South Wales": "University of South Wales",
    "Univ of Huddersfield": "University of Huddersfield",
    "Univ of Highlands Islands": "University of the Highlands and Islands",
    "London South Bank Univ": "London South Bank University",
    "Glasgow Caledonian Univ": "Glasgow Caledonian University",
    "Buckinghamshire New Univ": "Buckinghamshire New University",
    "Southampton Solent Univ": "Southampton Solent University",
    "Bishop Grosseteste Univ": "Bishop Grosseteste University",
    "Wrexham Glyndwr Univ": "Wrexham Glyndwr University",
    "Cardiff Metropolitan Univ": "Cardiff Metropolitan University",
    "London Metropolitan Univ": "London Metropolitan University",
    "Royal Agricultural Univ": "Royal Agricultural University",
    "Plymouth Marjon Univ": "Plymouth Marjon University",
    "Manchester Metropolitan U": "Manchester Metropolitan University",
    "Univ for Creative Arts": "University for the Creative Arts",
    "Univ College Birmingham": "University College Birmingham",
    "Queen Mary Univ of London": "Queen Mary University of London",
    "Birkbeck Univ of London": "Birkbeck, University of London",
    "Goldsmiths Univ of London": "Goldsmiths, University of London",
    "SOAS Univ of London": "SOAS University of London",
    "Norwich Univ of Arts": "Norwich University of the Arts",
    "Royal Holloway Univ London": "Royal Holloway, University of London",
    "Regents Univ London": "Regent's University London",
    "Ravensbourne Univ London": "Ravensbourne University London",
    "Arts Univ Bournemouth": "Arts University Bournemouth",
    "St Marys Univ Twickenham": "St Mary's University, Twickenham",
    "City St George's Univ": "City St George's, University of London",
    "UCL (Univ College London)": "UCL (University College London)",
    "Kings College London": "King's College London",
    "LSE": "London School of Economics",
    "UWE Bristol": "University of the West of England",
    "Queens University Belfast": "Queen's University Belfast",
    "Liverpool John Moores": "Liverpool John Moores University",
    "Wales Trinity Saint David": "University of Wales Trinity Saint David",
    "Canterbury Christ Church": "Canterbury Christ Church University",
    "London Sch Hygiene Trop Med": "London School of Hygiene & Tropical Medicine",
    "Liverpool Sch Trop Medicine": "Liverpool School of Tropical Medicine",
}


def normalize_name(name):
    name = name.strip()
    if name in NAME_MAP:
        return NAME_MAP[name]
    name = re.sub(r'\bUniv of\b', 'University of', name)
    name = re.sub(r'\bUniv$', 'University', name)
    name = re.sub(r'\sU$', ' University', name)
    return name


def get_uni_col_index(headers):
    for i, h in enumerate(headers):
        if h.strip().lower() == 'university':
            return i
    return 0

def process_file(filepath):
    rows = []
    changed = 0
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        uni_col = get_uni_col_index(headers)
        rows.append(headers)
        for row in reader:
            if not row:
                continue
            original = row[uni_col]
            normalized = normalize_name(original)
            if normalized != original:
                changed += 1
            row[uni_col] = normalized
            rows.append(row)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)

    return changed, len(rows) - 1


print("=" * 70)
print("Normalizing university names in CSV files...")
print("=" * 70)

all_universities = set()
for fname in FILES:
    filepath = os.path.join(DATA_DIR, fname)
    changed, total = process_file(filepath)
    print(f"\n{fname}:")
    print(f"  Total rows (excl header): {total}")
    print(f"  Names changed: {changed}")

print("\n" + "=" * 70)
print("Final unique university counts per file:")
print("=" * 70)

for fname in FILES:
    filepath = os.path.join(DATA_DIR, fname)
    unis = set()
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        uni_col = get_uni_col_index(headers)
        for row in reader:
            if row:
                unis.add(row[uni_col])
    print(f"\n{fname}: {len(unis)} unique universities")
    for u in sorted(unis):
        print(f"  - {u}")

print("\nDone.")
