"""Stage 4: skill_phrase -> skill_id via names, aliases, ambiguity rules and the exclude list."""

import re

from .types import Bundle, Claim


def _n(s: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", " ", s.lower()).strip()


def _strip(s: str) -> str:
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"\b(v?\d+(\.\d+)*|basic|advanced|intermediate|certified|programming|language)\b", " ", s.lower())
    return _n(s)


class Mapper:
    def __init__(self, taxonomy: dict):
        self.tax = taxonomy
        self.exclude = {_n(x) for x in taxonomy.get("exclude_list", [])}
        self.forms: dict[str, str] = {}  # normalised surface form -> skill_id
        self.raw: dict[str, list[tuple[str, str]]] = {}  # normalised -> [(exact surface, skill_id)]
        self.ambiguous: set[str] = set()
        self.family = {s["skill_id"]: s["family_id"] for s in taxonomy["skills"]}
        self.names = {s["skill_id"]: s["name"] for s in taxonomy["skills"]}
        for s in taxonomy["skills"]:
            for surf in [s["name"], *s.get("aliases", [])]:
                self.forms.setdefault(_n(surf), s["skill_id"])
                self.raw.setdefault(_n(surf), []).append((surf, s["skill_id"]))
            for a in s.get("ambiguous_with", []):
                self.ambiguous.add(_n(a["phrase"]))

    def map_phrase(self, phrase: str, context: str = "") -> str | None:
        n = _n(phrase)
        if not n or n in self.exclude:
            return None
        sid = self.forms.get(n) or self.forms.get(_strip(phrase))
        if not sid:
            return None
        if n in self.ambiguous or len(n) <= 2:
            # ambiguous surface: need the canonical casing and, for very short names, a same-family cue
            if not any(surf == phrase.strip() for surf, _ in self.raw.get(n, [])):
                return None
            if len(n) <= 2:
                cue = [self.names[k] for k, f in self.family.items() if f == self.family[sid] and k != sid]
                if not any(re.search(rf"\b{re.escape(c)}\b", context, re.I) for c in cue):
                    return None
        return sid


def map_claims(claims: list[Claim], taxonomy: dict, bundle: Bundle | None = None) -> list[str]:
    """Set skill_id in place. Returns unmatched phrases (deduped)."""
    m = Mapper(taxonomy)
    ctx = {s.source_id: s.text for s in bundle.sources} if bundle else {}
    unmatched: list[str] = []
    for c in claims:
        c.skill_id = m.map_phrase(c.skill_phrase, ctx.get(c.source_id, c.quote))
        if c.skill_id is None and c.skill_phrase not in unmatched:
            unmatched.append(c.skill_phrase)
    return unmatched
