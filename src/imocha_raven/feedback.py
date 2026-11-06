"""Feedback loop for Raven 3: human answers adjust a small set of parameters, humans own the rest.

Borrowed from RLHF, not RLHF. In RLHF, human preference labels train a reward model that then updates a
policy's weights by gradient steps. Here, human Yes/No and level answers from Latent (and later Teams) act
as the reward signal, but the "policy" is a calibrated rule (send if p_yes >= tau and some record shows a
level), and the only things the signal may move are two scalars, inside guardrails:

    AUTO-TUNED (this module)   tau    send threshold        risk-controlled, min labels, step limit
                               shift  level correction      direction of "too low / too high" answers
    HUMAN-ONLY (never here)    see HUMAN_ONLY below: weights, decay, discounts, noise, Raven 2 rules, taxonomy

Why so narrow: answers are biased (people accept flattering levels, only some people reply, players are not
the employee population), and a loop that can rewrite evidence weights from a few dozen answers will learn
the bias. Two scalars with step limits can be explained to a customer and rolled back in one line.

Usage:
    uv run python -m imocha_raven.feedback --source live            # dry run on pilot.db answers
    uv run python -m imocha_raven.feedback --source live --apply    # write engines/raven3_feedback.json
    uv run python -m imocha_raven.eval.simulate_feedback            # synthetic answers from hidden truth
"""

import argparse
import json
import math
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .engines.raven3 import FEEDBACK_FILE, TAU_FILE, accepted

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "pilot.db"

TARGET = 0.95  # promise: >= 95% of sends answered Yes
Z_ONE_SIDED = 1.645  # 95% one-sided lower bound on precision
AUTO = {
    "tau": {"min": 0.05, "max": 0.95, "max_step": 0.05, "min_labels": 30},
    "shift": {"min": 0, "max": 2, "max_step": 1, "min_labels": 20, "min_misses": 5, "min_lean": 0.6},
}
HUMAN_ONLY = {
    "Q (evidence weights per type)": "Fitting them on self-reports teaches the engine the answer bias; needs audit labels and a shadow run.",
    "GROUP_CAP (self-stated / training caps)": "Trust policy, not a statistic.",
    "SAME_CLUSTER (correlated-evidence discount)": "Needs labelled overlap pairs, not Yes/No answers.",
    "HALF_LIFE_Y (decay)": "Varies by skill type; set with customer L&D.",
    "LEVEL_NOISE (level confusion)": "Needs confirmed levels from audits or assessments.",
    "No level evidence -> hold": "Contract rule. Never tuned away.",
    "Raven 2 rules (floor, caps, decay windows, spread)": "Auditable rulebook and veto; changed only in quarterly review.",
    "Taxonomy, level lines, bands": "Customer HR decision.",
}


@dataclass
class Item:
    """One answered skill, seen through Raven 3."""
    skill_id: str
    scale_max: int
    p_yes: float
    level: int | None  # Raven 3's best level (sent or not)
    level_evidence: bool
    has_skill: bool
    implied_level: int | None  # level the person says is right
    source: str  # live | sim


def correct(it: Item, level: int | None = None) -> bool:
    """Would this send be a Yes? Has the skill and the level is within the accepted band of the implied level."""
    lvl = it.level if level is None else level
    if not it.has_skill or lvl is None:
        return False
    return it.implied_level is None or it.implied_level in accepted(lvl, it.scale_max)


