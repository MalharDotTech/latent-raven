# Alternative Engine: Calibrated Evidence Fusion

This engine treats the documents only as an evaluation contract. It does not implement the reference engine’s High routes, source caps, floor and ceiling rules, fixed decay windows, or logistic-regression design.

## 1. Architecture

1. **Privacy and identity gate, deterministic**
   - Join only by employee ID, then unique email.
   - Reject ambiguous identities.
   - Never ingest email, chat, meeting recordings or transcripts, calendars, browsing, or time tracking, per S3.4.
   - Preserve source, date, author, locator, and lineage.

2. **Evidence-event extraction, LLM**
   - One structured-output call per document chunk.
   - Extract atomic claims such as “implemented Python service,” exact supporting quote, date, negation, subject, scope, and demonstrated behavior.
   - The model never decides whether to send.
   - Deterministic code verifies every quote is an exact substring. Invalid events are discarded.

3. **Taxonomy and level entailment, LLM**
   - Candidate skills are retrieved from the customer taxonomy using aliases plus embeddings.
   - A constrained LLM call estimates entailment between each evidence event and:
     - possessing the candidate skill;
     - each customer-provided level description.
   - Ambiguous mappings retain probability mass across candidates instead of being forced.

4. **Evidence fusion, deterministic**
   - Cluster correlated events.
   - Combine calibrated event likelihoods into a joint distribution over `has_skill ∈ {false,true}` and customer levels.
   - Apply recency, contradiction, and dependency adjustments.

5. **Risk-controlled selector, deterministic**
   - Compute the probability that the harness will score the proposed decision Yes.
   - Send only if a calibration-derived threshold is cleared.
   - Rank eligible decisions by expected information value and confidence, excluding generic skills.
   - Send at most three skills per person per message.

6. **Monitoring, deterministic**
   - Run GT.A sets, GT.C checkpoints, STEP-6.B scoring, error-budget attribution, all S1.3 guards, answer rate, and slice stop rules unchanged.

LLM outputs are cached by document hash, prompt version, taxonomy version, and level-description version.

## 2. Has-skill and level decisions

For evidence event \(i\), the calibrated entailment model supplies:

\[
q_i=P(H=1\mid e_i),\qquad
r_{i,l}=P(L=l\mid H=1,e_i)
\]

Calibration uses isotonic regression or temperature scaling fitted out of sample.

Events are partitioned into approximately independent clusters \(c\), such as one project, certificate, assessment, or repeated CV lineage. Within a cluster:

\[
Q_c=\max_i(w_iq_i)
\]

Using the maximum prevents repetition from manufacturing confidence. Across clusters, a dependence-adjusted noisy-OR provides an initial possession probability:

\[
P_0(H=1)=1-\prod_c(1-Q_c)^{d_c}
\]

Here \(d_c\in[0,1]\) is a learned dependency discount. Bayesian likelihood updates then incorporate explicit positive and contradictory evidence:

\[
\operatorname{logit}P(H=1)
=\operatorname{logit}P_0(H=1)
+\sum_j \lambda_j\log LR_j
\]

The level posterior is obtained by weighted product-of-experts fusion:

\[
P(L=l\mid H=1,E)
\propto \pi_l\prod_c
\left(\epsilon+\sum_i a_{ic}r_{i,l}\right)^{d_c}
\]

The selected level is not necessarily the posterior mode. It is the level maximizing the probability of satisfying the evaluation rule:

\[
l^*=\arg\max_l P(\text{accepted level}\mid l,E)
\]

For scales with four or more levels, accepted means true level within \(l\pm1\). For scales of three or fewer levels, it means exact equality.

The final probability is:

\[
P(\text{Yes at }l^*)
=P(H=1\mid E)
\sum_{k\in A(l^*)}P(L=k\mid H=1,E)
\]

The engine abstains unless this probability clears a threshold selected by **conformal risk control** on a held-out, persona-grouped calibration split. The threshold is the lowest value whose upper confidence bound on error is at most 3% offline, preserving the GT.C offline target of 97%. A separately frozen live threshold targets at most 5% error, with the checkpoint requiring at least 96%.

## 3. Difficult evidence

