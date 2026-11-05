"""Eval harness: `uv run python -m imocha_raven.eval.run`. Writes runs/<timestamp>/ and runs/latest/."""

import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from .. import extract, load, pipeline
from ..engines.raven1 import Raven1
from ..engines.raven2 import Raven2
from ..engines.raven3 import TAU_FILE, Raven3
from ..panel import EngineScore
from .score import expected_catch, judge_sends, load_truth, split_of, wilson

ROOT = Path(__file__).resolve().parents[3]
TARGET = 0.95
MIN_CAL_SENDS = 10
JUDGES = ["raven1", "raven2", "raven3"]


def prep(path: Path, tax: dict) -> dict:
    """Load, extract (shared, cached) and run the LLM baseline once per person."""
    b = load.load_bundle(path)
    ex = extract.get_extraction(b, tax)
    return {"bundle": b, "claims": ex.claims, "unmatched": ex.unmatched, "r1": Raven1().infer(b, tax, ex.claims)}


def run_one(p: dict, tax: dict, tau: float, shift: int) -> dict:
    b, cl = p["bundle"], p["claims"]
    return {"raven1": p["r1"], "raven2": Raven2().infer(b, tax, cl), "raven3": Raven3(tau, shift).infer(b, tax, cl)}


def curve(rows: list[dict], oracle_sends: int) -> list[dict]:
    """Risk-coverage: sweep the threshold over distinct p_yes values (rows need p_yes)."""
    pts, rs = [], [r for r in rows if r["p_yes"] is not None]
    for t in sorted({r["p_yes"] for r in rs}, reverse=True):
        s = [r for r in rs if r["p_yes"] >= t]
        k = sum(r["yes"] for r in s)
        c = sum(r["yes"] and r["oracle_send"] for r in s)
        pts.append({"tau": t, "sends": len(s), "precision": round(k / len(s), 4), "coverage": round(c / oracle_sends, 4)})
    return pts


def pick_tau(pts: list[dict]) -> float:
    ok = [p for p in pts if p["precision"] >= TARGET and p["sends"] >= MIN_CAL_SENDS]
    return min(p["tau"] for p in ok) if ok else 1.01


def cov_at_target(pts: list[dict]) -> dict:
    ok = [p for p in pts if p["precision"] >= TARGET]
    return max(ok, key=lambda p: (p["coverage"], -p["tau"])) if ok else {}


def twin_flips(res: dict, twins: dict, src_of_twin: dict, judge: str) -> int:
    n = 0
    for tid, r in twins.items():
        a = {d.skill_id: (d.action, d.level) for d in res[src_of_twin[tid]][judge].decisions}
        b = {d.skill_id: (d.action, d.level) for d in r[judge].decisions}
        n += sum(a.get(k) != b.get(k) for k in a.keys() | b.keys())
    return n


