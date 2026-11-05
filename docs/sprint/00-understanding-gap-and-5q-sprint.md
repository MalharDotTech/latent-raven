---
title: WorkRaven - Understanding gap + 5-Question Sprint
date: 2026-11-05
deadline: 2026-11-06 12:00 IST (CTO meeting)
inputs: [../skill-proficiency-inference-engineering-plan.md, ../getting-skills-right-the-plan.md]
research: [../research/01-vendor-landscape.md, ../research/02-methods.md, ../research/03-work-evidence-tools.md, ../research/04-data-sourcing.md, ../research/05-codex-adversarial-review.md]
---

# WorkRaven - Understanding gap + 5-Question Sprint

> **Reframe (later, same day):** the docs are mostly iMocha's internal eval for their own engine. See [01-eval-contract-vs-engine.md](01-eval-contract-vs-engine.md). Where this file says "the logic you must implement" (G.2.2, G.2.6, G.2.9, Q3 route rules), read "iMocha's reference engine, the baseline to beat". The CH table there lists every change.

Your mental model is "a black box that reads everything about a person and outputs skills with a confidence score". The plan describes something narrower and stricter: a pipeline that **decides whether to ask an employee about a skill at all**, and stays silent unless independent evidence proves it. The score is hidden. The product is the abstention.

## Index

