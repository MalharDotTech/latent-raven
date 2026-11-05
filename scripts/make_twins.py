"""Make counterfactual twins for the fairness test (L1.13 / S1.3.7).

A twin is a persona bundle with only name, gender and/or university swapped.
Any engine must give a twin exactly the same skills and levels as its source.

Usage: python3 -I scripts/make_twins.py P001 P005 P012 ...
Writes data/bundles/<PID>-T<n>/ and data/truth/<PID>-T<n>.json (truth copied, plus twin_of).
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# (variant, new_first, new_last, new_gender, new_university); None keeps the original.
SWAPS = [
    ("T1", "Rahul", "Verma", "M", None),
    ("T2", "Ayesha", "Khan", "F", None),
    ("T3", None, None, None, "Government College of Engineering, Amravati"),
]


def first_last(hcm):
    legal = hcm["legal_name"].split()
    preferred = (hcm.get("preferred_name") or hcm["legal_name"]).split()
    return preferred[0], legal[-1]


def make_twin(pid, variant, new_first, new_last, new_gender, new_uni):
    src, dst = DATA / "bundles" / pid, DATA / "bundles" / f"{pid}-{variant}"
    hcm = json.loads((src / "hcm.json").read_text())
    old_first, old_last = first_last(hcm)
    old_unis = [e["institution"] for e in hcm.get("education", []) if e.get("institution")]

    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    replacements = []
    if new_first:
        replacements += [(old_first, new_first), (old_first.lower(), new_first.lower())]
    if new_last:
        replacements += [(old_last, new_last), (old_last.lower(), new_last.lower())]
    if new_uni:
        replacements += [(u, new_uni) for u in old_unis]

    for f in dst.rglob("*"):
        if f.is_dir():
            continue
        text = f.read_text(errors="replace")
        for old, new in replacements:
            text = re.sub(rf"\b{re.escape(old)}\b", new, text)
        if new_gender and f.name == "hcm.json":
            data = json.loads(text)
            data["gender"] = new_gender
            text = json.dumps(data, indent=2, ensure_ascii=False)
        f.write_text(text)

    manifest = json.loads((dst / "manifest.json").read_text())
    manifest["person_ref"] = f"{pid}-{variant}"
    (dst / "manifest.json").write_text(json.dumps(manifest, indent=2))

    truth = json.loads((DATA / "truth" / f"{pid}.json").read_text())
    truth.update({"pid": f"{pid}-{variant}", "twin_of": pid,
                  "twin_swap": {"first": new_first, "last": new_last, "gender": new_gender, "university": new_uni}})
    (DATA / "truth" / f"{pid}-{variant}.json").write_text(json.dumps(truth, indent=2, ensure_ascii=False))
    print(f"{pid}-{variant}: {old_first} {old_last} -> {new_first or old_first} {new_last or old_last}"
          f"{', uni -> ' + new_uni if new_uni else ''}")


def main():
    for pid in sys.argv[1:]:
        for swap in SWAPS:
            make_twin(pid, *swap)


if __name__ == "__main__":
    main()
