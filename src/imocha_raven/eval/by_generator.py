"""Self-agreement check: do engines (Claude reader) score better on Claude-written personas?

Slices runs/latest/decisions by which model family generated the persona.
Usage: uv run python -m imocha_raven.eval.by_generator
"""

import json
from pathlib import Path

from imocha_raven.eval.score import load_truth, rows_of, is_yes, split_of, wilson

RUN = Path(__file__).resolve().parents[3] / "runs" / "latest"
BATCH_FAMILY = {"A": "claude", "C": "claude", "E": "claude",
                "B": "codex", "D": "codex", "G": "codex",
                "F": "codex+claude repair"}


def batch_of(pid: str) -> str:
    n = int(pid[1:4])
    for batch, lo, hi in [("A", 1, 6), ("B", 7, 11), ("C", 12, 16), ("D", 17, 21),
                          ("E", 22, 27), ("F", 28, 32), ("G", 33, 42)]:
        if lo <= n <= hi:
            return batch
    raise ValueError(pid)


def main():
    stats = {}
    for f in sorted((RUN / "decisions").glob("P0[0-9][0-9].json")):
        pid = f.stem
        rows = rows_of(load_truth(pid))
        oracle_sends = sum(r["oracle"]["action"] == "send" for r in rows.values())
        family = BATCH_FAMILY[batch_of(pid)]
        for result in json.loads(f.read_text()):
            for split in ("all", split_of(pid)):
                s = stats.setdefault((result["engine"], family, split), {"n": 0, "yes": 0, "hit": 0, "oracle": 0, "people": 0})
                s["oracle"] += oracle_sends
                s["people"] += 1
                for d in result["decisions"]:
                    if d["action"] != "send":
                        continue
                    row = rows.get(d["skill_id"])
                    yes = is_yes(d["level"], row)
                    s["n"] += 1
                    s["yes"] += yes
                    s["hit"] += yes and row["oracle"]["action"] == "send"
    out = []
    print(f"{'engine':7} {'family':20} {'split':5} {'people':>6} {'sends':>5} {'precision':>9} {'95% CI':>13} {'coverage':>8}")
    for (engine, family, split), s in sorted(stats.items()):
        p = s["yes"] / s["n"] if s["n"] else 0
        lo, hi = wilson(s["yes"], s["n"])
        cov = s["hit"] / s["oracle"] if s["oracle"] else 0
        print(f"{engine:7} {family:20} {split:5} {s['people']:6} {s['n']:5} {p:9.3f} {f'{lo:.2f}-{hi:.2f}':>13} {cov:8.2f}")
        out.append(dict(engine=engine, family=family, split=split, people=s["people"], sends=s["n"],
                        precision=round(p, 4), precision_ci=[lo, hi], coverage=round(cov, 4)))
    (RUN / "by_generator.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