- **Correlation:** Cluster by source lineage, project, repository, time overlap, common upstream text, and semantic similarity. Highly related clusters receive lower \(d_c\). Duplicate evidence therefore improves traceability, not confidence.
- **Decay:** Learn a monotone recency calibration curve by broad skill family. Recency reduces an event’s likelihood ratio continuously. There are no fixed two-year or five-year windows.
- **Contradiction:** Failed assessments, explicit denial, negated work claims, and evidence of supervision update the joint posterior through calibrated negative likelihood ratios. Severe unresolved identity or mapping contradictions force hold.
- **Flattery:** Employee answers calibrate possession only. Level probabilities and thresholds are calibrated against the assessment set. Mean signed level error, exact-level accuracy, and level-distribution divergence are release gates, preventing flattering overstatement or middle-level collapse.

## 4. Swappable harness interface

### Input, one person

```json
{
  "person_id": "E10442",
  "customer_id": "C17",
  "as_of": "2026-11-05",
  "taxonomy": [
    {
      "skill_id": "python",
      "name": "Python",
      "generic": false,
      "levels": [
        {"value": 1, "name": "Aware", "description": "..."},
        {"value": 2, "name": "Working", "description": "..."}
      ]
    }
  ],
  "sources": [
    {
      "source_id": "github-77",
      "source_type": "work_record",
      "lineage_key": "repo-9",
      "observed_at": "2026-09-12",
      "content": "...",
      "locator": "PR 418"
    }
  ]
}
```

### Output, one candidate decision

```json
{
  "person_id": "E10442",
  "action": "send",
  "skill_id": "python",
  "skill": "Python",
  "level": 3,
  "level_name": "Advanced",
  "p_has_skill": 0.997,
  "level_distribution": {"1": 0.001, "2": 0.030, "3": 0.749, "4": 0.220},
  "p_yes": 0.996,
  "threshold": 0.987,
  "reason_if_hold": null,
  "evidence": [
    {
      "quote": "Implemented the Python ingestion service",
      "source_id": "github-77",
      "locator": "PR 418",
      "observed_at": "2026-09-12"
    }
  ],
  "model_version": "cef-1.0",
  "calibration_version": "customer-C17-v3"
}
```

`action` is `send` or `hold`. Holds retain probabilities and use reason codes such as `insufficient_confidence`, `mapping_ambiguity`, `level_uncertain`, `contradiction`, `privacy_block`, or `identity_ambiguous`. A message assembler chooses no more than three `send` decisions and shows no more than three verified quotes per skill.

## 5. Tuning with 20 to 30 synthetic personas

Use persona-grouped leave-one-out evaluation so evidence from one persona never appears in both fitting and evaluation. Freeze the LLM, prompts, embeddings, clustering logic, and priors. Tune only:

- one global entailment temperature;
- dependency discounts for duplicate, same-project, and cross-project evidence;
- one monotone recency curve per broad skill family;
- the abstention threshold.

Generate counterfactual pairs by changing only name, gender, or university and require identical outputs. Include hard negatives for wrong person, ambiguous taxonomy terms, stale evidence, listed-only skills, contradictory assessments, and flattering levels.

With this sample size, optimization should minimize parameters and maximize abstention. It cannot honestly certify 97% by itself. Final threshold certification must use the frozen GT.A sets, especially 200 labelled pairs and 300 assessment decisions.

## 6. Where it would lose to the reference engine

- Sparse customers may provide too little calibration data, making the probabilistic model abstain more often.
- Rare skills with weak level descriptions can produce unstable entailment probabilities.
- Learned decay may extrapolate poorly for a new skill family.
- Noisy-OR assumptions remain approximate even after clustering.
- The reference rule book is easier for HR to audit manually and can encode expert exceptions immediately.
- LLM extraction and entailment cost more and introduce model-version drift.
- Strict conformal thresholds may sacrifice early coverage until enough independent calibration examples exist.

## 7. Token cost

For a person with a CV, HR history, and roughly 20 relevant work items:

- Extraction: 15,000 to 30,000 input tokens, 2,000 to 4,000 output tokens.
- Batched taxonomy and level entailment: 5,000 to 12,000 input tokens, 1,000 to 2,000 output tokens.
- Deterministic fusion and selection: no LLM tokens.

Expected initial cost is approximately **23,000 to 48,000 input tokens and 3,000 to 6,000 output tokens per person**. Caching reduces recurring runs to new evidence only, typically **2,000 to 8,000 input tokens per person per cycle**.