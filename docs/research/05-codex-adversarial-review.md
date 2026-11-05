# Adversarial review

The plan is directionally sound, but its headline 95% claim is not currently defensible. It optimizes an employee-agreement metric that can look excellent while proficiency accuracy, coverage, and generalization remain poor.

## 1. Seven weakest assumptions and logic holes

1. **The checkpoint does not statistically prove 95%.**  
   **Why it fails:** S1.2 and DEC-11 accept 96% from 400 answers. At 384/400, the approximate 95% Wilson lower bound is only 93.6%. Answers are also clustered by person, department, and skill, so the effective sample is smaller.  
   **Concrete fix:** Gate on a cluster-bootstrap or hierarchical confidence bound whose lower limit exceeds 95%. At minimum, require roughly 98% observed at n=400, or collect substantially more independent answers.

2. **"Yes rate" is not accuracy and is easy to game.**  
   **Why it fails:** S0.1, STEP-6, P5.4, and DEC-4 exclude nonresponders and people who repeatedly agree, while sending only easy High-band cases. Employees may accept flattering levels or avoid challenging HR-backed claims. The resulting metric measures agreement among selected responders, not population precision.  
   **Concrete fix:** Pre-register the denominator, report intent-to-treat precision and coverage, retain all responses with sensitivity analyses, and audit a random sample of nonresponses and excluded responders against independent assessments.

3. **Evidence groups are treated as independent when they share one cause.**  
   **Why it fails:** STEP-3.2 and STEP-4.3 can count a GitHub PR, Jira ticket, project allocation, CV statement, and design document as separate corroboration even though all describe the same project. S3.1 deduplicates source types, not underlying events. This creates false confidence.  
   **Concrete fix:** Add `activity_id/project_id/time_window` lineage and count independent events, not systems. Correlated evidence should contribute diminishing or zero additional weight.

4. **The level algorithm manufactures certainty from an interval.**  
   **Why it fails:** Under STEP-4.3 to STEP-4.5, when floor and ceiling differ by two, choosing the midpoint guarantees that every value in the interval is within ±1. That is arithmetic coverage, not evidence that the midpoint is the person's level. DEC-3 then labels this "right."  
   **Concrete fix:** Produce a calibrated probability distribution over levels. Send only when `P(|predicted - true| <= 1)` clears a validated threshold, and separately report exact-level accuracy. Never turn a wide evidence range into a point estimate solely by choosing its center.

5. **Assessment validation is partially circular and assumes invalid comparability.**  
   **Why it fails:** A current assessment can directly establish High and set the level under STEP-3 and STEP-4, while GT.C evaluates the result against assessments. STEP-1's linear normalization assumes vendor scores and customer levels are interchangeable across skills. This leaks the answer into the predictor and ignores test reliability.  
   **Concrete fix:** Split assessment data into inference and blinded evaluation sets by person and skill. Build skill-specific score mappings using anchor items or empirical calibration, and report test-retest reliability before treating assessments as ground truth.

6. **The learning loop cannot learn unbiased weights from its own sends.**  
   **Why it fails:** STEP-7.1 fits customer-specific logistic regression only from skills admitted by STEP-5.1. Medium and Low cases are mostly unlabelled under DEC-10. This is selective-label bias, with few negatives and no evidence about the decision boundary. One thousand answers can still be inadequate after slicing by source, skill, and level.  
   **Concrete fix:** Randomly sample a small, consented exploration set from Medium and Low bands, preferably through offline review rather than employee messaging. Fit with inverse-propensity weighting and keep a temporally later holdout.

7. **The plan treats integration and governance as configuration problems.**  
   **Why it fails:** S3.6 and P2.5 claim a new source requires no software, while BP stories require source-specific authentication, pagination, permissions, schemas, deletion handling, authorship checks, and data retention. Authored-work ingestion also creates privacy and access-control risks absent from the checkpoints.  
   **Concrete fix:** Define a connector contract with provenance, authorization scope, deletion propagation, retention, tenant isolation, and source-specific conformance tests. Add a privacy/security checkpoint before C2 and narrow the demo to uploaded fixtures or one connector.

