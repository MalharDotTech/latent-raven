# 02 - Methods research for WorkRaven (skill + proficiency inference at 95%)

Lane: academic and applied ML methods. Date: 2026-11-05. Read against: `skill-proficiency-inference-engineering-plan.md` (steps cited as STEP-n.m, S1.2, etc.).
Citation status: [opened] = I read the page or abstract this session; [recalled] = well-known paper cited from memory, not opened, verify before quoting in the meeting.

## 1. TL;DR

- **The 96%/400 pass rule does not prove 95%.** 384/400 gives a Wilson 95% interval of 93.6% to 97.5%. The lower bound is below 95. The plan's "about +/-2 points" is the width, but it is asymmetric and the bound sits under the target. To claim "at least 95% with 95% confidence" you need roughly 388/400 (97.0%) observed, or about 771/800 (96.4%). See section 4.
- **Strongest upgrade: selective classification with a distribution-free risk guarantee** (Geifman and El-Yaniv; conformal risk control). It is exactly "abstain until empirical error on kept items has a provable upper bound <= 5%". Replace hand-set band thresholds in STEP-3/5 with one calibrated confidence score plus a threshold chosen on a held-out set with a Clopper-Pearson or Learn-then-Test bound.
- **Second: replace the hand-set band rules and hand-picked weights with a fitted, calibrated has-skill model** (logistic regression is fine, plus isotonic or Platt calibration and ECE reporting), and an **ordinal model for level** (cumulative-link ordinal regression, or IRT-flavoured) fitted on assessments, not hand-rules over floor and ceiling.
- **Third: keep "no quote, no record" and add entity linking with a cross-encoder rerank to the customer taxonomy.** It is already the right design; the research (SkillSpan, ESCOXLM-R) says span extraction is hard (F1 well below 95 even on clean job postings), so the abstain-on-mapping rule in STEP-2.2 is load-bearing.
- **Flattery is real and the plan's fix (assessments) is the right one but it is expensive.** Self-rated vs measured ability correlates only ~0.29-0.30 in meta-analyses, so "No" answers are a weak label for level. Treat Teams answers as a noisy label for has-skill, never for level.

## 2. Method table

| Method | WorkRaven step | What it fixes in the plan | Demo cost | Citation |
|---|---|---|---|---|
| Grounded LLM extraction + exact-quote check (already planned) | STEP-1 | Hallucinated skills; add normalised-whitespace match and char offsets | S | Plan STEP-1.1 |
| SkillSpan-style span model / JobBERT; ESCOXLM-R encoder | STEP-1, STEP-2 | Cheap deterministic extractor to cross-check LLM reader (STEP-1.6 reproducibility); ESCO-aware embeddings for candidate retrieval | M | [opened] Zhang et al. 2022 arXiv 2204.12811; [opened] Zhang et al. 2023 arXiv 2305.12092 |
| Bi-encoder retrieve + cross-encoder/LLM rerank to taxonomy; context-keyed disambiguation (Spark, Go, R) | STEP-2.1, 2.3 | Wrong-mapping budget (0.5 pts); give each ambiguous alias a context-cue list and require a quote-level cue | M | [recalled] standard entity-linking pattern (BLINK, Wu et al. 2020, arXiv 1911.03814) |
| Noisy-OR over independent groups | STEP-3 | Replaces ad-hoc "strongest sets base, extra groups raise most" with one defensible formula; groups count once by construction | S | [recalled] Pearl 1988 |
| Dawid-Skene / Snorkel label model | STEP-3, STEP-7 | Learns per-source reliability without labels; handles correlated sources badly unless modelled | M-L | [recalled] Dawid and Skene 1979; Ratner et al. arXiv 1605.07723 |
| Dempster-Shafer | STEP-3 | Gives explicit "unknown" mass, matches abstain, but poor tooling and counter-intuitive on conflict | L, skip | [recalled] Shafer 1976 |
| Logistic regression + isotonic/Platt calibration + ECE | STEP-7.1, STEP-3 | Hand weights; make score a probability so a threshold has meaning | S | [recalled] Platt 1999; Guo et al. arXiv 1706.04599 |
| Ordinal regression (cumulative link) / graded-response IRT | STEP-4 | Hand floor/ceiling/+1 table; gives P(level=k) so "within +/-1" is a probability mass | M | [recalled] McCullagh 1980; Samejima 1969 |
| Selective classification, risk-coverage curve | STEP-3 to 5 | Picks the abstention threshold from data, reports coverage at 5% risk | S-M | [opened] Geifman and El-Yaniv, NeurIPS 2017, arXiv 1705.08500 |
| Conformal risk control / conformal sets for ordinal labels | STEP-4, STEP-5 | Guarantee on expected loss; send only when prediction set fits inside a +/-1 window | M | [opened] Angelopoulos et al., ICLR 2024, arXiv 2208.02814; [recalled] Angelopoulos and Bates, gentle intro, arXiv 2107.07511 |
| Binomial lower bound (Clopper-Pearson) for the checkpoint | S1.2, GT.C | The pass rule | S | section 4 |
| Repo expertise mining with recency weighting | STEP-1 (GitHub reader), STEP-3.5 | Concrete features and decay for work-record evidence | M | [opened] Bilkent "Finding expert developers using artifact traceability graphs"; [opened] arXiv 2208.07501; [opened] Avelino et al., IEEE Software 2018 |
| LLM-judge validation with TPR/TNR and Rogan-Gladen correction | GT.B | Plan already says report TPR and TNR; add bias-corrected rate with CI | S | [opened] arXiv 2511.21140 |
| Self-assessment bias literature | S1.3.1, STEP-7.2 | Justifies "answers flatter"; sizes the effect | S (reading) | [opened] Mabe and West 1982 via search; 2024 meta-analysis PMC11433033; [recalled] Kruger and Dunning 1999 |

