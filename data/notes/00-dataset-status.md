# Dataset status - 2026-11-05 evening

## What exists

| Item | Path | State |
|---|---|---|
| Spec + roster (32 personas, 6 batches) | `data/spec/PERSONA_SPEC.md` | v1 |
| Customer taxonomy (55 skills, K4 + K3 scales, 15 excluded) | `data/taxonomy/customer_taxonomy.json` | Codex gpt-6.1-sol |
| Grounding corpus (57 certs, 177 real PR titles, 117 real issues, 30 courses, partial ladders/names) | `data/grounding/` | partial, see its README |
| Fault catalog (F01-F36, prevalence mostly unverified) | `docs/research/07-real-world-nuances.md` | Sonnet |
| 32 persona bundles + hidden truth | `data/bundles/P001..P032`, `data/truth/` | validator clean |
| 18 fairness twins (6 personas x name / name+gender / university) | `data/bundles/P0xx-T1..T3` | validator clean; pronouns in prose not swapped |
| Validator (schema, leakage, grounding, dates, slop) | `scripts/validate_personas.py` | checks schema, NOT cross-source coherence |
| Twin generator | `scripts/make_twins.py` | |
| Codex breadth audit (P001-P027) | `docs/research/08-codex-dataset-audit.md` | |
| Opus depth review (9 sampled) | `docs/research/09-opus-realism-review.md` | |

## Generators

| Batch | PIDs | Model | Realism (both audits) |
|---|---|---|---|
| A | P001-P006 | Claude Sonnet 5.5 | Good prose; structural bugs from its own helper script (PID-coded PR numbers, PRs merged before their ticket exists) |
| B | P007-P011 | Codex gpt-6.1-sol | Fixture-like; evidence narrates its own trap |
| C | P012-P016 | Claude Sonnet 5.5 | Most realistic (Opus); weekday clustering (Codex) |
| D | P017-P021 | Codex gpt-6-astra | All PRs on the 12th; flat yearly totals |
| E | P022-P027 | Claude Sonnet 5.5 | Good; minor CRM stage/ID issues |
| F | P028-P032 | Codex gpt-6.1-terra, repaired by Sonnet | Original was mechanical and thin; repaired, not yet audited |

## Where both audits agree

1. **Prose is believable, structure is generated.** IDs, dates, monthly counts and cross-source links carry generator fingerprints (PID-coded numbers, fixed day-of-month, repeating cycles, chronology breaks such as Ledgerly cited before the 2024 acquisition, `QA-2877` used twice).
2. **Truth mixes two layers.** Hidden ability (what the person can really do) and the observable oracle (what an engine should decide from the bundle). About 40 of 231 labels need "hold" instead of an exact level. Some trap expectations contradict each other or the true level (P001 Airflow, P015 Kubernetes, P008 assessed_level without an assessment file).
3. **Level 1 is misused** for real applied work (P001 Terraform, P015 observability, P024 incident management): labels drift from the taxonomy's level lines.
4. **Coverage gap:** the blocking "invented skill" row (no quote) has no real test. "Message misread" cannot be tested synthetically.
5. **Evidence narrates its traps** in places ("only merged the release bundle", "92% of current text"): too easy for an engine.

## What this dataset can and cannot claim

- **Can:** trap regression tests (does the engine hold, join neither, catch decay, refuse to count bots); engine-vs-engine comparison on the same inputs; determinism and fairness-twin invariance; tokens and cost per person.
- **Cannot:** any population precision claim. Same model family wrote evidence and truth; 32 people and ~250 skills; trap density far above a real workforce. 97% on 150 sends still has a lower bound near 92.9%.

## Decisions the user should own (before the fix pass)

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| U1 | Truth format | Keep one `true_level` vs split into `true_level` (hidden ability) + `oracle` (send@N / hold / not_extract / join_neither / do_not_message) | Split. Score precision on sends against `true_level` + `would_accept_levels`; score holds against `oracle` |
| U2 | What each level means in practice | Taxonomy level lines as written vs your own reading | Re-read the 4 level lines for 5 core skills; adjust once, apply everywhere |
| U3 | Identity rule | Stable employee ID wins vs email + ID must agree | ID wins when present; `join_neither` only when no stable key |
| U4 | Invisible-but-real skills (P010, P019, P025) | Count as engine miss vs correct hold | Correct hold; report as coverage, never precision |
| U5 | Your blind labels | Skip vs label ~50 skills blind against the bundle | Do it. Your disagreement rate with the generators is the most credible number for the CTO |
| U6 | Trap density | Keep adversarial vs add ~10 clean "boring" personas | Add clean personas so precision is not measured on a trap zoo |

