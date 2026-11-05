"""Shared contract between pipeline stages, engines and the eval harness.

Layer 2 (interface contract) from docs/sprint/01-eval-contract-vs-engine.md.
Engines see Bundle + Taxonomy only. Truth is loaded by the harness, never by an engine.
"""

from typing import Literal, Protocol

from pydantic import BaseModel

EvidenceType = Literal["applied", "test", "listed", "course", "cert", "self_rating", "authored_doc", "other"]
Action = Literal["send", "hold", "not_extract", "do_not_message"]


class Source(BaseModel):
    source_id: str
    source_type: str  # hcm, cv, github, jira, servicenow, salesforce, certs, lms, assessments, authored_doc
    path: str
    text: str  # raw file text as the engine sees it
    received: str | None = None
    lineage_key: str | None = None  # CV versions of one person share it: count once


class Bundle(BaseModel):
    person_ref: str
    as_of: str
    sources: list[Source]
    messaging_allowed: bool | None = None  # from HCM consent fields when present


class Claim(BaseModel):
    """One thing a reader found in one source. The model reads; code decides later."""
    source_id: str
    skill_phrase: str  # as written in the source
    quote: str  # verbatim span from the source text
    evidence_type: EvidenceType
    level_seen: int | None = None  # level line the record shows, closed list from taxonomy
    date: str | None = None  # YYYY-MM or YYYY-MM-DD of the work, not of the file
    quote_verified: bool = False  # set by code: quote found in source text
    skill_id: str | None = None  # set by mapper; None = unmatched
    group_key: str | None = None  # independence group, set by grouper
    ref: str | None = None  # work item id (PR, ticket) when the quote sits in one; set by code


class Citation(BaseModel):
    source_id: str
    quote: str


class Decision(BaseModel):
    person_ref: str
    skill_id: str
    action: Action
    level: int | None = None
    p_yes: float | None = None  # engine's own confidence that the person answers Yes
    evidence: list[Citation] = []  # at most 3
    reason: str = ""


class EngineResult(BaseModel):
    engine: str
    person_ref: str
    decisions: list[Decision]
    unmatched_skills: list[str] = []
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0


class Engine(Protocol):
    name: str

    def infer(self, bundle: Bundle, taxonomy: dict, claims: list[Claim]) -> EngineResult:
        """claims = shared cached extraction (stages 1-5). E0 may ignore them and read the bundle."""
        ...