## 3. Where the plan's logic is weak or hand-wavy

1. **Pass rule (S1.2) confuses width with a bound.** Covered in section 4. Fix: state the claim as a one-sided lower confidence bound, or define the C2 pass as "Clopper-Pearson 95% lower bound >= 95%" and size n accordingly. Also the 400 answers come from 100+ people, so answers are clustered (up to 3-4 per person, same evidence source). Effective n is below 400. Use a cluster bootstrap by person for the interval, or one answer per person for the headline number.
2. **Selection effect on the test sets.** Thresholds (97% offline) are tuned on the labelled pairs that are then used to certify. Split: tune the abstention threshold on one set, certify on a fresh one. With 200 labelled pairs (120 High), the offline 97% bar is itself noisy: 117/120 = 97.5% has a Wilson lower bound of about 92.9%.
3. **Hand-set band rules (3.A) are a classifier with no calibration.** "3+ months within 24 months", "2 groups" are thresholds on features, chosen by judgement, with no evidence they hit 97%. Fix: keep the rules as features (n_groups, months_active, recency, directness, verified), fit a logistic model on labelled pairs, calibrate (isotonic once >1000 points, Platt below), and pick the send threshold from the risk-coverage curve. The rule book becomes the interpretable prior and the explanation text, not the decision.
4. **STEP-7.1 logistic regression: right family, wrong label.** Logistic on evidence facts is the correct, auditable choice (small data, monotone, explainable, calibratable). Problems: (a) labels are employee answers, which are biased toward Yes (acquiescence, flattering levels); (b) the training set only contains items that already passed the High gate, so the model never sees negatives from the abstained region (selection bias, range restriction). Fix: fit on the labelled pairs (employee plus manager, includes low-band items) and use answers as a secondary, re-weighted signal; use sample weights from inverse send probability if you log the propensity. 1,000 answers per customer for a model with ~10 features is fine (about 100 events per variable on the No side is NOT: at 5% No you have ~50 negatives, so regularise heavily, L2, few features).
5. **Level logic (4.A) is not a probability.** Floor/ceiling/"floor + 1" gives no calibrated confidence and the +/-1 trick quietly turns a 2-wide uncertainty into a Yes. Fix: ordinal model that outputs P(level=k | evidence); send level l if P(|true - l| <= 1) >= tau, tau chosen by conformal risk control on the assessment set. For 5+ level scales this is the same tolerance but with a measured error rate. Note a 5-level scale and a centred guess already earns +/-1 coverage of ~60% of the mass by chance, so report exact-level accuracy against a "predict the mode level" baseline (S1.3.2 is right to demand this).
6. **Short scales and the exact-level rule (STEP-2.C).** Exact level on a 3-level scale is far harder than +/-1 on a 5-level scale; the same 95% target means very different engineering. Report precision per scale length and expect lower coverage on short scales, or set a separate target. Equally the "within one level" ground truth makes the Yes definition scale-dependent, so cross-customer Yes rates are not comparable.
7. **Flattery check (S1.3.1) needs assessments that most customers will not have.** The plan has 100 x 3 Tara assessments at iMocha, but at a customer the guard is blind. Cheaper proxies: (a) compare Yes rate for level above vs below modal level; (b) seed "decoy" levels (ask a level 2 above the stated one to a random 3-5% of sends, with consent for the experiment) and measure acceptance - an employee-level acquiescence estimate; (c) per-person acceptance rate (the plan's 10+ all-Yes exclusion is crude; use a hierarchical acquiescence rate).
8. **"Independent groups count once" is stated, not enforced.** CV and LinkedIn, Jira and GitHub for the same project, a cert and a course for the same cert are correlated. Noisy-OR assumes independence, so the count-once rule is a manual de-correlation. Fix: define the unit as the group in S3 (as the plan does), cap each group's contribution, and test conditional independence empirically (pairwise phi between group indicators on labelled pairs).
9. **Decay is a fixed window (2y / 5y).** Replace with exponential or half-life decay per skill type, fitted by checking Yes rate vs evidence age on labelled pairs. Repo-mining work uses recency-weighted edges (section 5D), but the weights there are set intuitively too, so fit it.
10. **No uncertainty on abstention coverage.** The plan reports coverage but sets no floor. A system that abstains on 95% of everything is trivially 99% precise. Track the risk-coverage curve and publish coverage at fixed risk; the customer's value is skills-sent-per-person.

## 4. Statistical check of the 96% / 400 pass rule

Computed in Python (Wilson via closed form; Clopper-Pearson by bisection on the binomial tail).

| Observed (n=400) | Wilson 95% two-sided | Wilson one-sided 95% lower | Clopper-Pearson one-sided 95% lower |
|---|---|---|---|
| 384 (96.0%) | 93.6% to 97.5% | 94.1% | 94.0% |
| 388 (97.0%) | 94.8% to 98.3% | 95.3% | 95.2% |
| 392 (98.0%) | 96.1% to 99.0% | 96.5% | 96.4% |
| 400 (100%) | 99.1% to 100% | 99.3% | 99.3% |

- **Claim check.** "400 answers gives about +/-2 points" is true as a rough half-width (-2.4 / +1.5 at 96%). It does not follow that "96% clears 95% with margin": the lower bound is 93.6% (two-sided) or 94.0% (one-sided exact). 96% observed is statistically compatible with a true rate of 94%.
- **What passes a "true rate >= 95% with 95% confidence" test:** at n=400 you need >=388 Yes (97.0%); at n=800 you need >=771 (96.4%).
- **Power of the current rule.** Probability of observing >=384/400 Yes: true 94% -> 5.1%, true 95% -> 21%, true 96% -> 57%, true 97% -> 90%. So the rule passes a system that is truly 95% about one time in five (false pass) and fails a system that is truly 96% about 43% of the time. It is a weak gate in both directions.
- **Power of the stricter rule (>=388/400):** true 96% -> 19%, true 97% -> 58%, true 98% -> 94%. n=800 with >=771: true 96% -> 33%, 97% -> 87%, 98% -> 99.9%.
- **Zero-failure rule of three:** to claim >=95% with 95% confidence from zero errors needs ln(0.05)/ln(0.95) = 59 clean answers; at 5% errors allowed it needs far more, hence the 400-800 range.
- **Clustering.** 400 answers from 100 people are not independent; use a person-level cluster bootstrap, expect a wider interval, and prefer a bound claim over a point claim.
- **Recommendation for the CTO:** write C2 as "Clopper-Pearson 95% lower bound >= 95% on >=800 answers from >=200 people, and every slice >= 93% point estimate with n >= 50 (a slice at n=50 with 93% observed has a lower bound near 82%; say so)". If 400 is the budget, the honest wording is "demonstrates >= 94% with 95% confidence; target 96-97% true rate".

## 5. Method notes by lane section

### A. Extraction and taxonomy linking
- **SkillSpan** (Zhang, Jensen, Sonniks, Plank, NAACL 2022): span-level hard and soft skill annotation, ~14.5K sentences / 12.5K spans; BERT baselines improve with domain-adaptive pretraining on job postings; nested skill/knowledge spans exist. Maps to STEP-1 reader as a deterministic cross-check. Domain is job postings, not CVs or tickets, so expect a drop on WorkRaven text. Cost M (fine-tune or use the released JobBERT checkpoints on Hugging Face).
- **ESCOXLM-R** (Zhang, van der Goot, Plank, ACL 2023): XLM-R-large continued-pretrained on ESCO text with an ESCO relation-prediction objective, 27 languages, SOTA on 6 of 9 tasks, biggest gains on short spans. Use as the encoder for STEP-2 candidate retrieval where the customer taxonomy resembles ESCO. Customer taxonomies (iMocha's own) will differ, so fine-tune a bi-encoder on the mapping set (500 phrases) instead of trusting ESCO alignment.
- **LLM extraction with grounding** (the plan): the exact-quote string match is a verified-citation constraint. Strengthen: require character offsets, normalise unicode and whitespace, and also check the quote supports the skill by a second NLI-style or LLM-judge pass (a real quote can still be about a different skill, e.g. "Spark plug" or a Go board game). Cost S.
- **Ambiguity (Spark, Go, R, SAP):** retrieval returns top-k taxonomy candidates; a closed-list pick conditions on the quote (the plan does this). Add per-alias cue lists ("RDD", "DataFrame", "pyspark" vs "Spark AR") and treat any pick with score margin below a threshold as "to review". Calibrate the margin so mapping precision hits its budget share.

### B. Fusion and proficiency
- **Noisy-OR**: P(has skill) = 1 - prod(1 - p_g) over *groups* g, each p_g capped for repeats. It matches "independent groups count once, repeats capped" directly: collapse repeats inside a group first (saturating function), then OR across groups. Demo cost S, explainable per message. Weakness: assumes independence across groups and cannot express contradiction; add a multiplicative penalty or a separate contradiction feature (STEP-3.6).
- **Logistic regression on group-level features** is the practical compromise: noisy-OR is a special case of logistic regression in odds space with log(1-p) inputs. Best for the 24h demo: hand-set noisy-OR priors now, logistic fit later.
- **Dawid-Skene / Snorkel** (label model for noisy sources, learns accuracies from agreement without ground truth): good fit for source-reliability learning in STEP-7.5, but you already have employee labels and a labelled set, so supervised fitting beats an unsupervised label model at your scale. Use Snorkel-style thinking only to estimate reliability for new sources before labels exist. Not a demo item.
- **Dempster-Shafer**: expresses ignorance cleanly, but conflict normalisation behaves badly and nobody on the team can debug it. Skip.
- **IRT / ordinal**: item response models treat proficiency as a latent trait and each evidence item as an item with difficulty and discrimination. Natural for assessments (many items per person), awkward for sparse work evidence. Pragmatic version: cumulative-link ordinal regression on level using features such as source cap, directness, level_kind counts. Gives P(level) for conformal tolerance. Cost M.

### C. Hitting a precision target via abstention
- **Selective classification** (Geifman and El-Yaniv 2017): choose confidence threshold so risk on accepted items is below a target with high probability, reported as a risk-coverage trade-off. Their ImageNet result (2% top-5 risk, 99.9% confidence, ~60% coverage) is the exact template for "5% risk, 95% confidence, X% coverage". Use the Clopper-Pearson bound on the held-out accepted set to pick the threshold. Cost S.
- **Conformal risk control** (Angelopoulos et al. 2023-24): controls expected value of a monotone loss; define loss = 1[|pred - true| > 1] or 1[no skill], pick lambda from calibration data. Guarantee is marginal and needs exchangeability (customer shift breaks it, so calibrate per customer). For ordinal levels, form a prediction set of levels and send only when the set fits inside a window of width 3 around the stated level. Cost M.
- **Calibration**: Platt (parametric, works with <1000 points), isotonic (non-parametric, needs more), report ECE and a reliability diagram; Guo et al. show modern nets are over-confident. LLM verbalised confidence is poorly calibrated; calibrate on your labelled pairs. Cost S.
- Caveat: marginal guarantees do not give per-slice guarantees; the plan's 93% slice floor needs slice-conditional calibration (Mondrian conformal) or enough data per slice.

### D. Repo expertise mining
- Evidence from the expert-finding literature: commit counts, files touched, code review participation and recency together beat commits alone; an artifact traceability graph weighting edges by recency reports up to 88% accuracy at method level (Bilkent paper). Avelino et al. (IEEE Software 2018) compare maintainer-identification heuristics and find commit-based measures work, controlling for size and recency. A 2022 survey (arXiv 2208.07501) lists open problems. I did not find an ICSE paper with a fitted decay function; the cited decay weights are chosen intuitively, so WorkRaven should fit its own half-life (section 3, item 9).
- Features to adopt for the GitHub reader (STEP-1, 3): merged PRs per language, months with activity (matches the plan's 3+ months rule), reviews given vs received (supports "leads or teaches"), repository size and maintainer role, share of commits surviving (code churn), recency half-life. Beware: language from file extension is a skill proxy, not proficiency; PR count says nothing about difficulty. Cost M.

### E. LLM judge and self-assessment
- **LLM-as-judge validation**: arXiv 2511.21140 gives the Rogan-Gladen correction, p_corrected = (p_observed + TNR - 1) / (TPR + TNR - 1), with a CI; it is unstable when TPR + TNR is near 1. The plan's "TPR and TNR reported separately" is correct. Add: estimate TNR on enough true negatives (a 90%-pass dataset has few), report bootstrap CI. Cost S.
- **Sycophancy analog**: Sharma et al. 2023, "Towards Understanding Sycophancy in Language Models" (arXiv 2310.13548, [recalled]) documents LLM flattery; the human analog here is acquiescence in confirm/deny prompts. Prompt framing "WorkRaven has inferred you have X" is an anchoring and acceptance cue; the plan's decision to show up to 3 pieces of evidence helps, but test a neutral two-sided wording in the internal pilot (STEP-6.5).
- **Self-assessment accuracy**: Mabe and West (1982) meta-analysis of 55 studies: mean self-rating vs performance validity .29 (SD .25); metasynthesis of 22 meta-analyses mean .29; 2024 meta-analysis of self-assessed intelligence r = .30 (115 samples). Kruger and Dunning (1999, [recalled]) report the least skilled overestimate most; later critiques attribute part of the pattern to regression to the mean and the better-than-average effect, so do not lean on "Dunning-Kruger" as a causal claim in the meeting. Implication: employee-chosen levels are a noisy label; the plan's choice to calibrate level on assessments only (STEP-7.2) is well founded.

## 6. Priority for a 24h demo

1. Compute and show the Wilson/Clopper-Pearson bound for the pass rule (S, 1 hour, high credibility).
2. Group-level noisy-OR with capped repeats and a per-source reliability table, calibrated to a probability on a toy labelled set; show a risk-coverage curve with a threshold at 5% risk (S-M).
3. Ordinal P(level) with a +/-1 mass test instead of floor/ceiling table (M, only if time).
Skip: Dempster-Shafer, Snorkel, IRT, ESCOXLM-R fine-tuning.

## 7. Sources

- SkillSpan: https://arxiv.org/abs/2204.12811
- ESCOXLM-R: https://arxiv.org/abs/2305.12092
- Selective Classification for Deep Neural Networks: https://arxiv.org/abs/1705.08500
- Conformal Risk Control: https://arxiv.org/abs/2208.02814
- Conformal Risk Control for Non-Monotonic Losses: https://arxiv.org/abs/2602.20151
- How to Correctly Report LLM-as-a-Judge Evaluations: https://arxiv.org/abs/2511.21140
- Comparison of debiasing methods for judge evaluation: https://alphaxiv.org/overview/2601.05420v1
- Finding expert developers using artifact traceability graphs: https://repository.bilkent.edu.tr/items/c4cbb88d-5fa3-4105-94f9-c509dbc143e4
- Source-code expertise survey: https://arxiv.org/pdf/2208.07501
- Avelino et al., IEEE Software 2018: https://homepages.dcc.ufmg.br/~mtov/pub/2018-ieeesw.pdf
- Self-assessed intelligence meta-analysis (2024): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11433033/
- Mabe and West 1982 (review): https://scholar9.com/publication-detail/validity-of-self-evaluation-of-ability-a-review-a--32328
- Metasynthesis of self-evaluation meta-analyses: https://www.scilit.net/publications/0fa200d67ce0eb3af83f082e631ab714
- Recalled, not opened: Guo et al. calibration https://arxiv.org/abs/1706.04599; Snorkel https://arxiv.org/abs/1605.07723; Angelopoulos and Bates gentle intro https://arxiv.org/abs/2107.07511; BLINK https://arxiv.org/abs/1911.03814; Sharma et al. sycophancy https://arxiv.org/abs/2310.13548; Dawid and Skene 1979; Kruger and Dunning 1999.