| ID | Section |
|---|---|
| G | [Gap analysis: your understanding vs the docs](#g-gap-analysis) |
| Q1 | [What is the actual problem?](#q1-what-is-the-actual-problem) |
| Q2 | [If I do X, what happens?](#q2-if-i-do-x-what-happens) |
| Q3 | [What must never break?](#q3-what-must-never-break) |
| Q4 | [Smallest fillable units](#q4-smallest-fillable-units) |
| Q5 | [What will "production" tell me?](#q5-what-will-production-tell-me) |
| X | [Experiments: "I tried this, this, this"](#x-experiments) |
| T | [Timeline to Fri 12:00](#t-timeline-to-fri-1200) |
| N | [Next steps, third-person view](#n-next-steps-third-person-view) |
| R | [Research synthesis (5 lanes)](#r-research-synthesis) |

---

<a id="g-gap-analysis"></a>
## G · Gap analysis

### G.1 What you got right

- **G.1.1** Multi-source evidence in, per-skill output out. Correct at the shape level.
- **G.1.2** "The real game is the extraction + inference logic." Correct. The plan agrees: STEP-1 to STEP-4 is where all the precision comes from.
- **G.1.3** Data is the bottleneck and determines output quality. Correct, and sharper than you said (see G.2.7).
- **G.1.4** A working demo beats cleverness. Correct for an interview.
- **G.1.5** Token efficiency matters. Correct, and the plan already bakes it in: structured fields skip the model (STEP-1.3).

### G.2 Where depth is missing

| # | Your understanding | What the docs actually say | Why it matters | Ref |
|---|---|---|---|---|
| G.2.1 | Output = skills with a confidence score | Output = **band** (High/Medium/Low/Disputed) + **stated level** on the customer's scale + up to 3 evidence quotes. The 0-100 score is a hidden sort key, never shown | You'd demo the wrong artifact. The CTO wants "send / hold / why", not a number | STEP-3.B, STEP-6.A |
| G.2.2 | An agent infers skill level | **"The model reads; code decides."** LLM only extracts typed facts with an exact quote, picks from closed lists. Bands and levels are deterministic rules | An "agent decides everything" design contradicts their core principle. Use it only as a baseline to beat | STEP-1, STEP-1.1-1.2 |
| G.2.3 | "5 points, three bands, ±1" as one thing | **Two separate outputs**: has-skill band (presence) and proficiency level. ±1 only on scales with 4+ levels; exact level on 3 or fewer | Band ≠ level. "Level 3, High" and "Level 3, Medium" are different facts | STEP-4.8, STEP-2.C |
| G.2.4 | Confidence = how sure we are | 95% = **employee "Yes" rate on skills we chose to send**. Live ≥95%, offline ≥97%, pass bar 96% on 400+ answers, every slice ≥93% | The target is precision on a filtered set, so coverage is a free variable. The engine wins by holding back | S0.1, S1.2, GT.C |
| G.2.5 | Employee "Yes" is the truth | "Yes" is **biased**: people accept flattering levels. Levels are calibrated against **assessments**, never answers. Guard metrics block gaming (flattery, middle-level pileup, easy skills) | The deepest idea in the doc. If you miss it, your eval is gameable and the CTO will notice | S1.3, STEP-7.2, P1.1-P1.3 |
| G.2.6 | More data points = more confidence | **Independent groups count, records don't.** Same group counts once; repeats capped. High needs: a measured result ≤2y, or work records in 3+ months in 24, or work/authored + another group, or verified cert + another group | This is the actual inference logic you said you hadn't understood. It's a rule book, not a model | S3.1, STEP-3.A |
| G.2.7 | Inputs: LinkedIn, GitHub, Confluence, Jira, CV, portfolio, website, certs | Plan's sources are **enterprise systems**: assessments (Tara), Jira/GitHub/ServiceNow/Salesforce, Confluence, HCM, LMS, verified certs, CV. **LinkedIn, portfolio, personal site aren't listed**; at best they're "self-stated", capped at Medium, **never High alone** | Scraping LinkedIn gives you the weakest evidence group. A faithful engine would send almost nothing from it. Your data plan and their logic collide | S3 table, STEP-3 "Never High alone" |
| G.2.8 | "A particular defined skill" is given | Skills must be **mapped to the customer's taxonomy** (alias → closed-list pick → review queue, never forced). Each skill needs **HR-approved per-level description lines**; the same line drives the decision and appears in the message | Taxonomy mapping + level lines are a whole step you skipped. Wrong mapping has its own error budget (0.5 of 5) | STEP-2, S1.1 |
| G.2.9 | Level from how much evidence | Level = **floor/ceiling** rule. Floor = highest level backed by 2+ groups / a measured result / 3+ months of work. Ceiling = highest capped record. Spread 0-1 → floor; 2 → floor+1; 3+ → hold. Each source has a level cap | Specific, implementable, testable. This is STEP-4 in full | STEP-4.3-4.5, 4.A |
| G.2.10 | Not mentioned | **Decay** (tools ~2y, domain ~5y), **contradiction** (failed test, expired cert, "No") lowers band | Two of the seven error-budget rows | STEP-3.5-3.6 |
| G.2.11 | Not mentioned | **Feedback loop**: every answer is a record; weights refit by logistic regression at 1,000 answers/customer; dispute reason codes route fixes to the step that caused them; auto stop rule | The system learns per customer. Demo-able as a simulation | STEP-7 |
| G.2.12 | Not mentioned | **Privacy is a hard rule**: never read email/chat/meetings/calendar; authored work opt-in; EU opt-in | Also kills naive LinkedIn scraping as a design story | S3.4, STEP-5.8 |
| G.2.13 | Build "the engine" | The plan is **checkpoint-gated** (C0-C4). C0 and C1 are offline: readers tested, ≥97% on labelled pairs. Nothing is messaged before | Your demo = a credible C0/C1 on a small set. That is the right scope for 20 hours | GT.C, BP |

### G.3 The one-line reframe

You framed it as "how smartly can I score skills". The docs frame it as **"how rarely can we be wrong when we speak"**. Every design choice serves precision, coverage is whatever is left.

### G.4 Where your three "innovation areas" stand

- **Tech stack.** Lowest leverage. The CTO already chose the architecture ("model reads, code decides"). Picking an exotic stack is status-optimizing. Pick boring, ship, move on.
- **Better logic.** High leverage, but only if you **measure** it. A claim like "my fused score beats the rule book" means nothing without a precision/coverage number on a labelled set.
- **Deployed demo.** Necessary. It's the floor, not the ceiling.
- **Missing fourth area: the eval harness.** This is what proves the other three. It's also what the plan spends the most words on (S1, GT). Build it first.

---

<a id="q1-what-is-the-actual-problem"></a>
## Q1 · What is the actual problem?

Stated: "Build the skill confidence engine."

Break it:

- "skill" → an entry in a customer taxonomy, with per-level description lines. You need a stand-in taxonomy (ESCO / SFIA subset, ~20-30 skills).
- "confidence" → not a displayed number. It's whether the evidence clears the route-to-High rules and pins the level within ±1. Effectively: P(employee says Yes) high enough to speak.
- "engine" → evidence records in, send/hold decisions + level + quotes out. Deterministic given records.
- "build" → for tomorrow, not production. C0/C1-equivalent: readers + rules + offline eval.
- "for whom" → the CTO evaluating **you**: execution speed, judgment, rigor, AI-tool leverage.

**Surviving problem:** Show the CTO a working pipeline that turns real-looking multi-source evidence into send/hold decisions per the plan, with a measured precision and coverage on a labelled set, plus 2-3 experiments showing where the plan's logic holds or breaks.

---

<a id="q2-if-i-do-x-what-happens"></a>
## Q2 · If I do X, what happens? (three chains max)

**Chain A - Scrape iMocha employees' LinkedIn as demo data**
→ evidence is self-stated, one group
→ engine (faithful to plan) caps at Medium, sends nothing
→ demo shows only "held back", no precision number possible (no ground truth)
→ plus ToS + DPDP exposure on identifiable people who didn't consent
→ **reject as primary data.** Usable only as a "this is what LinkedIn alone gets you" contrast on 2-3 consenting people (yourself first).

**Chain B - Synthetic personas with known truth + your own real profile**
→ generate ~20 personas with ground-truth skill + level, then multi-source artifacts (CV, GitHub-like PRs, Jira tickets, certs, course records) with planted traps matching the error budget (S1.1)
→ precision, coverage, and per-trap catch rate become computable
→ risk: "you graded your own homework" → mitigate: generator and inferrer are separate processes, different prompts, labels never shown to inferrer; plus 1-3 real profiles (you, consenting friends) as a sanity check
→ **accept.** This is the only path to a number by tomorrow.

**Chain C - One big LLM call per person ("here's everything, rate skills 1-4 with confidence")**
→ fast to build, looks impressive
→ nondeterministic (fails "same input, same facts" STEP-1.6), invents skills, reads CV length as depth, can't explain itself with quotes
→ contradicts the CTO's own principle
→ **use as the baseline experiment**, not the product. Beating it with the plan's pipeline on precision, determinism, and tokens is the story.

---

<a id="q3-what-must-never-break"></a>
## Q3 · What must never break?

| Category | Item | Produces |
|---|---|---|
| Must hold | No quote, no record: every extracted quote string-matches its source | Unit test, gates every run |
| Must hold | Evidence record schema (STEP-1 1.A fields) never changes shape | Pydantic model + schema test |
| Must hold | Same input → same facts (cache by content hash; temperature 0) | Run-twice test on frozen set |
| Must hold | High band only via the four routes in STEP-3.A | Rule-table unit tests |
| Must hold | Same evidence group counts once | Unit test with duplicate CVs |
| Must not | LLM outputs a band or a level directly | ADR-001 |
| Must not | Read email/chat/meetings; scrape non-consenting people | ADR-002 |
| Must not | Labels from the generator visible to the inferrer | ADR-003 (eval integrity) |
| Assumed true | Stand-in taxonomy (ESCO/SFIA subset) is representative of a customer's | Logged assumption; revisit if CTO shares one |
| Assumed true | Synthetic "employee would say Yes" labels approximate real answers | Logged; biggest honesty caveat in the demo |
| Assumed true | Public GitHub activity ≈ "work records" group | Logged; real customers have private repos + Jira |
| Assumed true | Plan's rule thresholds (3 months, 2 years, ±1) are the v1 rule book to implement as-is | Logged; experiments may challenge them |

---

<a id="q4-smallest-fillable-units"></a>
## Q4 · Smallest fillable units

Write the signature yourself (5 min each), then let Claude fill. Order = dependency order.

| # | Unit | Signature (sketch) | Who |
|---|---|---|---|
| U1 | Evidence record | `class Evidence(BaseModel)`: fields from STEP-1 1.A | You |
| U2 | Quote verifier | `verify_quote(quote: str, source_text: str) -> bool` | Claude |
| U3 | CV reader | `read_cv(text, person_id, source_id) -> list[Evidence]` (LLM, closed lists, then U2 filter) | Claude, you write 3 examples |
| U4 | GitHub reader | `read_github(events, person_id) -> list[Evidence]` (rules only) | Claude |
| U5 | Cert / course / HCM readers | rules only, synthetic JSON in | Claude |
| U6 | Skill mapper | `map_skill(phrase, quote, taxonomy) -> SkillId \| None` (alias, then closed-list LLM pick) | Claude |
| U7 | Has-skill | `band(records: list[Evidence], now) -> Band` (STEP-3 rules + decay + contradiction) | Claude, you write the rule table tests |
| U8 | Level | `level(records, level_lines, scale) -> Level \| Hold` (floor/ceiling) | Claude, you write 4.A tests |
| U9 | Send rules | `select(person, decisions) -> list[Ask]` (max 3, not generic) | Claude |
| U10 | Persona generator | separate script, writes artifacts + `labels.json` the engine never reads | Claude |
| U11 | Eval harness | `evaluate(decisions, labels) -> Report` precision, coverage, per-trap catch, tokens, cost | Claude, you define metrics |
| U12 | Demo UI | per person: evidence → band → level → Teams-style card; eval dashboard | Claude |

Kill switch: if a signature takes more than 5 minutes to write, the unit is too big. Split.

---

<a id="q5-what-will-production-tell-me"></a>
## Q5 · What will "production" tell me?

There is no production before Friday. The demo and the CTO's questions are the production signal. Decide now what you'll log so the signal is readable:

- **Per run:** tokens in/out per reader, cost per person, cache hit rate, wall time.
- **Per decision:** which route fired, which rule held it back, quotes used.
- **Per eval:** precision on sent, coverage, per-trap catch, level exact / ±1 / flattery delta.
- **Build log:** Claude Code + Codex tokens and cost for the whole build (`npx ccusage` for Claude Code; Codex JSONL logs in `.logs/`). This is your "how I used AI" slide.

Routing rule for surprises: a precision miss goes back to Q3 (constraints) or the eval definition, never a patch in a reader.

---

<a id="x-experiments"></a>
## X · Experiments

Three experiments, each a sentence you can say on Friday: "I tried X, measured Y, found Z."

| ID | Hypothesis | Setup | Metric | Pass |
|---|---|---|---|---|
| X1 | The plan's "model reads, code decides" pipeline beats a single-LLM-call baseline on precision and determinism | Same 20 personas through both | Precision on sent, coverage, run-twice agreement, tokens/person | Pipeline ≥95% precision and 100% determinism; baseline lower on either |
| X2 | Abstention is what buys precision | Sweep the band threshold (or the route rules) | Risk-coverage curve | 95% point exists at non-trivial coverage; you can name it |
| X3 | Each error-budget row is caught by its owning step | Planted traps per S1.1 row | Catch rate per trap type | Every trap row caught ≥ its budget |
| X4 (stretch) | A fitted fused score (logistic / noisy-OR over groups) matches the rule book with fewer hand-set thresholds | Same data, compare | Precision at matched coverage | Within 1 point, or better |

---

<a id="t-timeline-to-fri-1200"></a>
## T · Timeline to Fri 12:00

Rough blocks. Sleep is in here on purpose.

| Block | Hours | Output |
|---|---|---|
| Thu evening 1 | 1h | Read research files; lock taxonomy (20-30 skills, 4-level scale) + level lines; write U1 + ADRs |
| Thu evening 2 | 3h | U10 generator (20 personas, traps) + U2-U6 readers |
| Thu night | 2h | U7-U9 rules + unit tests; U11 harness; first X1/X3 numbers |
| Sleep | 6h | - |
| Fri early | 2h | X2 curve; U12 UI; deploy |
| Fri late morning | 1.5h | One real profile (yours) end to end; build cost log; 5-slide narrative |
| Buffer | 0.5h | - |

---

<a id="n-next-steps-third-person-view"></a>
## N · Next steps, third-person view

How the CTO likely sees the candidate tomorrow, and what moves the needle:

- **N.1** "Did he read our plan deeply?" Prove it by implementing STEP-3.A and STEP-4.A exactly, with unit tests named after plan IDs.
- **N.2** "Does he think in evals?" Lead with the eval harness and the risk-coverage curve, not the UI.
- **N.3** "Does he have judgment?" Say why you didn't scrape LinkedIn (weakest evidence group, consent, DPDP). That's a stronger signal than having scraped it.
- **N.4** "Can he push back?" Bring 2-3 critiques with numbers (from research/02 and research/05), e.g. whether 96% on 400 actually proves 95%.
- **N.5** "Can he ship with AI leverage?" Show the build log: agents run in parallel, tokens, cost, what you delegated vs wrote yourself.
- **N.6** Open question to ask early: can they share a real (anonymised) taxonomy file + proficiency scale? It changes STEP-2 from guesswork to real.

---

<a id="r-research-synthesis"></a>
## R · Research synthesis

Five lanes ran in parallel (4 Sonnet agents + 1 Codex). Full files in `docs/research/`. Items marked "unverified" in those files must be checked before quoting.

### R.1 Critiques of the plan, with numbers (bring 2-3 of these)

| ID | Critique | Number / evidence | Fix | Plan ref | Source |
|---|---|---|---|---|---|
| R.1.1 | 96% on 400 does not prove 95% | 384/400: Wilson 95% CI 93.6-97.5%; one-sided lower bound 94.0%. Rule passes a true-95% system ~21% of the time, fails a true-96% system ~43%. Clustering (100 people) widens it | Gate on a lower bound > 95%: ~388/400 (97.0%) or ~771/800 (96.4%); cluster bootstrap by person | S1.2, DEC-11 | 02, 05 |
| R.1.2 | "Independent groups" can share one cause | One project shows up as PR + ticket + allocation + CV line = 4 "groups" | Add `activity_id` / project lineage; count independent events, not systems | S3.1, STEP-3.2 | 05 |
| R.1.3 | Floor + 1 manufactures ±1 by arithmetic | Ceiling − floor = 2 → midpoint is always within ±1 of both ends | Ordinal model giving P(level); send only if P(\|err\| ≤ 1) clears a threshold; report exact-level separately | STEP-4.A | 02, 05 |
| R.1.4 | Learning loop has selection bias | Only High-band items get asked; ~50 negatives per 1,000 answers | Fit on labelled pairs; small consented exploration sample from Medium/Low; inverse-propensity weights | STEP-7.1, DEC-10 | 02, 05 |
| R.1.5 | Self-report is a weak label | Self-rating vs measured ability correlates ~.29-.30 in meta-analyses (unverified citation) | Keep assessments as level truth (plan already does); add decoy-level probes as cheap flattery check | S1.3.1, STEP-7.2 | 02 |
| R.1.6 | Assessment used both as input and as truth | A current measured result sets the level (STEP-4.A) and is the eval set (GT.A) | Split assessment data by person into inference vs blinded eval | GT.A | 05 |
| R.1.7 | "New source is config, not code" is optimistic | Each connector needs auth, pagination, deletion, retention | Connector contract + conformance tests | S3.6 | 05 |

### R.2 Market position

- **R.2.1** Every vendor infers skill presence; almost none publish how they infer level, and none define accuracy as employee agreement. Public numbers are marketing (Beamery "up to 90%", undefined). (01)
- **R.2.2** iMocha's existing inference engine maps a 0-100 confidence score directly to proficiency bands, conflating "how sure" with "how good". WorkRaven separating band and level is the fix. (01; source PDF is marked confidential - cite the idea, not the document)
- **R.2.3** Microsoft People Skills reads email/chat/meetings; WorkRaven's "never" rule is a differentiator at a recall cost. (01)
- **R.2.4** TechWolf is the closest analogue: work-system evidence, traceable levels, validation before use. (01, 03)
- **R.2.5** No public tool does validated per-skill proficiency from code evidence; Flow/LinearB/Swarmia measure team productivity. (03)

### R.3 What to steal for the demo

| Mechanism | Step | Source |
|---|---|---|
| Confidence-threshold slider = live risk-coverage curve | STEP-3/5, X2 | 01, 02 |
| Quote trace on every claim | STEP-1 | 01 (Lightcast) |
| Micro-assessment when floor/ceiling spread is wide, instead of only holding | STEP-4 | 01 (Gloat) |
| Noisy-OR over groups with capped repeats | STEP-3 | 02 |
| GitHub GraphQL recipe: merged PRs, reviews given, commit months → level kinds | STEP-1, STEP-4.B | 03 |

### R.4 Data verdict

- **R.4.1** Do not scrape iMocha staff LinkedIn: breaches LinkedIn User Agreement; hiQ lost on contract grounds; LinkedIn sued Proxycurl (Jan 2025), which shut down Jul 2025; DPDP "made public" exemption is ambiguous for profiling. (04; license/legal texts partly from secondary sources)
- **R.4.2** Plan: ~24 synthetic personas (hidden persona → artifact renderers, inferrer never sees labels, held-out split frozen by hash, traps per S1.1 row) + ~6 consenting volunteers donating CV + public GitHub handle + self-rating. (04)
- **R.4.3** "Message misread" (S1.1 row, 0.8 of the budget) cannot be tested synthetically. Say so. (04)

### R.5 Experiment updates

- **X1-X3** stand.
- **X5 (new, cheap, high signal):** metric-integrity simulation. Simulate populations with flattery and clustered answers; apply S1.2 exactly; measure how often a sub-95% system passes. Pure code, no LLM, ~1h. Directly backs R.1.1. (05)
- **X6 (new):** correlated-evidence stress test. Duplicate one activity across CV/GitHub/Jira/project; check whether band changes. Backs R.1.2. (05)

Brutal line: they don't need someone who can score skills; they need someone who knows when to shut up.
