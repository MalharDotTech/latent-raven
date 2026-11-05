# 09 Opus realism and label-honesty review (depth sample)

Stance: Indian tech hiring manager plus HR data analyst. Sample: P001, P004, P006 (A, Sonnet), P008, P010 (B, Codex gpt-6.1-sol), P013, P015 (C, Sonnet), P019 (D, Codex), P024 (E, Sonnet). Every file was read. K4 level lines are the yardstick for labels.

**Verdict.** The content layer (CVs, review comments, ADRs, ticket text) is often good enough to fool a recruiter. The structural layer (IDs, dates, monthly aggregates, cross-source links) would fail a two-minute look by any data engineer. Labels are the author's intent, not an independent judgment, and several contradict the taxonomy or each other. Fit for trap unit tests after fixes, not for a precision claim.

## 1. Per persona

### P001 Priya Sharma (A) - control positive
- Fake. All 38 PR numbers end in 1 (1641, 1681 ... 4731). Monthly `by_ext` is random noise: `.tf` 306 files in 2025-02 and Terraform in most months, for a person labelled Terraform 1. 6 of 12 PR-to-ticket pairs merge before the ticket exists (PR 1961 fixes DATA-1851 on 2023-05-02, ticket created 2023-05-10). CV v1 says "joining Kestrel Cloud Pvt Ltd on 07 Nov 2022", which nobody writes in an application CV.
- Convincing. Review "this df.collect() will pull whole month to driver?". "task_id changes will reset history in the UI". CV v2 "Cut billing_events_silver runtime from 3h10m to 55m".
- Labels. Terraform 1 should be 2: three reviewed, merged infra PRs is the K4 L2 definition, and L1 means "assessed exercise, no workplace delivery". Docker 2 rests only on the CV skills line, the exact pattern labelled not-held for Kubernetes in the same file. Mark it hold.
- Traps. The CV-lineage trap expects `hold` on Airflow, whose true level is 4. The F18 trap expects `join_neither` on Python for the correctly ID-linked control. The F10 trap names PySpark, but the bot PRs bump boto3 and the Amazon provider, and `author_type: bot` makes it trivial.

### P004 Vikram Reddy (A) - decayed Java expert, now EM
- Fake. The ARCH page body says "Page created by Vikram; sections 2-5 written and revised by the engineers listed above". That is the F34 trap written into the evidence. Monthly activity shows `.java` edits in 2025-09, 2026-03 and 2026-08, which contradicts the decay plant. BILL keys are non-monotonic (BILL-188 in Sep 2016 after BILL-694 in Jun 2016). 7 of 25 tickets have an assignee before the ticket was created.
- Convincing. "design looks ok, not reviewing the code line by line. @sana-m pls". ADR-014 on gapless GST invoice numbering. "(Updated Mar 2025 for Director promotion panel)".
- Labels. Java 2 is defensible on evidence. The right action is hold, not "send at 2" to a Director-track manager. Truth contradicts itself: `would_accept_levels [2,3]` versus notes "will push back if offered Java 2". Technical leadership 4 rests on his own CV and pages. "Adopted by other teams" is not in the bundle. By evidence it is 3.

### P006 Rohan Mehta (A) - LLM-polished junior CV
- Fake. PR-to-Jira keys are shifted by one throughout. PR "WEB-6046 reapply FilterBar fix" points to a ticket titled "EU invoice labels i18n". 15 of 20 linked PRs merge before their ticket exists. The internship employer is "Early-stage fintech startup, Pune", where a real CV names it.
- Convincing. The path from E&TC at Jaihind College of Engineering, Kuran, through Masai School to SDE-1. "revert WEB-5956 (broke filters)". The LLM summary "Highly motivated and results-driven" is an honest plant.
- Labels. React, TypeScript and JavaScript at 2 are fair. Node.js 1 from a CV capstone breaks the L1 definition. Use hold. AWS `has_skill: false` from an unverifiable self-reported CLF-C02 asserts an absence the evidence cannot show. Label it unknown.

### P008 Mohammed Faizal (B) - SRE with bot-inflated merges
- Fake. Monthly `by_ext` cycles the same six pairs (6/4, 24/16, 21/14, 30/20, 18/12, 15/10) ten times. Eight reviews reuse three sentences verbatim. Every infra-live PR has `{.tf:3,.yaml:2}`. Bot PRs are numbered "(1)" to "(9)" with identical +8-8 diffs. Every PR body starts with the skill name ("Docker image...", "Observability silence..."). PLAT-6288 says "Faizal took release handoff after code review; only merged the release bundle." The export ships `metric_definitions` and `bot_prs_merged_by_self`, which hands the engine the answer.
- Convincing. CV "GitHub dashboard shows 438 merges in 2025". ENG-3012 "Never edit the state just to silence a plan difference."
- Labels. Nine skills all at 3, all with `would_accept [2,3,4]`, and all with `assessed_level: 3`, though no assessment file exists. Docker 3 from one PR should be 2. Code review 3 from eight templated reviews is 2 at best.

