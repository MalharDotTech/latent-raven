# Productionizing Raven: playbook

How to run Raven 2 (rulebook) and Raven 3 (weighted, calibrated) on real employee data across diverse skill families: what to tune, how often, where humans decide, and how Latent feedback flows back into the parameters.

## Index

| ID | Section |
|---|---|
| PB.1 | [Outcomes: what Raven decides](#pb1-outcomes) |
| PB.2 | [Parameter inventory](#pb2-parameter-inventory) |
| PB.3 | [Tuning cadence: real time, daily, weekly, quarterly](#pb3-tuning-cadence) |
| PB.4 | [Feedback loop from Latent and Teams answers](#pb4-feedback-loop) |
| PB.5 | [Human in the loop](#pb5-human-in-the-loop) |
| PB.6 | [Guardrails and kill switches](#pb6-guardrails) |
| PB.7 | [Diverse skill families and cold start](#pb7-diverse-skill-families) |
| PB.8 | [Rollout stages](#pb8-rollout) |
| PB.9 | [Data, privacy and fairness operations](#pb9-data-privacy-fairness) |
| PB.10 | [Metrics dashboard](#pb10-metrics) |
| PB.11 | [Implemented: the minimum feedback loop (RLHF-borrowed)](#pb11-implemented-loop) |

---

<a id="pb1-outcomes"></a>
## PB.1 Outcomes: what Raven decides

**Send does not mean "high skill".** It means "we are confident the person has this skill **and** we can name their level within ±1". A level-1 skill with solid evidence is a send. A level-4 claim from a CV alone is a hold.

| Outcome | Meaning | Who acts next |
|---|---|---|
| `send` | Skill present, level backed by evidence, p(Yes) ≥ threshold | Employee confirms on Teams |
| `hold:needs_evidence` | Plausible skill, but evidence too thin or too old, or no record shows a level | Employee ("bring proof": link GitHub, portfolio, take an assessment); product (connect the missing source) |
| `hold:conflict` | Evidence disagrees: ceiling - floor ≥ 3, test contradicts work, sources conflict | Human reviewer queue |
| `not_extract` | Mentioned but not a skill to record: excluded generic, wrong mapping, decoy | Nobody; logged for taxonomy QA |
| `do_not_message` | Consent or region blocks messaging | Nobody; can still be stored if policy allows |
| `unmatched` | Real skill outside the customer taxonomy | Taxonomy owner queue |

"Abstain" in Latent is the panel-level view: the judges disagree by 3+ levels or fewer than 2 can score. In production, that is `hold:conflict`. Thin evidence is `hold:needs_evidence`. Keep these two holds separate: one is a coverage problem, the other a correctness problem, and they need different owners.

---

<a id="pb2-parameter-inventory"></a>
## PB.2 Parameter inventory

### Raven 3 (learned and calibrated: tune with data)

| Parameter | Today | What it controls | Learned from |
|---|---|---|---|
| `tau` (threshold) | 0.364, one global value | Send vs hold. Trades precision for coverage | Rolling labelled answers, per segment |
| `shift` | +1 on applied work | Corrects the extractor's habit of reading applied work one level low | "level too low / too high" answers per evidence type |
| `Q[type]` | test 0.85, applied 0.8, authored 0.7, cert 0.6, course 0.15, listed 0.12 | How much one record of each type raises P(has skill) | Logistic fit of Yes/No on evidence features |
| `GROUP_CAP` | self 0.3, training 0.15 | Ceiling on self-stated and course evidence | Same fit, constrained |
| `SAME_CLUSTER` | 0.3 | Discount for correlated evidence (same repo, project or CV lineage) | Pairs with known overlap; keep conservative |
| `HALF_LIFE_Y` | 2.5 years | Evidence decay | Yes rate vs evidence age, per skill type (tools decay faster than practices) |
| `LEVEL_NOISE` | [0.6, 0.25, 0.1, 0.05] | How far a record's level can sit from the true level | Confusion matrix: level seen vs confirmed level |
| No-level-evidence rule | Hold | Stops middle-level guessing | Fixed policy; never tuned away |

### Raven 2 (rulebook: change only through review)

| Parameter | Today | Why it is not auto-tuned |
|---|---|---|
| Decay window per skill (`decay_hint_years`) | 2 or 5 years | Customers sign off on it; it is auditable |
| Source caps per group | org/self capped at "applies alone"; training at "knows" | Encodes policy about trust |
| Floor rule | 2+ groups, a measured result under 2 years, or work in 3+ months | Core of the contract |
| Spread hold | ceiling - floor ≥ 3 | Disagreement policy |
| Establishing groups | measured, work, authored, org, third_party | Trust policy |

Raven 2 is the explainable fallback and the guardrail. If Raven 3 sends where Raven 2 sees a conflict, route to review rather than send.

### Shared, outside the engines

| Parameter | Controls |
|---|---|
| Extractor model and prompt version | Claim quality. Any change re-runs the frozen eval before release |
| Quote verification tolerance | Hallucination filter. Never loosen without an audit |
| Taxonomy aliases, ambiguity and exclude list | Mapping errors (Go the language vs "go", SAP HCM vs FI) |
| Send policy: max 3 skills, 3 quotes, cadence | Message fatigue and answer quality |
| Segment definitions | Which slices get their own threshold |

---

<a id="pb3-tuning-cadence"></a>
## PB.3 Tuning cadence

Rule: **single answers never move parameters in real time.** Real-time learning from individual answers invites feedback loops, gaming ("say Yes to everything") and drift nobody can explain to a customer.

| Cadence | What changes | How | Approval |
|---|---|---|---|
| Real time | Nothing in the model. Only policy switches: pause a skill, a segment or the whole sender | Circuit breaker on the rolling Yes rate (PB.6) | Automatic, then a human confirms |
| Daily | Monitoring only: Yes rate per segment, holds, conflicts, extraction failures, drift in evidence mix | Batch job plus dashboard | None needed |
| Weekly | `tau` per segment; `shift` | Risk-controlled recalibration on a rolling 4-8 week window of labelled answers (PB.4) with max step size and minimum n | Auto-proposed; a reviewer approves the diff |
| Every 2-4 weeks | `Q`, `GROUP_CAP`, `LEVEL_NOISE`, `HALF_LIFE_Y` | Refit with current values as priors (Bayesian or L2 toward current); champion/challenger in shadow for 1 week | ML owner + product sign-off |
| Quarterly | Raven 2 rules, taxonomy level lines, decay windows, segment map | Human review with customer HR; re-run frozen eval and fairness twins | Customer + iMocha |
| On any extractor or model change | Everything downstream | Re-extract a frozen benchmark, compare claim diffs, re-calibrate `tau` | Release gate |

---

<a id="pb4-feedback-loop"></a>
## PB.4 Feedback loop from Latent and Teams answers

### Signals collected per sent skill

| Signal | Source | What it measures | Known bias |
|---|---|---|---|
| Self-rating (locked before reveal) | Latent | The person's own level, unanchored | Over- and under-claimers |
| "Do you have this skill?" Yes/No | Latent, Teams | Has-skill precision | Social desirability (people accept flattering skills) |
| "Level too low / right / too high" | Latent, Teams | Level calibration and direction of error | Direction is informative, magnitude is not |
| "Anything we missed?" | Latent | Coverage gaps and unmatched skills | Free text, needs triage |
| Manager or peer confirmation (sampled) | Audit | Independent truth | Costly, so sampled |
| Assessment result | iMocha tests | Measured anchor for level | Shows knowing more than applying (level ≤ 1 alone) |

### How the signals become parameter updates

1. **Labels.** A send gets label `yes` if has-skill = Yes and level = "right", or within the ±1 rule after the person's correction. Weight self-report labels below audit labels (e.g. 0.5 vs 1.0) and shrink self-report labels from known over-claimers.
2. **Threshold per segment (weekly).** For each segment (skill family × evidence-source mix), take labelled sends from the rolling window. Choose the smallest `tau` whose upper confidence bound on the error rate is ≤ 5% (risk control / Learn-then-Test style), not the point estimate. Require n ≥ 100 labels per segment; below that, inherit the parent segment's `tau`. Limit each step to ±0.05.
3. **Level shift (weekly).** Count "too low" vs "too high" per evidence type. If "too low" persistently exceeds "too high" with a confidence interval excluding zero, raise the shift for that type by 0.5 (fractional shifts become a level prior), and the reverse for "too high".
4. **Evidence weights (bi-weekly).** Fit P(Yes) ~ weighted evidence features with current `Q` as the prior. Constraints: monotone (more evidence never lowers P), test ≤ 1 level, self-stated capped.
5. **Exploration for holds.** Answers only exist for sends, so holds never get labelled and a strict engine looks perfect while missing everything. Each week, ask a small random sample of holds (1-3% of `hold:needs_evidence`, never `hold:conflict`) as low-key "Do you use X at work?" questions, and run manager audits on a stratified sample of holds. This measures the false-hold rate and coverage honestly.
6. **Never optimise the Yes rate alone.** Pair it with coverage and the audit precision, or the system learns to send only the safest skills.

### Biases to correct before learning

- **Selection bias:** only sends get answers; fix with exploration (step 5).
- **Answer bias:** people say Yes to flattering levels; use pre-reveal self-ratings and audits as anchors.
- **Non-response bias:** people who reply differ from people who don't; track response rate per segment and weight it.
- **Population shift:** Latent players are friends and volunteers; production employees are not. Use Latent to debug and calibrate only coarsely, not as the population estimate.

---

<a id="pb5-human-in-the-loop"></a>
## PB.5 Human in the loop

| Where | Who | What they decide | Volume control |
|---|---|---|---|
| Level lines and bands per customer | Customer HR / L&D + iMocha | What each level means and the mapping from score to band (High / Medium / Low / Disputed). Bands are a customer risk choice, not a model output | Once per taxonomy version |
| Conflict queue (`hold:conflict`) | Skill SME or manager | Resolve the level, or confirm hold | Prioritise by business value; SLA |
| Weekly audit sample | Trained reviewers, blind to engine output | Independent precision on sends and the false-hold rate on holds | ~100-200 items/week, stratified by family |
| Parameter change review | ML owner + product | Approve or reject auto-proposed `tau`/`shift`/weight diffs, with before/after on the frozen eval and shadow traffic | Weekly |
| Unmatched skills | Taxonomy owner | Add a skill, add an alias, or exclude | Weekly batch |
| Disputes | Employee → manager | "No" on a sent skill with an appeal note | Feeds the audit set |
| Fairness review | Responsible-AI reviewer | Slice metrics and twin flips before every release | Release gate |

Band mapping recipe: start with the calibrated p(Yes) and the level posterior from Raven 3. Map `p ≥ tau` with level evidence to **High** (send), `tau_low ≤ p < tau` to **Medium** (hold:needs_evidence, ask for proof), `p < tau_low` to **Low** (no action), and Raven 2/3 disagreement or spread ≥ 3 to **Disputed** (human). Humans pick `tau_low` and approve `tau`; the system proposes both from data.

---

<a id="pb6-guardrails"></a>
## PB.6 Guardrails and kill switches

- **Circuit breaker:** if the rolling 7-day Yes rate's lower confidence bound for a segment drops below 92%, pause sends for that segment automatically and page the owner.
- **Step limits:** `tau` ±0.05 per week, `shift` ±0.5, weights ±20% relative per refit.
- **Minimum sample:** no segment-specific parameter below n = 100 labels; inherit from the parent.
- **Frozen benchmark:** synthetic + audited real set, never used for fitting; every change must not regress precision by more than 1 point or twin flips at all.
- **Champion/challenger:** a new parameter set runs in shadow (decides, does not send) for a week before promotion.
- **Raven 2 veto:** Raven 3 cannot send when Raven 2 says the evidence conflicts (spread ≥ 3 or test contradiction); route to review.
- **No level evidence, no level:** permanent rule.
- **Message budget:** max 3 skills per person per message, max one message per person per month.

---

<a id="pb7-diverse-skill-families"></a>
## PB.7 Diverse skill families and cold start

Engineers leave rich traces (GitHub, Jira); sales, design, support, HR and finance mostly do not. Without a plan, Raven quietly becomes an engineer-only product.

| Family | Evidence that exists | Connector to add | Typical outcome without it |
|---|---|---|---|
| Engineering | GitHub, Jira, CI, design docs | Already common | Good coverage |
| Data / ML | Repos, notebooks, dbt runs, Airflow history | dbt / Airflow metadata | Medium |
| Design | Figma activity, portfolio, research reports | Figma, Confluence, portfolio | CV-only, so mostly holds |
| Sales / CS | CRM opportunities, account notes | Salesforce / HubSpot | Holds; credit-split traps |
| Support | ServiceNow / Zendesk tickets | ITSM | Volume ≠ depth traps |
| HR / Finance | ATS, HRIS, SAP, models | ATS, HRIS | Invisible skills, mostly holds |
| Off-taxonomy (civil, mechanical, facilities) | CVs, certifications | None: taxonomy decision | Zero sends plus unmatched list (correct) |

Cold start for a new family or customer:
1. Start with Raven 2 rules only, plus `tau` inherited from the closest family.
2. Run in shadow for 2-4 weeks; collect audit labels (n ≥ 100 per family).
3. Fit a family-specific `tau` and `shift`; promote Raven 3 for that family when its audit precision lower bound beats Raven 2's.
4. Report coverage per family on the customer dashboard, with "connect source X to unlock Y% more coverage".

---

<a id="pb8-rollout"></a>
## PB.8 Rollout stages

| Stage | Scope | Exit gate |
|---|---|---|
| 0 Offline | Frozen synthetic benchmark + audited real sample | Precision lower bound ≥ target on the test half; zero twin flips in Raven 2/3 decisions; determinism |
| 1 Shadow | Real customer data, decisions logged, nothing sent | Audit precision on 200+ shadow sends; extraction error rate; conflict queue manageable |
| 2 Pilot | One department, opt-in, ≤ 3 skills per person | Live Yes rate lower bound ≥ 95% on 400+ answers (about 388/400 needed to prove 95%) |
| 3 Canary | 5-10% of employees per family | No circuit-breaker trips for 2 weeks; fairness slices within tolerance |
| 4 General | All consenting employees | Weekly review cadence running; kill switch tested |

---

<a id="pb9-data-privacy-fairness"></a>
## PB.9 Data, privacy and fairness operations

- **Identity:** a stable key (employee ID, linked account, HR rehire or name-change record) wins; never merge on name; no stable key means no merge. Name and email changes keep history (they disproportionately affect women after marriage).
- **Consent and region:** honour per-region consent (EU, India DPDP Act). `do_not_message` is enforced in the engine, not the UI.
- **Protected attributes:** strip DOB, gender, marital status and photos before extraction; redact names before the LLM reads, which also removes the twin-flip source seen in Raven 3.
- **Prompt injection:** the reader has no tools, quotes must exist in the source, and code decides levels. Keep all three.
- **Retention:** raw documents short-lived; keep only claims with quotes and source pointers; delete on employee request.
- **Fairness:** fairness twins run in CI on every change; slice Yes rate, coverage and hold rate by gender (where lawfully known), location, role family, tenure and age band; investigate gaps over 3 points.

---

<a id="pb10-metrics"></a>
## PB.10 Metrics dashboard

| Metric | Target | Why |
|---|---|---|
| Live Yes rate (with Wilson CI) | ≥ 95%, lower bound | The business promise |
| Audit precision on sends | ≥ 95% | Independent of self-report bias |
| Coverage (correct sends / skills truly held, from audits) | Rising per family | Usefulness |
| False-hold rate (from hold exploration and audits) | Falling | Holds that should have been sends |
| Conflict queue size and age | SLA met | Human load |
| Level calibration: % "too low" vs "too high" | Balanced | Shift health |
| Response rate | Stable per segment | Non-response bias |
| Twin flips | 0 for Raven 2/3 | Fairness |
| Cost and latency per person | Budget | Unit economics |
| Unmatched skills per family | Triaged weekly | Taxonomy health |

---

<a id="pb11-implemented-loop"></a>
## PB.11 Implemented: the minimum feedback loop (RLHF-borrowed)

**Borrowed from RLHF, not RLHF.** In RLHF, human preference labels train a reward model, and the policy's weights are updated by gradient steps against it. Raven borrows only the idea that human judgement is the reward signal. The "policy" is a calibrated rule (send if p(Yes) ≥ tau and some record shows a level), and the signal may move only two scalars, inside guardrails. There is no reward model and no gradient update, and evidence weights are never learned from self-reports.

| Parameter | Owner | Mechanism (code) | Guardrails |
|---|---|---|---|
| `tau` | Loop (auto) | `feedback.propose_tau`: lowest tau whose one-sided 95% lower bound on precision is ≥ 95% on labelled Raven 3 candidates; if none qualify, tighten | ≥ 30 labels; ±0.05 per run; range 0.05-0.95 |
| `shift` | Loop (auto) | `feedback.propose_shift`: reacts only to level misses outside the ±1 band, when they lean one way | ≥ 20 level answers; ≥ 5 misses; lean ≥ 0.6; ±1 per run; range 0-2 |
| `Q`, `GROUP_CAP`, `SAME_CLUSTER`, `HALF_LIFE_Y`, `LEVEL_NOISE` | Human | Audit labels + shadow run (PB.3) | Listed in `feedback.HUMAN_ONLY`; the loop cannot write them |
| No-level-evidence rule, Raven 2 rules, taxonomy, bands | Human | Quarterly review | Never automated |

Data flow:

1. A player answers in Latent ("Do you have this skill?", "Panel's level is too low / right / too high") → `pilot.db`.
2. `feedback.load_live` joins each answer with the Raven 3 trace stored for that round (p(Yes), best level, level evidence). Implied level = rounded panel average adjusted by the answer, or the pre-reveal self-rating when the panel abstained.
3. Latent shows every skill that any Raven sends, so players also answer on skills Raven 3 held. That is built-in hold exploration: labels on both sides of the threshold.
4. `feedback.run` proposes new `tau`/`shift` and writes `engines/raven3_feedback.json` (an overlay plus history) only with `--apply`. Raven 3 reads the overlay at the next round. `RAVEN3_FEEDBACK=0` disables it, and deleting the file rolls back to the offline baseline `raven3_tau.json`.
5. `eval.run` always passes tau and shift explicitly, so offline scores never depend on live feedback.

```bash
uv run python -m imocha_raven.feedback --source live            # dry run: what would change and why
uv run python -m imocha_raven.feedback --source live --apply    # write the overlay
uv run python -m imocha_raven.eval.simulate_feedback --labels said     # answers as people give them (flattery included)
uv run python -m imocha_raven.eval.simulate_feedback --labels ability  # answers as an expert audit would
```

What the simulation shows (186 synthetic answers, start tau 0.75):
- **tau** walks back toward the calibrated region (lowest qualifying ≈ 0.35-0.39) by 0.05 per round, from either side.
- **shift** depends on whose labels you trust. With "said" labels, only 3 level misses occur, so shift stays at +1. With "ability" labels, 12 misses occur, all too high, and the loop proposes 0. People accept flattering levels, so an engine tuned only on their answers drifts upward. This is why the loop's authority over shift is narrow and why audit labels outrank self-reports (PB.4).