## 2. Experiments executable in under 24 hours

| Experiment | Hypothesis | Setup | Metric | Pass/fail threshold |
|---|---|---|---|---|
| **Metric integrity simulation** | S1.2 rarely releases a system whose real precision is below 95%. | Simulate 10,000 populations with clustered employees, flattering overratings, nonresponse correlated with errors, and High-band selection. Apply the exact S0.1/S1.2 exclusions. | False-release probability and gap between reported Yes rate and true precision. | Pass if false-release probability is under 5% and absolute bias under 2 points. |
| **Correlated-evidence stress test** | STEP-3/4 remain calibrated when multiple systems describe the same work. | Generate 500 labelled person-skill profiles. Duplicate each underlying activity across CV, Jira, GitHub, and project records, then vary contradiction and staleness. | Has-skill precision, exact/±1 level accuracy, coverage, and confidence change after duplication. | Pass if duplication changes confidence in under 1% of cases, High precision is at least 97%, ±1 accuracy at least 95%, and coverage at least 40%. |
| **Extraction and mapping challenge set** | STEP-1/2 can reach required precision without collapsing coverage. | Hand-label 200 public or synthetic resume/work snippets containing negation, required-vs-used skills, aliases, "Spark/Go/R" ambiguity, prompt injection, and absent taxonomy entries. Run each twice. | Mapping precision, recall/coverage, fabricated-quote rate, and repeat agreement. | Pass if precision is at least 97% at at least 60% coverage, fabricated quotes are zero, and repeat agreement is at least 99%. |

## 3. Minimal deployed demo in under 20 engineer-hours

### Components and decision boundary

1. **Upload/API ingestion** - Accept synthetic CSV/JSON profiles and text evidence. Pure code.
2. **Evidence extractor** - One batched LLM call per person returning schema-validated quotes, dates, directness, and level signals.
3. **Taxonomy mapper** - Pure-code alias and fuzzy candidate generation; LLM only resolves ambiguous top candidates or abstains.
4. **Inference engine** - Pure code for lineage deduplication, decay, caps, floor/ceiling, contradictions, and send/hold decisions.
5. **Review UI** - Show inference, cited evidence, confidence, abstentions, and correction controls.
6. **Evaluation page** - Pure-code precision, coverage, exact/±1 accuracy, slices, and confusion matrices.
7. **Audit store** - Save source hash, prompt/model version, structured output, rule version, and decision.

Estimated per person with 5 to 10 short evidence items:

- Extraction: 3,000 input + 700 output tokens
- Ambiguous mapping/level classification: 1,500 input + 300 output tokens
- Total: approximately **5,500 tokens per person**, with zero LLM tokens for unambiguous structured records and scoring

### Stack recommendation

- **FastAPI + Pydantic** - Fast schema-first implementation and reliable structured-output validation.
- **SQLite locally, managed Postgres for deployment** - Minimal setup while preserving a clean migration path.
- **Server-rendered Jinja + HTMX** - Enough interactivity without spending the demo budget on a frontend framework.
- **Anthropic API structured JSON** - Claude Code builds the system; a low-cost Claude model handles only semantic extraction and ambiguity.
- **RapidFuzz** - Cheap deterministic taxonomy candidate retrieval.
- **Docker + Railway or Render** - One-command deployment with API and database support.
- **Pytest + seeded synthetic fixtures** - Reproducible adversarial validation rather than a polished but unverifiable demo.

## 4. Three questions for the CTO

1. Is the product promise 95% employee agreement, 95% precision against independent ground truth, or a legally defensible proficiency decision? Which one may be traded away to increase coverage?

2. What minimum coverage makes the system commercially useful? A system can achieve near-perfect precision by sending one obvious skill to 5% of employees.

3. Are we willing to fund randomized exploration and independent assessments, including Medium/Low cases, or are we implicitly accepting that the learning loop can never validate errors outside its existing High-band policy?