def wilson_lower(k: int, n: int, z: float = Z_ONE_SIDED) -> float:
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    return (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d


def load_live(db: Path = DB) -> list[Item]:
    """Answers from real (non-demo) Latent rounds joined with the panel Raven 3 produced for that person."""
    if not db.exists():
        return []
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    rows = c.execute("""SELECT s.result, a.skill_id, a.has_skill, a.level_feedback, r.panel AS avg, sr.level AS self
        FROM answers a JOIN submissions s ON s.id = a.submission_id
        LEFT JOIN reveals r ON r.submission_id = a.submission_id AND r.skill_id = a.skill_id
        LEFT JOIN self_ratings sr ON sr.submission_id = a.submission_id AND sr.skill_id = a.skill_id
        WHERE s.demo = 0 AND s.status = 'ready'""").fetchall()
    out = []
    for row in rows:
        panel = json.loads(row["result"] or "{}")
        sk = next((s for s in panel.get("skills", []) if s["skill_id"] == row["skill_id"]), None)
        r3 = next((j for j in (sk or {}).get("judges", []) if j["judge"] == "raven3"), None)
        if not r3 or not r3.get("trace"):
            continue
        t = r3["trace"]
        delta = {"too_low": 1, "right": 0, "too_high": -1}.get(row["level_feedback"])
        # "Panel's level is too low" means the person sits above the panel average.
        implied = round(row["avg"]) + delta if row["avg"] is not None and delta is not None else row["self"]
        top = sk["scale_max"]
        out.append(Item(skill_id=row["skill_id"], scale_max=top, p_yes=float(t.get("p_yes") or 0), level=t.get("best"),
                        level_evidence=bool(t.get("level_evidence", True)), has_skill=row["has_skill"] == "yes",
                        implied_level=None if implied is None else max(1, min(top, implied)), source="live"))
    return out


def current() -> dict:
    """Effective config: offline baseline (eval) overlaid with the last applied feedback values."""
    base = json.loads(TAU_FILE.read_text()) if TAU_FILE.exists() else {"tau": 0.9, "shift": 0}
    fb = json.loads(FEEDBACK_FILE.read_text()) if FEEDBACK_FILE.exists() else {}
    return {"tau": fb.get("tau", base["tau"]), "shift": fb.get("shift", base.get("shift", 0)),
            "baseline": {"tau": base["tau"], "shift": base.get("shift", 0)}, "history": fb.get("history", [])}


def tau_curve(items: list[Item]) -> list[dict]:
    """For every candidate tau: how many labelled candidates would be sent, their precision, and its lower bound."""
    cfg = AUTO["tau"]
    scored = [it for it in items if it.level_evidence and it.level is not None]
    out = []
    for t in [round(x / 100, 2) for x in range(int(cfg["min"] * 100), int(cfg["max"] * 100) + 1)]:
        sends = [it for it in scored if it.p_yes >= t]
        k = sum(correct(it) for it in sends)
        out.append({"tau": t, "sends": len(sends), "precision": round(k / len(sends), 4) if sends else None,
                    "lower_bound": round(wilson_lower(k, len(sends)), 4) if sends else None})
    return out


def propose_tau(items: list[Item], tau_now: float) -> tuple[float, str]:
    """Smallest tau whose one-sided 95% lower bound on precision meets TARGET, moved at most max_step."""
    cfg = AUTO["tau"]
    scored = [it for it in items if it.level_evidence and it.level is not None]
    if len(scored) < cfg["min_labels"]:
        return tau_now, f"hold: {len(scored)} labelled Raven 3 candidates < {cfg['min_labels']} needed"
    ok = [pt["tau"] for pt in tau_curve(scored) if pt["sends"] >= 10 and pt["lower_bound"] >= TARGET]
    if ok:
        want, why = ok[0], f"lowest tau with precision lower bound >= {TARGET:.0%} is {ok[0]}"
    else:
        want, why = cfg["max"], f"no tau reaches a {TARGET:.0%} lower bound on {len(scored)} labels: tighten"
    step = max(-cfg["max_step"], min(cfg["max_step"], want - tau_now))
    new = round(min(cfg["max"], max(cfg["min"], tau_now + step)), 4)
    return new, why + (f"; step limited to {step:+.2f}" if abs(want - tau_now) > cfg["max_step"] else "")


def propose_shift(items: list[Item], shift_now: int) -> tuple[int, str]:
    """Move the applied-work level correction only on real misses: levels outside the accepted band.
    Being off-centre inside the +-1 band is by design (Raven 3 picks the level that maximises the band)."""
    cfg = AUTO["shift"]
    rated = [it for it in items if it.has_skill and it.level is not None and it.implied_level is not None]
    if len(rated) < cfg["min_labels"]:
        return shift_now, f"hold: {len(rated)} level answers < {cfg['min_labels']} needed"
    misses = [it for it in rated if it.implied_level not in accepted(it.level, it.scale_max)]
    low = sum(it.implied_level > it.level for it in misses)
    high = len(misses) - low
    if len(misses) < cfg["min_misses"]:
        return shift_now, f"hold: {len(misses)} level misses of {len(rated)} answers, too few to move"
    lean = (low - high) / len(misses)
    if abs(lean) < cfg["min_lean"]:
        return shift_now, f"hold: misses split too low {low} vs too high {high} (lean {lean:+.2f})"
    new = max(cfg["min"], min(cfg["max"], shift_now + (1 if lean > 0 else -1)))
    return new, f"misses lean one way: too low {low} vs too high {high} of {len(rated)} answers (lean {lean:+.2f})"


def run(items: list[Item], apply: bool = False, start: dict | None = None) -> dict:
    cur = start or current()
    tau, tau_why = propose_tau(items, cur["tau"])
    shift, shift_why = propose_shift(items, cur["shift"])
    sends_now = [it for it in items if it.level_evidence and it.p_yes >= cur["tau"]]
    report = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "labels": len(items),
              "sources": sorted({it.source for it in items}),
              "precision_at_current_tau": round(sum(map(correct, sends_now)) / len(sends_now), 4) if sends_now else None,
              "tau": {"from": cur["tau"], "to": tau, "why": tau_why},
              "shift": {"from": cur["shift"], "to": shift, "why": shift_why},
              "human_only_untouched": list(HUMAN_ONLY)}
    if apply and (tau != cur["tau"] or shift != cur["shift"]):
        hist = cur.get("history", []) + [{k: report[k] for k in ("at", "labels", "sources", "tau", "shift")}]
        FEEDBACK_FILE.write_text(json.dumps({"tau": tau, "shift": shift, "updated_at": report["at"], "history": hist[-50:]},
                                            indent=1))
        report["applied"] = True
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", choices=["live"], default="live")
    ap.add_argument("--apply", action="store_true", help="write engines/raven3_feedback.json (default: dry run)")
    args = ap.parse_args()
    print(json.dumps(run(load_live(), apply=args.apply), indent=1))


if __name__ == "__main__":
    main()
