"""Shared helpers: taxonomy lookups, source groups, dates, consent, send policy."""

import json
import re
from datetime import date

from ..types import Bundle, Citation, Claim, Decision

EU = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU",
      "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}
GROUP_OF = {"assessments": "measured", "github": "work", "github_public": "work", "jira": "work", "servicenow": "work", "salesforce": "work",
            "authored_doc": "authored", "hcm": "org", "certs": "third_party", "lms": "training", "cv": "self"}
GROUP_RANK = ["measured", "work", "authored", "org", "third_party", "self", "training"]  # conflict order, STEP-4.7


def skill_index(taxonomy: dict) -> dict[str, dict]:
    return {s["skill_id"]: s for s in taxonomy["skills"]}


def scale_levels(taxonomy: dict, skill_id: str) -> list[dict]:
    fam = next(f for f in taxonomy["skill_families"] if f["family_id"] == skill_index(taxonomy)[skill_id]["family_id"])
    return next(s for s in taxonomy["scales"] if s["scale_id"] == fam["scale_id"])["levels"]


def scale_max(taxonomy: dict, skill_id: str) -> int:
    return len(scale_levels(taxonomy, skill_id))


def is_generic(taxonomy: dict, skill_id: str) -> bool:
    s = skill_index(taxonomy)[skill_id]
    ex = {e.lower() for e in taxonomy.get("exclude_list", [])}
    return bool(s.get("generic")) or s["name"].lower() in ex


def src_of(bundle: Bundle) -> dict:
    return {s.source_id: s for s in bundle.sources}


def _verified_cert(text: str, quote: str) -> bool:
    i = text.find(quote)
    if i < 0:
        return False
    a, b = text.rfind("{", 0, i), text.find("}", i)
    return '"verification_status": "verified"' in text[a:b if b > 0 else len(text)]


def group_of(claim: Claim, bundle: Bundle) -> str:
    """Independence group (S3). Unchecked certs and listed/self-rated items count as self-stated."""
    s = src_of(bundle).get(claim.source_id)
    g = GROUP_OF.get(s.source_type if s else "", "self")
    if claim.evidence_type in ("listed", "self_rating"):
        return "self"
    if claim.evidence_type == "course":
        return "training"
    if g == "third_party" and not _verified_cert(s.text, claim.quote):
        return "self"
    return g


def cluster_of(claim: Claim, source) -> str:
    """Correlated-evidence cluster: one repo / ticket project / source (CV versions share a lineage)."""
    ref = claim.ref or ""
    proj = ref.split("#")[0] if "#" in ref else ref.rsplit("-", 1)[0] if "-" in ref else ""
    own = (claim.group_key or "").startswith("self:")
    return f"{source.source_type}:{source.lineage_key or source.source_id}" if own or not claim.group_key \
        else f"{claim.group_key}|{proj}"


def parse_date(s: str | None) -> date | None:
    m = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?", s or "")
    return date(int(m[1]), int(m[2]), int(m[3] or 15)) if m else None


def claim_date(claim: Claim, bundle: Bundle) -> date | None:
    s = src_of(bundle).get(claim.source_id)
    return parse_date(claim.date) or parse_date(s.received if s else None)


def age_years(d: date | None, bundle: Bundle) -> float:
    ref = parse_date(bundle.as_of) or date(2026, 11, 5)
    return 0.0 if d is None else max(0.0, (ref - d).days / 365.25)


def usable(claims: list[Claim]) -> list[Claim]:
    """No quote, no record: verified, mapped claims only, in a stable order."""
    c = [x for x in claims if x.quote_verified and x.skill_id]
    return sorted(c, key=lambda x: (x.skill_id, x.source_id, x.date or "", x.quote))


def messaging_ok(bundle: Bundle) -> bool:
    """HCM consent: notice given, no opt-out, EU needs explicit opt-in."""
    if bundle.messaging_allowed is False:
        return False
    for s in bundle.sources:
        if s.source_type != "hcm":
            continue
        try:
            h = json.loads(s.text)
        except json.JSONDecodeError:
            continue
        c = h.get("messaging_consent") or {}
        if h.get("country") in EU and not c.get("eu_opt_in"):
            return False
        if c.get("opted_out") or c.get("notice_given") is False:
            return False
    return True


def citations(claims: list[Claim], bundle: Bundle, n: int = 3) -> list[Citation]:
    """Up to n distinct verified quotes, strongest group first."""
    seen, out = set(), []
    key = lambda c: (GROUP_RANK.index(group_of(c, bundle)), c.evidence_type != "applied", -(c.level_seen or 0), c.quote)
    for c in sorted(claims, key=key):
        if c.quote_verified and c.quote not in seen:
            seen.add(c.quote)
            out.append(Citation(source_id=c.source_id, quote=c.quote))
    return out[:n]


def apply_policy(decisions: list[Decision], bundle: Bundle, taxonomy: dict) -> list[Decision]:
    """Consent gate and generic-skill exclusion. Runs last, for every engine."""
    ok = messaging_ok(bundle)
    out = []
    for d in decisions:
        if not ok:
            d = d.model_copy(update={"action": "do_not_message", "level": None, "reason": "No messaging consent in HCM."})
        elif d.action == "send" and is_generic(taxonomy, d.skill_id):
            d = d.model_copy(update={"action": "not_extract", "level": None, "reason": "Generic skill on the exclude list."})
        out.append(d.model_copy(update={"evidence": d.evidence[:3]}))
    return out


def cap_message(decisions: list[Decision], n: int = 3) -> list[Decision]:
    """One message: the n sends with highest p_yes (ties: skill_id)."""
    s = [d for d in decisions if d.action == "send"]
    return sorted(s, key=lambda d: (-(d.p_yes or 0), d.skill_id))[:n]
