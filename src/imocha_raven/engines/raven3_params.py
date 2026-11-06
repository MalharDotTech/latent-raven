"""Raven 3 parameter registry: every knob, what it does, who owns it, where the idea came from, what it feeds.

Single source of truth for docs/engine/raven3-interiors.md and the engine-room "Raven 3 interiors" view.
IDs P1..P13 match the comments in raven3.score_skill / decide. Print the markdown table:
    uv run python -m imocha_raven.engines.raven3_params
"""

from . import raven3
from .common import GROUP_OF

# Where ideas came from. Research docs live in docs/research; plan steps are iMocha's evaluation plan (kept local).
SRC = {
    "06": "docs/research/06-codex-alt-engine.md (Codex: calibrated evidence fusion)",
    "02": "docs/research/02-methods.md (Sonnet: methods survey)",
    "05": "docs/research/05-codex-adversarial-review.md (Codex: adversarial review)",
    "D7": "docs/sprint/01-eval-contract-vs-engine.md D.7 (v0 trim of 06)",
    "plan": "iMocha plan (eval contract), cited by step ID",
    "spec": "data/spec/PERSONA_SPEC.md section 8 (user decisions D-U1..D-U6)",
    "ours": "Our finding in this build (engine-room trace / extractor audit)",
}

# stage: input -> evidence -> possession -> level -> decision -> policy
PARAMS = [
    {"id": "IN1", "name": "quote_verified", "value": "substring match after normalising", "stage": "input", "owner": "contract",
     "does": "Drops any claim whose quote is not found in the source text: no quote, no record.",
     "source": "plan STEP-1 and L2 interface (sprint 01 L2); kept by 06 section 1", "feeds": ["P1"]},
    {"id": "IN2", "name": "evidence_type + level_seen", "value": "applied/test/listed/course/cert/...; level from level lines",
     "stage": "input", "owner": "contract",
     "does": "What kind of record it is and which customer level line it shows; a test alone shows at most level 1.",
     "source": "plan STEP-3 'did > listed', STEP-4.1-4.2; spec D-U2 (applied work first)", "feeds": ["P1", "P6"]},
    {"id": "IN3", "name": "group (source -> trust group)", "value": str(GROUP_OF), "stage": "input", "owner": "human",
     "does": "Maps each source system to a trust group (measured, work, authored, org, third_party, self, training).",
     "source": "plan S3 source table and STEP-4.7 conflict order", "feeds": ["P2", "P4"]},
    {"id": "P1", "name": "Q (evidence weight by type)", "value": str(raven3.Q), "stage": "evidence", "owner": "human",
     "does": "How much one record of this type raises the chance the person has the skill.",
     "source": "06 section 2 q_i = P(H=1|e_i) (should be isotonic-calibrated; v0 hand-set); ordering from plan STEP-3.1-3.4",
     "feeds": ["P4"]},
    {"id": "P2", "name": "GROUP_CAP", "value": str(raven3.GROUP_CAP), "stage": "evidence", "owner": "human",
     "does": "Ceiling on self-stated and training evidence, however many times it is repeated.",
     "source": "plan S3 source caps, adapted from a level cap to a probability cap", "feeds": ["P4"]},
    {"id": "P3", "name": "HALF_LIFE_Y (decay)", "value": f"{raven3.HALF_LIFE_Y} years", "stage": "evidence", "owner": "human",
     "does": "Evidence loses half its weight every 2.5 years, continuously, instead of falling off a cliff.",
     "source": "06 section 3 continuous recency curve; D7 'one exponential half-life'; value sits between plan STEP-3.5 windows (2y tools, 5y domain)",
     "feeds": ["P4"]},
    {"id": "P4", "name": "dependence discount (SAME_CLUSTER)", "value": f"duplicate 0, same cluster {raven3.SAME_CLUSTER}, new cluster 1",
     "stage": "evidence", "owner": "human",
     "does": "The strongest record in a cluster counts fully, repeats of the same work count 0.3, duplicates count 0.",
     "source": "06 section 2 max-in-cluster and d_c; D7 fixed values; 02 point 8 ('independent groups count once' is stated, not enforced); plan S3.1, STEP-3.3",
     "feeds": ["P5", "P6"]},
    {"id": "P5", "name": "noisy-OR -> P(has)", "value": "1 - prod(1 - weight)", "stage": "possession", "owner": "formula",
     "does": "Combines the weighted records into one probability that the person has the skill.",
     "source": "06 section 2 dependence-adjusted noisy-OR; 02 methods table (replaces plan STEP-3's ad-hoc strongest-plus-extras)",
     "feeds": ["P11"]},
    {"id": "P6", "name": "LEVEL_NOISE", "value": str(raven3.LEVEL_NOISE), "stage": "level", "owner": "human",
     "does": "How likely the true level is 0, 1, 2 or 3 steps away from the level a record shows.",
     "source": "06 section 2 r_{i,l} = P(L=l|e_i) (should be learned from assessments; v0 hand-set); 05 fix 'calibrated distribution over levels'",
     "feeds": ["P8"]},
    {"id": "P7", "name": "shift", "value": "baseline from eval; live overlay from feedback loop", "stage": "level", "owner": "auto",
     "does": "Adds +1 to levels read from applied work, correcting the reader's habit of under-levelling it.",
     "source": "ours: extractor audit (applied work read one level low); fitted on the calibration half; auto-tuned by feedback.py",
     "feeds": ["P8"]},
    {"id": "P8", "name": "level posterior", "value": "flat prior x prod(LEVEL_NOISE^weight)", "stage": "level", "owner": "formula",
     "does": "Turns all level readings into a probability for each level.",
     "source": "06 section 2 weighted product-of-experts fusion", "feeds": ["P9"]},
    {"id": "P9", "name": "accepted band", "value": "+-1 on K4 scales, exact on K3", "stage": "level", "owner": "contract",
     "does": "The levels at which the person would still answer Yes.",
     "source": "plan S1 Yes definition (has skill and level within +-1; exact on 3-level scales)", "feeds": ["P10"]},
    {"id": "P10", "name": "l* = argmax P(accepted)", "value": "level whose band holds the most probability", "stage": "level",
     "owner": "formula", "does": "Picks the level most likely to be answered Yes, not simply the most likely level.",
     "source": "06 section 2; D7 keep-list", "feeds": ["P11"]},
    {"id": "P11", "name": "p_yes", "value": "P(has) x P(accepted at l*)", "stage": "decision", "owner": "formula",
     "does": "The engine's probability that this message would get a Yes.",
     "source": "06 section 2 final probability; 05 fix 'send only when P(|pred - true| <= 1) clears a threshold'",
     "feeds": ["P13"]},
    {"id": "P12", "name": "no level evidence -> hold", "value": "rule", "stage": "decision", "owner": "contract",
     "does": "If no record shows a level, hold: a middle-level guess passes +-1 75% of the time and is not a reading.",
     "source": "ours: found through the trace visual (37 of 139 sends were guesses); grounded in plan STEP-4.1 and spec D-U2",
     "feeds": ["P13"]},
    {"id": "P13", "name": "tau (send threshold)", "value": "baseline from eval; live overlay from feedback loop", "stage": "decision",
     "owner": "auto", "does": "Send only when p_yes clears this line; trades coverage for precision.",
     "source": "02 selective classification and conformal risk control (Geifman and El-Yaniv; Angelopoulos et al.); 06 section 2; 05 point 1 (gate on a lower bound); fitted on the calibration half; auto-tuned by feedback.py",
     "feeds": ["OUT"]},
    {"id": "POL", "name": "send policy", "value": "max 3 skills, 3 quotes; consent; generic exclude list", "stage": "policy",
     "owner": "contract", "does": "Last gate for every engine: consent, generic skills, message size.",
     "source": "plan STEP-5.3, 5.7, 5.8 (sprint 01 L2.7, L2.9)", "feeds": ["OUT"]},
]

NOT_YET = [
    ("Calibrated q_i (isotonic or temperature scaling)", "06 section 2", "P1 is hand-set; needs labelled answers or audits"),
    ("Contradiction likelihood ratios (failed test, expired cert, explicit No)", "06 section 3; plan STEP-3.6", "not implemented; Raven 2 handles test conflict"),
    ("Learned decay per skill family", "06 section 3", "one half-life for all skills"),
    ("Semantic and time-overlap clustering", "06 section 3", "clusters by source lineage and project key only"),
    ("Level probabilities calibrated on assessments", "05; 06 section 3", "LEVEL_NOISE is hand-set"),
    ("Person-level cluster bootstrap for the precision bound", "02 point on clustering; 05 point 1", "Wilson interval per send"),
]


def markdown() -> str:
    lines = ["| ID | Parameter | Value | Owner | What it does | Source | Feeds |", "|---|---|---|---|---|---|---|"]
    for p in PARAMS:
        lines.append(f"| {p['id']} | {p['name']} | {p['value'].replace('|', '/')} | {p['owner']} | {p['does']} | {p['source']} | "
                     f"{', '.join(p['feeds'])} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(markdown())
