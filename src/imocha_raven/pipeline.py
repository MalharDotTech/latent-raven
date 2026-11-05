"""Bundle in, PanelResult out: run the three judges on one shared extraction and merge for the app."""

import json

from . import extract
from .engines.common import skill_index
from .engines.raven1 import Raven1
from .engines.raven2 import Raven2
from .engines.raven3 import Raven3
from .llm import CACHE
from .panel import JUDGES, JudgeScore, PanelResult, PanelSkill
from .types import Bundle, Decision, EngineResult

SHOW = 5
EXPECTED_SOURCE = {"software": "github", "data": "github", "platform": "github", "ai": "github", "quality": "github",
                   "engineering_practice": "github", "delivery": "jira", "product_design": "jira", "service": "servicenow",
                   "sales_cs": "salesforce", "people": "hcm", "finance": "hcm"}


def engines(tau: float | None = None) -> list:
    return [Raven1(), Raven2(), Raven3(tau)]


def extraction_usage(pid: str) -> dict:
    """Cost, tokens, latency of the shared extraction for one person, from the cache and the llm log."""
    f = CACHE / "claims" / f"{pid}.json"
    cost = json.loads(f.read_text()).get("cost_usd", 0.0) if f.exists() else 0.0
    tok, lat = 0, 0.0
    log = CACHE / "llm_calls.jsonl"
    for ln in log.read_text().splitlines() if log.exists() else []:
        r = json.loads(ln)
        if r["purpose"].startswith(f"extract:{pid}:"):
            tok += r["input_tokens"] + r["output_tokens"]
            lat += r["latency_s"]
    return {"cost_usd": cost, "tokens": tok, "latency_s": lat}


def _judge(engine: str, d: Decision | None) -> JudgeScore:
    if d is None:
        return JudgeScore(judge=engine, action="hold", reason="No evidence found for this skill.")
    ev = d.evidence[0] if d.evidence else None
    sent = d.action == "send"
    return JudgeScore(judge=engine, action=d.action, level=d.level if sent else None, p_yes=d.p_yes,
                      quote=ev.quote if ev else None, source_id=ev.source_id if ev else None, reason=d.reason,
                      trace=d.trace)


def _missing_source(bundle: Bundle, claims: list, family: str, sid: str) -> str | None:
    have = {s.source_id: s.source_type for s in bundle.sources}
    got = {have.get(c.source_id) for c in claims if c.skill_id == sid}
    return next((s for s in (EXPECTED_SOURCE.get(family, "github"), "assessments") if s not in got), None)


def build_panel(bundle: Bundle, taxonomy: dict, claims: list, results: list[EngineResult], unmatched: list[str]) -> PanelResult:
    idx, fams = skill_index(taxonomy), {f["family_id"]: f for f in taxonomy["skill_families"]}
    by = {r.engine: {d.skill_id: d for d in r.decisions} for r in results}
    sends = {sid for m in by.values() for sid, d in m.items() if d.action == "send"}

    def rank(sid):
        s = [m[sid] for m in by.values() if sid in m and m[sid].action == "send"]
        lv = [d.level for d in s]
        return (-len(s), max(lv) - min(lv), -sum(d.p_yes if d.p_yes is not None else 0.5 for d in s) / len(s), sid)

    def panel_skill(sid):
        sk = idx[sid]
        fam = fams[sk["family_id"]]
        scale = next(x for x in taxonomy["scales"] if x["scale_id"] == fam["scale_id"])
        return PanelSkill(skill_id=sid, name=sk["name"], family=fam["name"], scale_max=len(scale["levels"]),
                          level_lines=sk["level_lines"], judges=[_judge(j, by.get(j, {}).get(sid)) for j in JUDGES])

    shown = sorted(sends, key=rank)[:SHOW]
    rest = [sid for sid in by.get("raven3", {}) if sid not in sends]
    rest.sort(key=lambda s: (-(by["raven3"][s].p_yes or 0), s))
    abstained = []
    for sid in rest[:SHOW]:
        sk, d2 = idx[sid], by.get("raven2", {}).get(sid)
        abstained.append({"skill_id": sid, "name": sk["name"], "reason": (d2 or by["raven3"][sid]).reason,
                          "missing_source": _missing_source(bundle, claims, sk["family_id"], sid)})
    u = extraction_usage(bundle.person_ref)
    r1 = next((r for r in results if r.engine == "raven1"), None)
    return PanelResult(person_ref=bundle.person_ref, skills=[panel_skill(s) for s in shown], abstained=abstained,
                       unmatched_skills=unmatched,
                       cost_usd=u["cost_usd"] + (r1.cost_usd if r1 else 0),
                       tokens=u["tokens"] + (r1.input_tokens + r1.output_tokens if r1 else 0),
                       latency_s=u["latency_s"] + (r1.latency_s if r1 else 0))


def run_engines(bundle: Bundle, taxonomy: dict, tau: float | None = None):
    """Returns (results, claims, unmatched). One extraction shared by all judges."""
    ex = extract.get_extraction(bundle, taxonomy)
    return [e.infer(bundle, taxonomy, ex.claims) for e in engines(tau)], ex.claims, ex.unmatched


def run_panel(bundle: Bundle, taxonomy: dict) -> PanelResult:
    results, claims, unmatched = run_engines(bundle, taxonomy)
    return build_panel(bundle, taxonomy, claims, results, unmatched)
