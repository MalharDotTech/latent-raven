"""Raven 3 (E2): calibrated evidence fusion, v0. Clusters, one half-life, noisy-OR, argmax P(accepted), threshold tau."""

import json
import math
import os
from collections import defaultdict
from pathlib import Path

from ..types import Bundle, Claim, Decision, EngineResult
from .common import (age_years, apply_policy, citations, claim_date, cluster_of, group_of, scale_max, skill_index, src_of,
                     usable)

TAU_FILE = Path(__file__).with_name("raven3_tau.json")  # offline baseline, fitted by eval.run on the calibration half
FEEDBACK_FILE = Path(__file__).with_name("raven3_feedback.json")  # live overlay written by feedback.py (tau, shift only)

# Parameters below are HUMAN-ONLY: the feedback loop (feedback.py) never changes them. See feedback.HUMAN_ONLY.
HALF_LIFE_Y = 2.5
SAME_CLUSTER = 0.3  # duplicate quote 0, same project/source 0.3, different 1
Q = {"test": 0.85, "applied": 0.8, "authored_doc": 0.7, "cert": 0.6, "other": 0.2, "course": 0.15, "listed": 0.12,
     "self_rating": 0.1}
GROUP_CAP = {"self": 0.3, "training": 0.15}
LEVEL_NOISE = [0.6, 0.25, 0.1, 0.05]  # P(true level | record shows level) by distance


def load_cfg() -> dict:
    """tau and shift: offline baseline from eval.run, overlaid with feedback-loop values unless RAVEN3_FEEDBACK=0.
    eval.run always passes tau/shift explicitly, so offline scores never depend on live feedback."""
    cfg = json.loads(TAU_FILE.read_text()) if TAU_FILE.exists() else {"tau": 0.9, "shift": 0}
    if FEEDBACK_FILE.exists() and os.environ.get("RAVEN3_FEEDBACK", "1") != "0":
        fb = json.loads(FEEDBACK_FILE.read_text())
        cfg = {**cfg, "tau": fb.get("tau", cfg["tau"]), "shift": fb.get("shift", cfg.get("shift", 0))}
    return cfg


def accepted(level: int, top: int) -> list[int]:
    """Levels at which the person would answer Yes to `level`: +-1 on K4, exact on K3."""
    return [level] if top <= 3 else [k for k in (level - 1, level, level + 1) if 1 <= k <= top]


class Raven3:
    name = "raven3"

    def __init__(self, tau: float | None = None, shift: int | None = None):
        cfg = load_cfg()
        self.tau = cfg["tau"] if tau is None else tau
        self.shift = cfg.get("shift", 0) if shift is None else shift  # readers under-level applied work

    def candidates(self, bundle: Bundle, taxonomy: dict, claims: list[Claim]) -> list[Decision]:
        """Best level and p_yes per skill, before any threshold. Action is hold here."""
        by = defaultdict(list)
        for c in usable(claims):
            by[c.skill_id].append(c)
        src = src_of(bundle)
        out = []
        for sid, cl in sorted(by.items()):
            top = scale_max(taxonomy, sid)
            rows = []
            for c in cl:
                g = group_of(c, bundle)
                q = min(Q.get(c.evidence_type, 0.2), GROUP_CAP.get(g, 1.0))
                q *= 0.5 ** (age_years(claim_date(c, bundle), bundle) / HALF_LIFE_Y)
                s = src[c.source_id]
                rows.append((-q, s.lineage_key or s.source_id, cluster_of(c, s), c))
            rows.sort(key=lambda r: (r[0], r[3].quote))
            seen_q, seen_cluster, miss, contrib, leveled = set(), set(), 1.0, [], False
            lp = [0.0] * top
            for nq, lin, cluster, c in rows:
                key = (lin, " ".join(c.quote.lower().split()))
                d = 0.0 if key in seen_q else (SAME_CLUSTER if cluster in seen_cluster else 1.0)
                seen_q.add(key)
                seen_cluster.add(cluster)
                w = -nq * d
                miss *= 1 - w
                contrib.append({"type": c.evidence_type, "group": group_of(c, bundle), "q": round(-nq, 3),
                                "discount": d, "weight": round(w, 3), "level": c.level_seen})
                if c.level_seen and w > 0:
                    leveled = True
                    seen = min(top, c.level_seen + (self.shift if c.evidence_type == "applied" else 0))
                    for k in range(top):
                        lp[k] += w * math.log(LEVEL_NOISE[min(abs(k + 1 - seen), 3)])
            ph = 1 - miss
            m = max(lp)
            pl = [math.exp(x - m) for x in lp]
            z = sum(pl)
            pl = [x / z for x in pl]
            best = max(range(1, top + 1), key=lambda l: (sum(pl[k - 1] for k in accepted(l, top)), l))
            p = ph * sum(pl[k - 1] for k in accepted(best, top))
            out.append(Decision(person_ref=bundle.person_ref, skill_id=sid, action="hold", level=best, p_yes=round(p, 4),
                                evidence=citations(cl, bundle), reason=f"P(has)={ph:.2f}, level dist={[round(x, 2) for x in pl]}",
                                trace={"p_has": round(ph, 4), "level_dist": [round(x, 4) for x in pl], "best": best,
                                       "accepted": accepted(best, top), "p_yes": round(p, 4), "tau": self.tau,
                                       "shift": self.shift, "level_evidence": leveled, "evidence": contrib[:10]}))
        return out

    def infer(self, bundle: Bundle, taxonomy: dict, claims: list[Claim]) -> EngineResult:
        ds = []
        for d in self.candidates(bundle, taxonomy, claims):
            if not d.trace.get("level_evidence", True):
                # No record shows a level: a middle-level guess is not a reading. Contract: no level evidence, no level.
                d = d.model_copy(update={"level": None, "reason": f"No level evidence. {d.reason}"})
            elif d.p_yes >= self.tau:
                d = d.model_copy(update={"action": "send", "reason": f"p_yes {d.p_yes} >= tau {self.tau}. {d.reason}"})
            else:
                d = d.model_copy(update={"level": None, "reason": f"p_yes {d.p_yes} < tau {self.tau}. {d.reason}"})
            ds.append(d)
        un = sorted({c.skill_phrase for c in claims if c.quote_verified and not c.skill_id})
        return EngineResult(engine=self.name, person_ref=bundle.person_ref, decisions=apply_policy(ds, bundle, taxonomy),
                            unmatched_skills=un)
