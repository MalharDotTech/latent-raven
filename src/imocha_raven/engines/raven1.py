"""Raven 1 (E0): the naive LLM baseline. One Haiku call over the raw bundle text, no rules, no verification."""

from .. import llm
from ..types import Bundle, Citation, Claim, Decision, EngineResult
from .common import apply_policy, scale_max, skill_index, src_of

MAX_CHARS = 60000
PROMPT = """You infer which workplace skills an employee has and at what level, from their documents.

Skills (skill_id: name [levels 1..max]):
{skills}

Level scale (K4, 1..4): 1 explains concepts, 2 delivers with guidance, 3 delivers independently, 4 guides others.
K3 skills (sales, customer success; max 3): 1 delivers with guidance, 2 delivers independently, 3 guides others.

Documents:
{docs}

Return a JSON object: {{"skills": [{{"skill_id": "...", "level": <int>, "confidence": <0-1>, "source_id": "...",
"quote": "<exact quote from the documents>"}}], "unmatched": ["real skills not in the list"]}}.
List every skill from the list the person has. Reply with JSON only."""


class Raven1:
    name = "raven1"

    def infer(self, bundle: Bundle, taxonomy: dict, claims: list[Claim]) -> EngineResult:
        idx = skill_index(taxonomy)
        skills = "\n".join(f"{k}: {v['name']} [max {scale_max(taxonomy, k)}]" for k, v in idx.items())
        docs = "\n\n".join(f"### {s.source_id} ({s.source_type})\n{s.text[:MAX_CHARS]}" for s in bundle.sources)
        obj, r = llm.call_json(PROMPT.format(skills=skills, docs=docs), model="haiku", purpose=f"raven1:{bundle.person_ref}")
        src, ds = src_of(bundle), {}
        for x in obj.get("skills", []):
            sid = x.get("skill_id")
            if sid not in idx or sid in ds or not isinstance(x.get("level"), int):
                continue
            q, s = str(x.get("quote") or ""), src.get(x.get("source_id"))
            ev = [Citation(source_id=s.source_id, quote=q)] if s and q else []
            ds[sid] = Decision(person_ref=bundle.person_ref, skill_id=sid, action="send",
                               level=max(1, min(x["level"], scale_max(taxonomy, sid))),
                               p_yes=float(x.get("confidence") or 0.0), evidence=ev, reason="LLM read of the raw bundle.")
        return EngineResult(engine=self.name, person_ref=bundle.person_ref,
                            decisions=apply_policy(sorted(ds.values(), key=lambda d: d.skill_id), bundle, taxonomy),
                            unmatched_skills=[str(u) for u in obj.get("unmatched", [])], cost_usd=r.cost_usd,
                            input_tokens=r.input_tokens, output_tokens=r.output_tokens, latency_s=r.latency_s)
