"""Stage 1: load bundles and the taxonomy. Never touches data/truth/."""

import json
from pathlib import Path

from .types import Bundle, Source

ROOT = Path(__file__).resolve().parents[2]
BUNDLES = ROOT / "data" / "bundles"
REAL = ROOT / "data" / "real" / "bundles"
TAXONOMY = ROOT / "data" / "taxonomy" / "customer_taxonomy.json"


def load_taxonomy() -> dict:
    return json.loads(TAXONOMY.read_text())


def _consent(text: str) -> bool | None:
    try:
        c = json.loads(text).get("messaging_consent")
    except (json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(c, dict):
        return None
    if c.get("opted_out"):
        return False
    if c.get("notice_given") is False:
        return False
    if c.get("notice_given") is True:
        return True
    return None


def load_bundle(d: str | Path) -> Bundle:
    d = Path(d)
    m = json.loads((d / "manifest.json").read_text())
    sources, allowed = [], None
    for s in m["sources"]:
        p = d / s["path"]
        text = p.read_text(errors="replace") if p.exists() else ""
        if s["source_type"] == "hcm":
            allowed = _consent(text)
        sources.append(Source(source_id=s["source_id"], source_type=s["source_type"], path=s["path"], text=text,
                              received=s.get("received"), lineage_key=s.get("lineage_key")))
    return Bundle(person_ref=m["person_ref"], as_of=m.get("as_of", ""), sources=sources, messaging_allowed=allowed)


def list_bundles(kind: str = "all") -> list[Path]:
    syn = sorted(p for p in BUNDLES.iterdir() if (p / "manifest.json").exists()) if BUNDLES.exists() else []
    real = sorted(p for p in REAL.iterdir() if (p / "manifest.json").exists()) if REAL.exists() else []
    twins = [p for p in syn if "-T" in p.name]
    plain = [p for p in syn if "-T" not in p.name]
    return {"synthetic": plain, "twins": twins, "real": real, "all": plain + twins + real}[kind]