### P010 Siddharth Joshi (B) - contractor, private repos
- Fake. Jira descriptions narrate the design ("restricted review URL omitted from cross-tenant export"; "Siddharth bulk-closed customer followups ... no broker changes"). Every ticket is assigned on the 1st with 3 story points. An IIT Bombay CS 2013 graduate who spent 11 years in TCS and then became a Kestrel contractor is a profile any Indian hiring manager would question.
- Convincing. "Client names not included as per NDA." "Total Experience: 10 years 10 months". "Notice period: as per project release".
- Labels. True Java 4 rests on a "private assessor" that cannot be checked. The trap expects `hold`, but `would_accept [3,4]` means sending Java at 3 from the CV earns a Yes. Trap scoring and answer scoring disagree on the same pair. The `identity_links` block resolves F21 trivially.

### P013 Rahul Kumar (C) - frontend, name collision
- Fake. "Zoho Books-like invoicing module": a Zoho employee would name the product. Monthly `by_ext` is a fixed ratio of `merged_prs`.
- Convincing. The whole CV ("Current CTC: 9.2 LPA", CBSE 84%/88%, DoB, "Kannada (read, write)", declaration with place and date). The revert-then-v2 pattern on WEB-3601, with coherent Jira dates. Review "key={index} will break reorder".
- Labels. React and TypeScript 3 are fair. CI/CD 1 from an ESLint config change misuses L1 again. The `join_neither` trap is untestable inside a bundle already linked by employee ID. It also contradicts the "clean control" summary: the engine either sends React 3 or joins neither, not both.

### P015 Aditya Verma (C) - certificate collector
- Fake. PR titles "(copied from recon)" and "(copied from data-platform)" are signposts no engineer would write. CKAD and KCNA show `expires: null`. The proctoring flag format is `tab_switch_x4` here and `tab_switch:1` in P001.
- Convincing. A 9-certificate list at the top of a 2.5-year CV. "fix: eventbridge cron tz (UTC vs IST)". A copy-paste IAM PR, then a revert, then a least-privilege redo with 8 review comments.
- Labels. AWS 2 is fair, but Tara "Intermediate" maps to 2 here and to 3 for SQL in P001. Docker 1 from courses alone should be not-held. Observability 1 should be 2, because he shipped alarms. Kubernetes carries three traps with three different expected behaviours (`hold`, `send_at_level_1`, `not_extract`). No engine can pass all three.

