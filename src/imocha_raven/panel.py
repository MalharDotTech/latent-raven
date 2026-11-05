"""Contract between the engines and the app (Latent mode + dashboard).

The app only imports from this module. Until the real pipeline lands, it calls fake_panel().
Judges: raven1 = LLM baseline (E0), raven2 = iMocha reference engine (E1), raven3 = our engine (E2).
"""

from typing import Literal

from pydantic import BaseModel

JUDGES = {"raven1": "Raven 1", "raven2": "Raven 2", "raven3": "Raven 3"}
JUDGE_BLURB = {
    "raven1": "One big LLM prompt. Fast, confident, sometimes wrong.",
    "raven2": "iMocha's reference rules: floor, ceiling, caps, decay.",
    "raven3": "Our engine: evidence clusters, dependence-aware, calibrated.",
}
Verdict = Literal["latent_winner", "close_call", "reality_check", "panel_abstains"]


class JudgeScore(BaseModel):
    judge: str  # raven1 | raven2 | raven3
    action: Literal["send", "hold", "not_extract", "do_not_message"]
    level: int | None = None  # None when the judge holds
    p_yes: float | None = None
    quote: str | None = None  # strongest verbatim quote from the person's own documents
    source_id: str | None = None
    reason: str = ""
    trace: dict = {}  # raven1: confidence; raven2: groups/floor/ceiling/rule; raven3: p_has, level_dist, tau, evidence weights


class PanelSkill(BaseModel):
    skill_id: str
    name: str
    family: str
    scale_max: int  # 4 (K4) or 3 (K3)
    level_lines: dict[str, str]  # "1".."4" -> customer level sentence, shown for self-rating
    judges: list[JudgeScore]


class PanelResult(BaseModel):
    person_ref: str
    skills: list[PanelSkill]  # 3-5 skills shown in Latent mode (any judge sends)
    abstained: list[dict] = []  # [{skill_id, name, reason, missing_source}] -> "bring proof"
    unmatched_skills: list[str] = []  # real skills outside the taxonomy
    cost_usd: float = 0.0
    tokens: int = 0
    latency_s: float = 0.0


def panel_average(skill: PanelSkill) -> tuple[float | None, int | None]:
    """Average and spread over judges that gave a level."""
    levels = [j.level for j in skill.judges if j.level is not None]
    if not levels:
        return None, None
    return sum(levels) / len(levels), max(levels) - min(levels)


def verdict(self_level: int, skill: PanelSkill) -> Verdict:
    """Latent rule. Needs 2+ judges with a level (a lone judge is not a panel).
    Spread >= 3 mirrors the reference engine's hold rule (ceiling - floor >= 3)."""
    avg, spread = panel_average(skill)
    scored = sum(j.level is not None for j in skill.judges)
    if avg is None or scored < 2 or spread >= 3:
        return "panel_abstains"
    gap = abs(avg - self_level)
    if gap <= 0.5:
        return "latent_winner"
    if gap <= 1:
        return "close_call"
    return "reality_check"


def fake_panel(person_ref: str = "demo") -> PanelResult:
    """Stand-in so the UI can be built before the engines exist."""
    lines = {"1": "Explains Python functions, lists and exceptions in a scored exercise.",
             "2": "Adds a Python script and unit tests with reviewer guidance.",
             "3": "Independently maintains a production Python module and fixes runtime faults.",
             "4": "Reviews Python module designs and teaches test patterns colleagues adopt."}
    py = PanelSkill(skill_id="python", name="Python", family="software", scale_max=4, level_lines=lines, judges=[
        JudgeScore(judge="raven1", action="send", level=4, p_yes=0.9, quote="Built eventPro (Go, Kafka to ClickHouse)",
                   source_id="cv_1", reason="Lots of Python keywords."),
        JudgeScore(judge="raven2", action="send", level=3, p_yes=0.8, quote="28x faster than the Python baseline",
                   source_id="cv_1", reason="Floor 3 from two independent groups."),
        JudgeScore(judge="raven3", action="send", level=3, p_yes=0.86, quote="Built a conversational BI agent (RAG + LLM)",
                   source_id="cv_2", reason="Applied production work, recent."),
    ])
    kafka = py.model_copy(update={"skill_id": "kafka", "name": "Kafka", "family": "data", "judges": [
        JudgeScore(judge="raven1", action="send", level=4, p_yes=0.7, quote="Kafka to ClickHouse", source_id="cv_1"),
        JudgeScore(judge="raven2", action="hold", reason="Only one evidence group."),
        JudgeScore(judge="raven3", action="send", level=2, p_yes=0.6, quote="Kafka to ClickHouse", source_id="cv_1"),
    ]})
    return PanelResult(person_ref=person_ref, skills=[py, kafka],
                       abstained=[{"skill_id": "kubernetes", "name": "Kubernetes", "reason": "Listed only, no work shown.",
                                   "missing_source": "github"}],
                       unmatched_skills=["ClickHouse", "Metabase"], cost_usd=0.03, tokens=41000, latency_s=38.0)


class EngineScore(BaseModel):
    """One row of the dashboard scoreboard, written by eval to runs/latest/summary.json as list[EngineScore]."""
    judge: str
    sends: int
    precision: float  # simulated Yes rate on sends
    precision_ci: tuple[float, float]  # Wilson 95%
    coverage: float  # sends / oracle sends
    traps_caught: int
    traps_total: int
    twin_flips: int  # fairness twins whose output differs from source
    cost_usd: float
    tokens: int
    latency_s: float
