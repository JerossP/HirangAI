"""
rebrand.py — one-shot brand & terminology replacement for HirangAI
"""
import re

with open("app.py", encoding="utf-8") as f:
    src = f.read()

original_len = len(src)

pairs = [
    # Doc comment
    ("TalentLens AI \u2014 Streamlit frontend entry point",
     "HirangAI \u2014 Streamlit frontend entry point"),
    # Exact quoted strings (page_title, labels, etc.)
    ('"TalentLens AI"',          '"HirangAI"'),
    # Score naming first (most specific)
    ("TalentLens Match Score",   "Candidate Fit Score"),
    ("TalentLens Score",         "Candidate Fit Score"),
    # File-name tokens
    ("TalentLens_Rankings",      "HirangAI_Rankings"),
    ("TalentLens_Report_",       "HirangAI_Report_"),
    ("TalentLens_Shortlist",     "HirangAI_Shortlist"),
    # General brand
    ("TalentLens AI",            "HirangAI"),
    ("TalentLens",               "HirangAI"),
    # Column / label abbreviation
    ("TL Score",                 "Fit Score"),
    # Hero subtitle
    ("Resume Intelligence & Candidate Evaluation Platform",
     "Choose Better. Hire Smarter."),
    ("Resume Intelligence \u0026 Candidate Evaluation Platform",
     "Choose Better. Hire Smarter."),
    # Hero badge text
    ("AI Hiring Intelligence",   "HirangAI"),
    # Ranking mode description snippet
    ("TL \u00d7 70%",            "Fit \u00d7 70%"),
    ("TL \u00d7 0.70",           "Fit \u00d7 0.70"),
    # Shortlist card "TL " prefix inside HTML f-strings — handled below
]

for old, new in pairs:
    count = src.count(old)
    if count:
        print(f"  {count:>3}x  {old!r}")
        src = src.replace(old, new)

# Fix "TL&nbsp;" inside HTML shortlist cards -> "Fit&nbsp;"
src = re.sub(r'\bTL&amp;nbsp;', "Fit&amp;nbsp;", src)
src = re.sub(r'\bTL&nbsp;', "Fit&nbsp;", src)

# Fix "TL {value}" patterns inside f-strings (e.g. f"TL {_stl}")
# Only replace when TL is followed by a space and a Python expression/digit
src = re.sub(r'"TL\s+\{', '"Fit {', src)
src = re.sub(r"'TL\s+\{", "'Fit {", src)
# Fix literal "TL " at start of f-string segment (HTML)
src = re.sub(r'>TL\s+\{', '>Fit {', src)

assert len(src) > 0
with open("app.py", "w", encoding="utf-8") as f:
    f.write(src)

print(f"\nDone. File size: {len(src):,} chars (was {original_len:,})")
