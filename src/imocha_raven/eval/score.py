"""Scoring against truth-v2. The only module that reads data/truth/."""

import hashlib
import json
import math
from pathlib import Path

from ..engines.common import scale_max
from ..engines.raven3 import accepted
from ..types import EngineResult

TRUTH = Path(__file__).resolve().parents[3] / "data" / "truth"


def load_truth(pid: str) -> dict:
    return json.loads((TRUTH / f"{pid}.json").read_text())


def split_of(pid: str) -> str:
    """Deterministic calibration/test halves."""
    return "cal" if int(hashlib.sha1(pid.encode()).hexdigest(), 16) % 2 == 0 else "test"


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def rows_of(truth: dict) -> dict[str, dict]:
    return {s["skill_id"]: s for s in truth["skills"]}


def is_yes(level: int | None, row: dict | None) -> bool:
    """Simulated answer: has the skill and the stated level is one the person would accept."""
    if not row or not row["has_skill"] or level is None:
        return False
    return level in (row.get("would_accept_levels") or row["oracle"].get("accept_levels") or [])


def sends(result: EngineResult):
    return [d for d in result.decisions if d.action == "send"]


def judge_sends(results: dict[str, EngineResult], truths: dict[str, dict]) -> list[dict]:
    """One row per send: pid, engine, skill, level, p_yes, yes, oracle_send."""
    out = []
    for key, r in results.items():
        rows = rows_of(truths[r.person_ref])
        for d in sends(r):
            row = rows.get(d.skill_id)
            out.append({"pid": r.person_ref, "engine": r.engine, "skill_id": d.skill_id, "level": d.level, "p_yes": d.p_yes,
                        "yes": is_yes(d.level, row), "oracle_send": bool(row and row["oracle"]["action"] == "send")})
    return out


def expected_catch(expected: str, action: str, level: int | None, taxonomy: dict, skill_id: str) -> bool | None:
    """Does the engine's action match expected_engine_behavior? None = not a per-skill behavior (identity traps)."""
    if expected.startswith("send"):
        if action != "send":
            return False
        if expected == "send":
            return True
        n = int(expected.rsplit("_", 1)[1])
        return level in accepted(n, scale_max(taxonomy, skill_id))
    if expected == "hold":
        return action in ("hold", "not_extract")
    if expected == "not_extract":
        return action in ("not_extract", "hold")
    if expected == "do_not_message":
        return action == "do_not_message"
    return None
