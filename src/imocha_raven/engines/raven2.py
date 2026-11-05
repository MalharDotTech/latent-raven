"""Raven 2 (E1): iMocha's reference rules, STEP-3..STEP-5. Deterministic, no LLM.

HUMAN-ONLY: no parameter here is tuned by the feedback loop (feedback.py). Rules change only in review.
"""

from collections import defaultdict

from ..types import Bundle, Claim, Decision, EngineResult
from .common import (age_years, apply_policy, citations, claim_date, group_of, scale_levels, scale_max,
                     skill_index, usable)

ESTABLISH = {"measured", "work", "authored", "org", "third_party"}  # groups that can establish a skill alone


def cap(group: str, taxonomy: dict, sid: str, seen: int | None) -> int | None:
    """STEP-4.2: a record shows at most its source's highest level."""
    if seen is None:
        return None
    lv = scale_levels(taxonomy, sid)
    kind = {x["level_kind"]: x["value"] for x in lv}
    top = {"org": kind["applies_alone"], "self": kind["applies_alone"],
           "training": kind.get("knows", 0)}.get(group, len(lv))
    return min(seen, top) or None


class Raven2:
    name = "raven2"

    def _decide(self, sid, cl, bundle, taxonomy) -> Decision:
        sk = skill_index(taxonomy)[sid]
        window = sk["decay_hint_years"]
        top = scale_max(taxonomy, sid)
        cur = [c for c in cl if age_years(claim_date(c, bundle), bundle) <= window]
        trace = {"window_years": window, "scale_max": top, "records_total": len(cl), "records_in_window": len(cur)}
        mk = lambda a, r, lvl=None, ev=None, **t: Decision(person_ref=bundle.person_ref, skill_id=sid, action=a, level=lvl,
                                                           reason=r, evidence=citations(ev or cl, bundle),
                                                           trace={**trace, **t})
        if not cur:
            return mk("hold", f"No evidence inside the {window}y decay window.", rule="decay")
        rec = [(group_of(c, bundle), cap(group_of(c, bundle), taxonomy, sid, c.level_seen), c) for c in cur]
        trace["records"] = [{"group": g, "level": lv, "type": c.evidence_type} for g, lv, c in rec][:12]
        groups = {g for g, _, _ in rec}
        est = groups & ESTABLISH
        measured = [(lv, c) for g, lv, c in rec if g == "measured" and lv and age_years(claim_date(c, bundle), bundle) < 2]
        months = lambda L: {(claim_date(c, bundle).strftime("%Y-%m")) for g, lv, c in rec
                            if g == "work" and lv and lv >= L and claim_date(c, bundle)
                            and age_years(claim_date(c, bundle), bundle) <= 2}
        work_months = months(1)
        trace.update(groups=sorted(groups), establishing=sorted(est), measured=len(measured), work_months=len(work_months))
        high = (bool(measured) or len(work_months) >= 3
                or (bool({"work", "authored"} & groups) and len(est) >= 2)
                or ("third_party" in groups and len(est) >= 2))
        if not high:
            return mk("hold", "Not High: no measured result, sustained work, or two establishing groups.", rule="not_high")
        floor = 0
        for L in range(top, 0, -1):
            backed = {g for g, lv, _ in rec if lv and lv >= L}
            if len(backed) >= 2 or any(lv >= L for lv, _ in measured) or len(months(L)) >= 3:
                floor = L
                break
        if not floor:
            return mk("hold", "No floor: no level backed by 2+ groups, a measured result, or 3+ months of work.", rule="no_floor")
        ceiling = max(lv for _, lv, _ in rec if lv)
        if measured:
            lvl = max(lv for lv, _ in measured)
            if any(lv and abs(lv - lvl) >= 2 for g, lv, _ in rec if g != "measured"):
                return mk("hold", "Another group sits 2+ levels from the measured result.", rule="measured_conflict",
                          floor=floor, ceiling=ceiling)
        else:
            gap = ceiling - floor
            if gap >= 3:
                return mk("hold", f"Ceiling {ceiling} - floor {floor} >= 3: evidence disagrees.", rule="spread",
                          floor=floor, ceiling=ceiling)
            lvl = floor + 1 if gap == 2 else floor
        lvl = min(lvl, top)
        return mk("send", f"Floor {floor}, ceiling {ceiling}, groups {sorted(groups)}.", lvl, rule="send",
                  floor=floor, ceiling=ceiling)

    def infer(self, bundle: Bundle, taxonomy: dict, claims: list[Claim]) -> EngineResult:
        by = defaultdict(list)
        for c in usable(claims):
            by[c.skill_id].append(c)
        ds = [self._decide(sid, cl, bundle, taxonomy) for sid, cl in sorted(by.items())]
        un = sorted({c.skill_phrase for c in claims if c.quote_verified and not c.skill_id})
        return EngineResult(engine=self.name, person_ref=bundle.person_ref, decisions=apply_policy(ds, bundle, taxonomy),
                            unmatched_skills=un)