### P019 Lakshmi Narayanan (D) - name-order variance
- Fake. The CV says "Internal directory and Jira have N. Lakshmi; payroll has expanded name." and "Don't ask me to maintain Java billing code alone." GitHub `co_authors[].contribution` and `author_contribution` are fields GitHub does not have. Every PR is opened on the 12th and merged on the 16th, and every ticket runs from the 5th to the 24th. billing-core PR #1901 lands in 2025, while P004's billing-core PRs are past #6800 by then.
- Convincing. ENG-419 is the best doc in the sample ("An opaque object key is not an access check"). Review "possession is not authorisation". The "N. Lakshmi" initial (father's name as initial) is culturally correct.
- Labels. Security 4 fits the K4 L4 line, but the support for it is narrated rather than shown. Linux 3 from one SSH-key ticket plus Infosys support should be 2. Incident management 3 cites only the CV and a "private assessor". Drop it or score it as hold-only.

### P024 Ramesh Yadav (E) - high-volume L1
- Fake. Monthly counts are exactly 95 for four straight months. The note says "96 of ~4,900" but 98 rows are listed. Priorities are "P1-P4" rather than ServiceNow's "1 - Critical" format. `resolution_time_minutes: 25` sits on a ticket open for 4 days.
- Convincing. "sir kindly check". "Re: Re: Re: FW: URGENT issue with billing run". "Customer entered IFSC in wrong field". Legal name "Ramesh Suresh Yadav", which follows the Maharashtrian convention.
- Labels. ServiceNow 2 is honest under the taxonomy. Incident management 1 should be 2: INC "Raised P1, paged on-call L2 ... Updated cust every 30 min" is the L2 line verbatim. The F16 trap on the same skill expects `hold` while truth says held at 1.

## 2. Missing realism (all personas)

- Jira has no comments, changelog, sprint, epic link, fixVersion or issue links. `description_excerpt` is mostly null (A, C) or narrator prose (B, D).
- GitHub has no commit counts, CI status, drafts or named reviewers. PR bodies are absent (A, C) or keyword-seeded (B, D).
- Workday has no supervisory org, cost center, performance or calibration rows, leave gaps or location transfers.
- LMS shows only completions. Real Docebo exports are dominated by enrolled-never-finished rows, given the 12.6% MOOC completion rate cited in the fault catalog.
- ServiceNow has no caller company, contact_type, close_code, work notes or SLA breach flags.
- P008 is an on-call SRE with zero incident records. P001 has been primary on-call since 2023 and also has none. P024's CV claims "Maintaining knowledge base articles" with no authored KB.
- Colleagues are placeholders ("billing-maintainer-kc", "operator-maintainer"). Real data names people, and those names recur across sources.

## 3. Model comparison

- **Batch C (Sonnet) is the most realistic.** IDs vary, PR-to-Jira chronology is coherent, reverts and re-applies happen, Indian CV conventions are exact, and certificate timelines are plausible. Its weaknesses are formulaic monthly ratios and signposted PR titles.
- **Batch E (Sonnet) has the best mess.** Its customer text could pass as a real export. Its aggregates contain placeholders.
- **Batch A (Sonnet) has the best domain content and the worst structure.** It has a persona-digit fingerprint in every PR number, broken ticket chronology, an off-by-one key map in P006 and random `by_ext` noise that contradicts the labels. This looks like one buggy generator script, not a model trait, because batch C uses the same model and is clean.
- **Codex B reads like a test fixture.** It has sequential IDs, modular cycles, verbatim repeats, keyword-seeded bodies, answer-bearing metadata fields and flat labels (nine skills at 3). Its CVs are genuinely good: terse, "till date", "as per NDA".
- **Codex D writes the strongest technical prose** (ENG-419), and gets the name convention right. Its cadence is mechanical, it invents schema fields and it explains its traps inside the evidence.
- In short, Sonnet writes like an employee. Codex writes like a QA engineer describing an employee. Both fail on cross-source structure, which no LLM should be asked to hand-generate.
- `scripts/validate_personas.py` passes all of these. It checks schema, not coherence.

## 4. Can this support a 95% precision claim to a CTO?

No. Reasons, each checkable.
- Circular truth. The same model wrote the evidence, the label and the simulated answer (`would_accept_levels`). A Yes rate computed from that is the generator agreeing with itself.
- Sample size. About 32 x 8 = 250 labelled pairs, clustered in 32 people. An engine observed at 97% on 150 sends has a Wilson 95% lower bound near 92.9%, before clustering. A 97% run cannot certify 95%.
- Base rate. Every persona carries 3 to 7 traps. Precision measured on trap-dense data does not transfer to a real workforce in either direction.
- Bias in both directions. Signposted traps (B, D) inflate engine scores. Contradictory traps and noisy aggregates (A) cap scores below what a good engine deserves.

Claims you can make: "The engine handles fault types F10, F14, F18, F24, F26, F28 and others as specified, on N hand-checked cases each." "The pipeline end-to-end produces evidence-cited decisions in the customer taxonomy." "These failure modes are covered by regression tests."

Claims you cannot make: any precision, coverage or Yes-rate number as a forecast for real employees. Any fairness claim. 32 personas cannot carry name, gender and university slices.

**Five improvements, in order.**
1. Generate structure with a script, not a model. Use one world registry with per-repo PR counters, per-project Jira key counters, a shared calendar and named colleagues. LLMs write only free text into slots. Add a coherence validator covering ticket-before-PR, assignee-after-created, monotonic keys, `monthly_activity` consistent with listed items and `by_ext` consistent with the role.
2. Remove narration. Delete every sentence that explains a trap (P004 page body, P008 PLAT-6288, P010 all descriptions, P019 CV and co-author fields, P015 "(copied from ...)"). Express ownership through real structures: page history, `Co-authored-by` trailers, Jira changelog.
3. Re-label blind. Two human raters label each skill against the K4 lines without seeing generator intent, then adjudicate. Fix the systematic L1 misuse (L1 means assessed only). Resolve the contradictory traps (P001 Airflow and Python, P015 Kubernetes, P024 incident management). Fix the vendor-label-to-level mapping. Remove `assessed_level` where no assessment exists.
4. Split scoring into two instruments. Trap tests check behaviour (send, hold, join). The answer simulation checks `would_accept`. Today P010 and P013 make the two disagree on the same pair.
5. Calibrate to real exports. Pull 3 to 5 anonymised real Jira, GitHub, Workday and ServiceNow exports (Finvu's own repos would do for GitHub and Jira). Copy their field sets, null rates and description lengths. Then add 10 or more boring personas with zero or one trap, so the base rate resembles a real org.

## 5. Decisions the user should own

- **What a level means.** Is a 3-year L1 agent who works tickets alone "with guidance" (L2)? Does L1 ever apply to someone with workplace output? The generators answered this inconsistently. It is a product definition, not a fact.
- **Send policy for decayed or senior skills.** Messaging a Director-track EM "Java level 2" is a relationship risk, whatever the label. Decide hold versus send for managers and decayed experts.
- **Hidden-truth personas (P010, P019).** Should the engine be rewarded for sending a CV-backed level the person would accept, or for holding because the evidence is thin? That choice is the difference between evidence precision and answer precision.
- **Identity policy.** Decide what join evidence is enough (verified alias, email history, employee ID), and whether an ambiguous join zeroes all of a person's sends or only the contested sources.
- **Trap prevalence and mix.** Which faults, at what rates, reflect iMocha's real customers? The fault catalog marks 13 rows as "Assumed". Only conversations with customers can set those rates.
- **Label a blind 50 yourself.** Read 50 skill pairs as a hiring manager would, without the truth files. Your disagreement rate with the generators is the best single number you can put in front of a CTO.

The data looks real at the sentence level and fake at the spreadsheet level, and a CTO's team reads spreadsheets.