def main():
    tax = load.load_taxonomy()
    paths = {p.name: p for p in load.list_bundles("synthetic")}
    twin_paths = {p.name: p for p in load.list_bundles("twins")}
    with ThreadPoolExecutor(8) as ex:
        keys = list(paths) + list(twin_paths)
        preps = dict(zip(keys, ex.map(lambda k: prep((paths | twin_paths)[k], tax), keys)))
    truths = {k: load_truth(k) for k in paths}
    oracle = {k: sum(s["oracle"]["action"] == "send" for s in t["skills"]) for k, t in truths.items()}
    split = {k: split_of(k) for k in paths}

    # raven3 tau and level shift: fitted on the calibration half only
    cal = [k for k in paths if split[k] == "cal"]
    best = None
    for shift in (0, 1):
        raw = {k: Raven3(0.0, shift).infer(preps[k]["bundle"], tax, preps[k]["claims"]) for k in paths}
        cal_pts = curve(judge_sends({k: raw[k] for k in cal}, truths), sum(oracle[k] for k in cal))
        tau = pick_tau(cal_pts)
        pt = next((p for p in cal_pts if p["tau"] == tau), {"coverage": 0})
        if best is None or pt["coverage"] > best[0]:
            best = (pt["coverage"], tau, shift, raw, pt)
    _, tau, shift, raw, cal_pt = best
    TAU_FILE.write_text(json.dumps({"tau": tau, "shift": shift, "target_precision": TARGET, "calibration_personas": len(cal),
                                    "calibration_point": cal_pt}, indent=1))

    res = {k: run_one(preps[k], tax, tau, shift) for k in paths}
    twin_res = {k: run_one(preps[k], tax, tau, shift) for k in twin_paths}
    again = {k: run_one(preps[k], tax, tau, shift) for k in paths}
    det = {j: all(res[k][j].model_dump_json() == again[k][j].model_dump_json() for k in paths) for j in JUDGES}
    src_of_twin = {t: t.split("-T")[0] for t in twin_paths}

    # traps
    traps = []
    for k, t in truths.items():
        for tr in t["traps"]:
            sid = tr.get("skill_id")
            if not sid:
                continue
            for j in JUDGES:
                d = next((d for d in res[k][j].decisions if d.skill_id == sid), None)
                a, lv = (d.action, d.level) if d else ("hold", None)
                c = expected_catch(tr["expected_engine_behavior"], a, lv, tax, sid)
                if c is not None:
                    traps.append({"pid": k, "fault_id": tr["fault_id"], "s11_row": tr["s11_row"], "skill_id": sid,
                                  "expected": tr["expected_engine_behavior"], "engine": j, "action": a, "level": lv,
                                  "caught": c, "split": split[k]})

    def usage(k, j):
        if j == "raven1":
            r = preps[k]["r1"]
            return r.cost_usd, r.input_tokens + r.output_tokens, r.latency_s
        u = pipeline.extraction_usage(k)
        return u["cost_usd"], u["tokens"], u["latency_s"]

    def scoreboard(sel: list[str]) -> list[EngineScore]:
        out = []
        sub = {k: res[k] for k in sel}
        for j in JUDGES:
            rows = [r for r in judge_sends({k: v[j] for k, v in sub.items()}, truths)]
            n, yes = len(rows), sum(r["yes"] for r in rows)
            hit = sum(r["yes"] and r["oracle_send"] for r in rows)
            tr = [t for t in traps if t["engine"] == j and t["pid"] in sel]
            fl = twin_flips({**res}, {t: twin_res[t] for t in twin_paths if src_of_twin[t] in sel}, src_of_twin, j)
            u = [usage(k, j) for k in sel]
            out.append(EngineScore(judge=j, sends=n, precision=round(yes / n, 4) if n else 0.0, precision_ci=wilson(yes, n),
                                   coverage=round(hit / max(1, sum(oracle[k] for k in sel)), 4),
                                   traps_caught=sum(t["caught"] for t in tr), traps_total=len(tr), twin_flips=fl,
                                   cost_usd=round(sum(x[0] for x in u), 4), tokens=sum(x[1] for x in u),
                                   latency_s=round(sum(x[2] for x in u), 1)))
        return out

    test = [k for k in paths if split[k] == "test"]
    curves = {}
    for j in JUDGES:
        if j == "raven2":
            continue
        raw_j = raw if j == "raven3" else {k: res[k][j] for k in paths}
        for name, sel in (("all", list(paths)), ("cal", cal), ("test", test)):
            rows = judge_sends({k: raw_j[k] for k in sel}, truths)
            curves.setdefault(j, {})[name] = curve(rows, sum(oracle[k] for k in sel))
    key_point = {n: cov_at_target(curves["raven3"][n]) for n in ("all", "cal", "test")}

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = ROOT / "runs" / ts
    (out / "per_person").mkdir(parents=True)
    (out / "decisions").mkdir()
    (out / "real").mkdir()
    dump = lambda name, obj: (out / name).write_text(json.dumps(obj, indent=1))
    dump("summary.json", [s.model_dump() for s in scoreboard(test)])
    dump("summary_all.json", [s.model_dump() for s in scoreboard(list(paths))])
    dump("summary_cal.json", [s.model_dump() for s in scoreboard(cal)])
    dump("curve.json", {"curves": curves, "raven3_tau": tau, "raven3_shift": shift, "raven3_at_target": key_point,
                        "raven2_point": next(s.model_dump() for s in scoreboard(list(paths)) if s.judge == "raven2")})
    dump("traps.json", traps)
    dump("meta.json", {"tau": tau, "shift": shift, "split": split, "determinism": det, "oracle_sends": oracle, "target_precision": TARGET,
                       "twin_flips_by_twin": {t: {j: twin_flips(res, {t: twin_res[t]}, src_of_twin, j) for j in JUDGES}
                                              for t in twin_paths}})
    for k in paths:
        p = preps[k]
        pr = pipeline.build_panel(p["bundle"], tax, p["claims"], list(res[k].values()), p["unmatched"])
        (out / "per_person" / f"{k}.json").write_text(pr.model_dump_json(indent=1))
        (out / "decisions" / f"{k}.json").write_text(json.dumps([r.model_dump() for r in res[k].values()], indent=1))

    def real(path: Path):
        b = load.load_bundle(path)
        return b.person_ref, pipeline.run_panel(b, tax)
    with ThreadPoolExecutor(4) as ex:
        for rid, pr in ex.map(real, load.list_bundles("real")):
            (out / "real" / f"{rid}.json").write_text(pr.model_dump_json(indent=1))

    latest = ROOT / "runs" / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink() if latest.is_symlink() else shutil.rmtree(latest)
    shutil.copytree(out, latest)
    print(f"wrote {out} and runs/latest; tau={tau} shift={shift}; determinism={det}")
    for name in ("test", "all"):
        print(f"--- {name}")
        for s in scoreboard(test if name == "test" else list(paths)):
            print(s.model_dump())
    print("raven3 coverage at >=95% precision:", key_point)


if __name__ == "__main__":
    sys.exit(main())
