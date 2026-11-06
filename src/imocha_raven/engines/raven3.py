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

    def score_skill(self, sid: str, cl: list[Claim], bundle: Bundle, taxonomy: dict) -> tuple[Decision, dict]:
        """One skill end to end. Returns the candidate decision (action hold, before tau) and every intermediate
        number, so the explanation shown in the app is the computation itself, not a re-implementation."""
        top = scale_max(taxonomy, sid)
        src = src_of(bundle)
        rows = []
        for c in cl:
            g = group_of(c, bundle)
            base = Q.get(c.evidence_type, 0.2)  # P1 evidence weight by type
            cap = GROUP_CAP.get(g, 1.0)  # P2 cap for self-stated / training groups
            age = age_years(claim_date(c, bundle), bundle)
            decay = 0.5 ** (age / HALF_LIFE_Y)  # P3 one exponential half-life
            q = min(base, cap) * decay
            s = src[c.source_id]
            rows.append({"q": q, "lin": s.lineage_key or s.source_id, "cluster": cluster_of(c, s), "claim": c,
                         "group": g, "base": base, "cap": cap, "age": age, "decay": decay})
        rows.sort(key=lambda r: (-r["q"], r["claim"].quote))
        seen_q, seen_cluster, miss, leveled = set(), set(), 1.0, False
        lp = [0.0] * top
        steps = []
        for r in rows:
            c = r["claim"]
            key = (r["lin"], " ".join(c.quote.lower().split()))
            # P4 dependence discount: duplicate quote 0, same cluster SAME_CLUSTER, new cluster 1
            d, why = (0.0, "duplicate") if key in seen_q else \
                (SAME_CLUSTER, "same cluster") if r["cluster"] in seen_cluster else (1.0, "new cluster")
            seen_q.add(key)
            seen_cluster.add(r["cluster"])
            w = r["q"] * d
            miss *= 1 - w  # P5 noisy-OR: P(has) = 1 - prod(1 - w)
            seen = None
            if c.level_seen and w > 0:
                leveled = True
                # P7 shift: the reader under-levels applied work; P6 level noise turns a reading into a likelihood
                seen = min(top, c.level_seen + (self.shift if c.evidence_type == "applied" else 0))
                for k in range(top):
                    lp[k] += w * math.log(LEVEL_NOISE[min(abs(k + 1 - seen), 3)])
            steps.append({"quote": c.quote[:160], "source_id": c.source_id, "type": c.evidence_type, "group": r["group"],
                          "cluster": r["cluster"], "base_q": r["base"], "group_cap": r["cap"], "age_years": round(r["age"], 2),
                          "decay": round(r["decay"], 4), "q": round(r["q"], 4), "discount": d, "discount_why": why,
                          "weight": round(w, 4), "p_has_so_far": round(1 - miss, 4), "level_seen": c.level_seen,
                          "level_used": seen, "loglik_so_far": [round(x, 4) for x in lp]})
        ph = 1 - miss
        m = max(lp)
        pl = [math.exp(x - m) for x in lp]
        z = sum(pl)
        pl = [x / z for x in pl]  # P8 level posterior (product of experts, flat prior)
        band = {lvl: sum(pl[k - 1] for k in accepted(lvl, top)) for lvl in range(1, top + 1)}  # P9
        best = max(range(1, top + 1), key=lambda lvl: (band[lvl], lvl))  # P10 l* = argmax P(accepted)
        p = ph * band[best]  # P11 p_yes = P(has) x P(accepted at l*)
        contrib = [{k: st[k] for k in ("type", "group", "q", "discount", "weight")} | {"level": st["level_seen"]}
                   for st in steps]
        trace = {"p_has": round(ph, 4), "level_dist": [round(x, 4) for x in pl], "best": best,
                 "accepted": accepted(best, top), "p_yes": round(p, 4), "tau": self.tau, "shift": self.shift,
                 "level_evidence": leveled, "evidence": contrib[:10]}
        dec = Decision(person_ref=bundle.person_ref, skill_id=sid, action="hold", level=best, p_yes=round(p, 4),
                       evidence=citations(cl, bundle), reason=f"P(has)={ph:.2f}, level dist={[round(x, 2) for x in pl]}",
                       trace=trace)
        detail = {"skill_id": sid, "scale_max": top, "records": steps, "p_has": round(ph, 4),
                  "loglik": [round(x, 4) for x in lp], "level_dist": trace["level_dist"],
                  "band_prob": {k: round(v, 4) for k, v in band.items()}, "best": best,
                  "accepted": trace["accepted"], "p_yes": round(p, 4), "tau": self.tau, "shift": self.shift,
                  "level_evidence": leveled}
        return dec, detail

    def candidates(self, bundle: Bundle, taxonomy: dict, claims: list[Claim]) -> list[Decision]:
        """Best level and p_yes per skill, before any threshold. Action is hold here."""
        by = defaultdict(list)
        for c in usable(claims):
            by[c.skill_id].append(c)
        return [self.score_skill(sid, cl, bundle, taxonomy)[0] for sid, cl in sorted(by.items())]

    @staticmethod
    def decide(d: Decision, tau: float) -> Decision:
        """P12 no level evidence -> hold; P13 tau gate."""
        if not d.trace.get("level_evidence", True):
            # No record shows a level: a middle-level guess is not a reading. Contract: no level evidence, no level.
            return d.model_copy(update={"level": None, "reason": f"No level evidence. {d.reason}"})
        if d.p_yes >= tau:
            return d.model_copy(update={"action": "send", "reason": f"p_yes {d.p_yes} >= tau {tau}. {d.reason}"})
        return d.model_copy(update={"level": None, "reason": f"p_yes {d.p_yes} < tau {tau}. {d.reason}"})

    def explain(self, bundle: Bundle, taxonomy: dict, claims: list[Claim], skill_id: str) -> dict | None:
        """Step-by-step record of how Raven 3 decides one skill for one person (for the engine-room replay)."""
        cl = [c for c in usable(claims) if c.skill_id == skill_id]
        if not cl:
            return None
        cand, detail = self.score_skill(skill_id, cl, bundle, taxonomy)
        final = apply_policy([self.decide(cand, self.tau)], bundle, taxonomy)[0]
        return detail | {"person_ref": bundle.person_ref, "action": final.action, "level": final.level,
                         "reason": final.reason}

    def infer(self, bundle: Bundle, taxonomy: dict, claims: list[Claim]) -> EngineResult:
        ds = [self.decide(d, self.tau) for d in self.candidates(bundle, taxonomy, claims)]
        un = sorted({c.skill_phrase for c in claims if c.quote_verified and not c.skill_id})
        return EngineResult(engine=self.name, person_ref=bundle.person_ref, decisions=apply_policy(ds, bundle, taxonomy),
                            unmatched_skills=un)
