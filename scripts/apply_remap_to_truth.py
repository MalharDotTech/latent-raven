"""Apply data/notes/id_remap.json (from fix_structure.py) to truth files, so IDs cited in truth match the bundles.

Usage: python3 -I scripts/apply_remap_to_truth.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
remap = json.loads((ROOT / "data/notes/id_remap.json").read_text())

for pid, mapping in remap.items():
    path = ROOT / "data/truth" / f"{pid}.json"
    text = path.read_text()
    # Longest keys first; single pass so a new ID is never remapped again.
    keys = sorted((k for k in mapping if k), key=len, reverse=True)
    if not keys:
        print(f"{pid}: 0 replacements")
        continue
    pattern = re.compile(r"(?<![\w-])(" + "|".join(re.escape(k) for k in keys) + r")(?![\w-])")
    new, n = pattern.subn(lambda m: mapping[m.group(1)], text)
    if n:
        json.loads(new)
        path.write_text(new)
    print(f"{pid}: {n} replacements")