### User answers (2026-11-05)

- U1: yes, split.
- U2: level lines literally, applied work first; a test alone shows at most level 1. (Note: the level lines are our Kestrel taxonomy, written by Codex in the style of the plan; iMocha's plan only says "customer level lines".)
- U3: stable ID wins; no stable ID, no merge. Name/email change with persistent ID keeps history (also a skill-history view across role changes).
- U4: correct hold, reported as a coverage gap; product feature: "sources to connect next".
- U5: yes, user labels ~50 skills blind.
- U6: real pilot set R001-R008 in data/real/ (gitignored, no truth); Yes/No from the people after the engine exists. Patterns: docs/research/10-real-cv-observations.md.
- All recorded as spec section 8 (D-U1..D-U6) + truth-v2 schema.

### Fix pass launched 2026-11-05 ~22:30

| Job | Runner | Output |
|---|---|---|
| Batch G P033-P042 (ordinary + real-pattern seeded, truth-v2) | Codex gpt-6.1-sol high | data/bundles/P033-P042, .logs/batch_G.* |
| Structure fix + validator v2 (P001-P032) | Codex gpt-6.1-sol high | scripts/fix_structure.py, data/notes/id_remap.json |
| Truth v2 migration + recalibration (P001-P032) | Claude Opus | data/truth/, data/notes/truth_v2_changes.md (v1 backup data/truth_v1/) |
| Then: twins regen, remap evidence_refs, trap-narration removal, independent blind oracle labels on G (Claude, different family from Codex), user blind sheet | | |

## Proposed fix pass (after U1-U6)

1. Structural regeneration by script, not LLM: globally chronological PR/Jira numbers per repo, bursty dates from a sprint/holiday calendar, monthly totals derived from listed items. Codex.
2. Truth split per U1 and label recalibration against level lines, with the ~40 audit disagreements resolved. Opus proposes, user decides.
3. Remove trap narration from evidence. Sonnet.
4. Add invented-skill test cases (a reader that fabricates must be caught): plant phrases an LLM would likely hallucinate but that are absent from sources.
5. Validator v2: cross-source coherence (PR merged after ticket created, monthly ≥ listed, IDs unique, chronology vs company events).

## Build log (this phase)

| Run | Model | Tokens |
|---|---|---|
| Research lanes 01-04 | Claude Sonnet x4 | ~316k |
| Fault catalog 07 + grounding corpus | Claude Sonnet x2 | ~228k |
| Persona batches A, C, E | Claude Sonnet x3 | ~478k |
| Batch F repair | Claude Sonnet | ~169k |
| Opus depth review 09 | Claude Opus | ~240k |
| Taxonomy | Codex gpt-6.1-sol | 196k in (159k cached) / 10k out |
| Batch B | Codex gpt-6.1-sol | 710k in (656k cached) / 21k out |
| Batch D | Codex gpt-6-astra | 767k in (715k cached) / 24k out |
| Batch F | Codex gpt-6.1-terra | 300k in (258k cached) / 9k out |
| Breadth audit 08 | Codex gpt-6.1-sol | 2.17M in (2.01M cached) / 12k out |
| Review 05 + alt engine 06 | Codex default | 148k in / 7k out |

Main-session Claude Code totals: run `npx ccusage` (not parsed here). One Claude session-limit hit during batch F repair (resumed after reset).

## Self-agreement check (2026-11-06, `uv run python -m imocha_raven.eval.by_generator`)

Engines read with Claude Haiku. If they were rewarded for Claude agreeing with itself, they would score higher on Claude-written personas. They score lower.

| Raven 3 sends, precision | Claude-written A/C/E | Codex-written B/D/G | Adversarial F (Codex + Claude repair) |
|---|---|---|---|
| All 42 personas | 36/39 = 92% (CI 80-97) | 82/83 = 99% (CI 93-100) | 13/17 = 76% (CI 53-90) |

- Same direction for Raven 1 (47% Claude vs 74% Codex) and Raven 2.
- Reading: no sign of self-agreement bias; a strong generator difficulty effect instead. Codex batches are easier (audits: fixture-like, evidence narrates traps; G is ordinary people by design, 41/41).
- Honest headline for the hard slices (A/C/E + F): Raven 3 49/56 = 87.5%.
