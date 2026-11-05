"""Turn the real people's documents into engine-ready bundles.

Real data is gitignored (data/real/). It never gets a truth file: the only ground truth
for these people is their own Yes/No answer on the engine's output, collected later.

Usage: python3 -I scripts/ingest_real.py
Reads data/real/raw_text/*.txt|md, writes data/real/bundles/R0xx/ in the same layout as
data/bundles/P0xx/ so the same engine and harness run on both.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REAL = ROOT / "data" / "real"
RAW = REAL / "raw_text"
AS_OF = "2026-11-05"

# [rid, role_family, [[source_type, raw_file, received, extraction_note], ...]]
# Kept in gitignored data/real/people.json: raw file names carry real names.
PEOPLE = json.loads((REAL / "people.json").read_text())


def main():
    out = REAL / "bundles"
    # Only rebuild R-bundles; live app submissions share this folder.
    for rid, _, _ in PEOPLE:
        shutil.rmtree(out / rid, ignore_errors=True)
    index = []
    for rid, family, sources in PEOPLE:
        bdir = out / rid
        bdir.mkdir(parents=True)
        manifest = {"person_ref": rid, "customer": "real-pilot", "as_of": AS_OF, "sources": []}
        cv_n = 0
        for stype, raw, received, note in sources:
            if stype == "cv":
                cv_n += 1
                path = f"cv_v{cv_n}.md"
            else:
                (bdir / "docs").mkdir(exist_ok=True)
                path = f"docs/{Path(raw).stem}.md"
            shutil.copy(RAW / raw, bdir / path)
            entry = {"source_id": f"{stype}_{rid}_{cv_n if stype == 'cv' else Path(raw).stem}",
                     "source_type": stype, "path": path, "received": received, "extraction": note}
            if stype == "cv":
                entry["lineage_key"] = f"cv-{rid}"
            manifest["sources"].append(entry)
        (bdir / "manifest.json").write_text(json.dumps(manifest, indent=1))
        index.append({"rid": rid, "role_family": family, "sources": len(sources)})
        print(f"{rid} {family}: {len(sources)} sources")
    (REAL / "index.json").write_text(json.dumps(index, indent=1))


if __name__ == "__main__":
    main()
