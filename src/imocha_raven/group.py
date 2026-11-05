"""Stage 5: independence groups. Same group = not independent evidence."""

from .types import Bundle, Claim
from .verify import norm

SELF = {"cv", "authored_doc", "hcm"}  # the person's own words


def group_key(person_ref: str, source_type: str, source_id: str, lineage_key: str | None) -> str:
    if source_type in SELF:
        return f"self:{person_ref}"
    return f"{source_type}:{lineage_key or source_id}"


def assign_groups(bundle: Bundle, claims: list[Claim]) -> list[Claim]:
    """Set group_key; drop repeats of the same work item (PR/ticket) for the same skill within a group."""
    src = {s.source_id: s for s in bundle.sources}
    out, seen = [], set()
    for c in claims:
        s = src.get(c.source_id)
        c.group_key = group_key(bundle.person_ref, s.source_type, s.source_id, s.lineage_key) if s else f"unknown:{c.source_id}"
        k = (c.group_key, c.ref or norm(c.quote), c.skill_id or c.skill_phrase.lower())
        if k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out
