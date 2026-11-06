"""Exercise the feedback loop with simulated Latent answers drawn from hidden truth.

Each synthetic persona "plays Latent": for every skill shown on its panel it answers from hidden truth.
--labels said: the level the person would accept (would_accept_levels, flattery included), like a real answer.
--labels ability: the hidden true level, like an expert audit. The gap between the two is the answer bias.
Starting from a deliberately wrong tau and shift, the loop runs a few weekly rounds so you can watch it walk
back within its step limits. Read-only: never writes the live overlay.

Usage: uv run python -m imocha_raven.eval.simulate_feedback [--labels said|ability] [--start-tau 0.75] [--rounds 6]
"""

import argparse
import json
from pathlib import Path

from ..feedback import AUTO, TARGET, Item, run, tau_curve
from .score import load_truth, rows_of

RUN = Path(__file__).resolve().parents[3] / "runs" / "latest"


def sim_items(labels: str = "said") -> list[Item]:
    out = []
    for f in sorted((RUN / "per_person").glob("P0[0-9][0-9].json")):
        rows = rows_of(load_truth(f.stem))
        for sk in json.loads(f.read_text())["skills"]:
            r3 = next((j for j in sk["judges"] if j["judge"] == "raven3"), None)
            row = rows.get(sk["skill_id"])
            if not r3 or not r3.get("trace") or not row:
                continue
            t = r3["trace"]
            implied = row.get("true_level")
            ok = row.get("would_accept_levels") or []
            if labels == "said" and ok and t.get("best") is not None:
                implied = t["best"] if t["best"] in ok else min(ok, key=lambda x: abs(x - t["best"]))
            out.append(Item(skill_id=sk["skill_id"], scale_max=sk["scale_max"], p_yes=float(t.get("p_yes") or 0),
                            level=t.get("best"), level_evidence=bool(t.get("level_evidence", True)),
                            has_skill=bool(row["has_skill"]), implied_level=implied, source=f"sim:{labels}"))
    return out


def replay(labels: str = "said", start_tau: float = 0.75, start_shift: int = 1, rounds: int = 6) -> dict:
    """Everything the engine-room replay needs: the curve the loop looks at and each round's move."""
    items = sim_items(labels)
    cur, out = {"tau": start_tau, "shift": start_shift, "history": []}, []
    for i in range(1, rounds + 1):
        r = run(items, apply=False, start=cur)
        out.append({"round": i, "tau_from": r["tau"]["from"], "tau_to": r["tau"]["to"], "tau_why": r["tau"]["why"],
                    "shift_from": r["shift"]["from"], "shift_to": r["shift"]["to"], "shift_why": r["shift"]["why"],
                    "precision_at_tau": r["precision_at_current_tau"]})
        cur = {"tau": r["tau"]["to"], "shift": r["shift"]["to"], "history": []}
    return {"labels": labels, "n": len(items), "target": TARGET, "guardrails": AUTO, "curve": tau_curve(items), "rounds": out}


def write_replays():
    """runs/latest/feedback_replay.json: both label modes from both sides, for the app."""
    data = {f"{lab}_{side}": replay(lab, t, 1) for lab in ("said", "ability") for side, t in (("high", 0.75), ("low", 0.10))}
    (RUN / "feedback_replay.json").write_text(json.dumps(data, indent=1))
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-tau", type=float, default=0.75)
    ap.add_argument("--start-shift", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--labels", choices=["said", "ability"], default="said")
    ap.add_argument("--write", action="store_true", help="write runs/latest/feedback_replay.json for the app")
    a = ap.parse_args()
    if a.write:
        write_replays()
        print("wrote", RUN / "feedback_replay.json")
    items = sim_items(a.labels)
    print(f"simulated labels: {len(items)} ({a.labels}: skills shown on synthetic panels, answered from hidden truth)")
    cur = {"tau": a.start_tau, "shift": a.start_shift, "history": []}
    for i in range(1, a.rounds + 1):
        r = run(items, apply=False, start=cur)
        print(f"round {i}: tau {r['tau']['from']} -> {r['tau']['to']} | shift {r['shift']['from']} -> {r['shift']['to']}"
              f" | precision now {r['precision_at_current_tau']} | {r['tau']['why']}")
        cur = {"tau": r["tau"]["to"], "shift": r["shift"]["to"], "history": []}
    print("shift note:", r["shift"]["why"])


if __name__ == "__main__":
    main()
