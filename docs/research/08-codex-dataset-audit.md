**Verdict: useful adversarial fixtures, but not ready for a credible accuracy benchmark.** P001-P027 contain substantial technical evidence and recognizable workplace mess, alongside strong generator fingerprints, inconsistent level calibration, and overstated coverage.

I audited 231 skill labels and 116 trap entries against the supplied spec, taxonomy and nuance catalog. P028-P032 were excluded. No files under `data/` were edited; scripts stayed under `/tmp/codex-audit/`.

**Per-persona findings**

Realism: 1 = obviously fabricated, 5 = convincing export. `H` means hold because the bundle cannot establish a current level; it does not mean the person lacks the skill. Changes below are proposed evidence-supported ratings. Unlisted labels have no material disagreement. Leakage codes: **N** = numeric generator fingerprint; **S** = unusually explicit signposting; **none** = no material leak found.

| PID | Realism | Label issues and proposed treatment | Leakage | Fix list |
|---|---:|---|---|---|
| P001 | 3 | Terraform **1→2**: actual merged infrastructure changes exceed concepts-only knowledge. Docker **2→H**: CV-only. Technical writing **3→2/H**: readership and enforcement do not establish user task validation. | N | Replace PID-coded numbers; substantiate Docker and writing validation. |
| P002 | 4 | Workday **3→H**: guide shows procedural knowledge, but no audited transactions or tested configuration. HR operations **3→H** for the same evidence gap. | none | Supply anonymized case records; retain same-name control. |
| P003 | 3 | SQL **2→H**: stated read-only querying lacks a reviewed query/output. Other principal labels defensible. | none | Add query evidence; reconcile CV’s minikube claim with categorical “never held” truth. |
| P004 | 2 | Technical leadership **4→3**: rubric exists, but cross-team adoption and coaching outcomes are asserted privately. Technical writing **3→2/H** lacks task validation. | N, S | Repair pre-acquisition Ledgerly references; substantiate adoption; explain low review volumes. |
| P005 | 3 | System design **2→3**: independent deployed service design qualifies without cross-service ownership. Observability **2→3**: production profiling and leak repairs. Kubernetes **1→2**: guided manifests are application. Code review **2→3 candidate**: substantive defect catches, not volume, should decide. Python **1→H**. | N | Recalibrate against taxonomy; add review follow-through; fix Jira links. |
| P006 | 3 | Node.js **1→H**, SQL **1→H**: bootcamp/CV mentions lack assessed demonstrations. Frontend level 2 is convincing. | N | Preserve intentionally inflated CV; remove numeric encoding and mismatched ticket keys. |
| P007 | 2 | GCP **1→H**: exact retained knowledge comes from private calibration. Current delivery labels otherwise supported. | S | Vary reviews and follow-ups; remove credential-scan commentary from CV narrative. |
| P008 | 2 | Main operational levels are defensible after separating authorship from merges. | S | Remove numbered rotating bot titles; diversify review evidence and monthly totals. |
| P009 | 2 | Main positive levels supported. Python absence is private information; observable outcome should be hold. | S | Remove “No distributed data processing” clarification; vary repeated reviews and Sundays. |
| P010 | 4 | Java/Spring Boot/code review **4**, SQL/system design/API testing **3** are intentionally unrecoverable. **Keep hidden ability labels, require hold.** Docker **2** is also unobservable. | none | Explicitly exempt these from exact-level recovery scoring. |
| P011 | 2 | Positive current levels supported by post-return repairs. | none | Preserve career-break zeros; diversify copied reviews, follow-ups and Jira descriptions. |
| P012 | 3 | Selenium **2→3 pending reassessment**: last use September 2025 is inside the taxonomy’s two-year hint; elapsed time alone does not establish lost independence. Test-code scope alone also does not justify TypeScript’s cap. | none | Add a current Selenium exercise; repair `QA-2877` and identity oracle. |
| P013 | 3 | CI/CD **1→H**: lint/bundler edits do not demonstrate pipeline concepts in an assessment. Core frontend labels supported. | none | Repair identity oracle and source chronology. |
| P014 | 2 | Observability **1→2**: reviewed breadcrumb instrumentation is applied work. React 3 is defensible for evidenced React concepts, with mobile scope retained. | none | Vary Tuesday sampling; replace unvalidated rollback instructions with checked procedures. |
| P015 | 3 | Observability **1→2**: merged alarm changes are guided application. Linux **2→H**: access requests do not show administration. Docker **1→H** absent assessed understanding. | none | Preserve cert-collector exception; add actual Linux/lab evidence and first tenure month. |
| P016 | 2 | Performance testing 3 and Java 1 supported. Other principal labels plausible. | none | Remove Tuesday schedule; repair `QA-2877`; substantiate technical claims in guides. |
| P017 | 2 | High architecture/review labels have unusually good adoption evidence. AWS **2→H**: bounded implementation is asserted more strongly than exported evidence demonstrates. | N | Replace calendar dates and repeated yearly totals; repair repository numbering. |
| P018 | 2 | Main application/leadership labels supported. | N, S | Keep legacy duplicate; reconcile September ID conversion with March KC identity history. |
| P019 | 2 | Incident management **3→H**: decisive records explicitly excluded, with no matching missing-evidence trap. Java 2 remains plausible but weakly observed. | N, S | Add restricted-record-safe evidence or hold oracle; diversify dates. |
| P020 | 2 | UX research **3→2/H**: private recordings establish the hidden level; exported work has designer correction. No corresponding sparse-evidence trap. | N, S | Add observable research evidence or require hold; diversify dates. |
| P021 | 2 | Java **1→H**: current conceptual knowledge is privately assessed. Incident management **3→H**: technical recovery work does not establish independent incident coordination. | N | Preserve no-message consent gate; separate skill uncertainty from outreach prohibition. |
| P022 | 3 | Account management **1→H**: pilot conversions lack the reviewed account plan/guidance needed for K3 level 1. Other main labels plausible. | none | Repair low annual opportunity totals and stale open-stage records. |
| P023 | 3 | Technical writing 2 is reasonable; onboarding 3 has adoption evidence. Expansion records contradict categorical “no solution selling,” so **0→H** pending attribution. | none | Reconcile stages with notes; add field-level CRM correction evidence for level 1. |
| P024 | 3 | Incident management **1→2**: actual guided escalation, evidence collection and update cadence exceed concepts-only knowledge. | none | Reconcile resolution minutes with multi-day elapsed dates; preserve repetitive L1 notes. |
| P025 | 4 | Talent acquisition **3** is intentionally hidden. Workday **2**, HR operations **1**, stakeholder management **2→H**: claims/course completions lack task-level evidence. | none | Extend intentional hold oracle to all unsupported positives. |
| P026 | 2 | Workday **3→H**: requester RITMs and a migration guide do not establish current independent configuration. SAP **2→H**: historical use alone cannot determine today’s exact decayed level. | none | Repair pre-acquisition Ledgerly hypercare; add current competency evidence. |
| P027 | 3 | AWS **0→1/H**: a current verified foundational AWS exam conflicts with categorical absence, although it establishes no operational ability. Python **1** needs stronger assessed evidence. | S | Preserve demo/API-testing boundary; repair Salesforce IDs and unsupported backlog key. |

**Cross-persona statistics**

Computed from all 430 listed PRs across 17 personas. Gaps are consecutive **created-date differences within each persona**, pooled afterward. These are selected samples, not complete arrival streams.

| Measure | Result |
|---|---|
| Inter-PR gaps | 413 gaps; median **42 days**, mean **57.0 days**, range **1-1,129 days** |
| Gap distribution | 0-7d: **13**; 8-30d: **97**; 31-60d: **184**; 61-90d: **57**; 91-365d: **61**; >365d: **1** |
| Exact normalized title duplication | **0/430 excess duplicates, 0%**; no cross-persona duplicate titles |
| Cross-persona CV 6-grams | **43/5,996 distinct normalized 6-grams, 0.72%**, occur in multiple personas; versions combined by PID |
| PR states | **426 merged, 4 closed, 0 open**; **13/17** GitHub bundles contain only merged PRs |
| Created weekdays | Mon **70**, Tue **158**, Wed **67**, Thu **54**, Fri **34**, Sat **14**, Sun **33** |
| Repeated review follow-ups | Identical “Added regression fixture and reran checks.” **24 times across four personas**; another stock follow-up **8 times** |

The CV duplication is mostly legitimate convention: “to the best of my knowledge” appears in eight personas. It is weaker evidence of fabrication than the work-system patterns. CVs are reasonably varied, and P006’s polished bloat is intentional.

The strongest timing fingerprints are:

- All **68 PRs** in P017/P018/P019/P021 were created on the **12th**. All **58 Jira issues** in P017-P021 run from the **5th to the 24th**, exactly 19 days.
- P016 has **25/27 Tuesday PRs**; P014 has **24/36**. This resembles scheduled sampling without documented selection rules.
- P017 reports exactly **21 merged PRs and 446 reviews** in every year from 2022 through 2025.
- Weekends exist, so “no weekend work” is false. Holiday/calendar behavior is inconsistent: regular schedules continue mechanically, while other batches exclude weekends entirely. Sparse representative samples cannot establish a reliable holiday effect.

Volumes must use monthly totals, not sampled PR counts. P003’s **798 incidents in 2025** and P024’s **1,704** fit §5. P008’s **438 merges** are an intended attribution trap; **85 authored merges** are plausible. Exceptions needing explanation include P015’s **37 PRs/16 reviews**, P004’s **16 reviews**, P012’s **102 reviews**, and P022’s **19 created/15 closed opportunities** in 2025. P015’s nine certifications are intentional.

Every persona has HCM, CV and LMS evidence. Several identical source mixes are role-plausible, but universal LMS presence, schema differences aligned with batches, and repeated review templates expose generation boundaries.

**Leakage and shared-world consistency**

No literal `true_level`, fault ID, “planted,” or “synthetic” disclosure was found in the audited bundles. The real leakage is structural:

- **123/123 PR numbers** in P001/P004/P005/P006 end in their PID’s last digit. P017-P021 also use conspicuous persona-based number blocks.
- Statements such as “92% of current text,” “approximately 85 percent,” and repeated explanations of exactly which skill a contributor did not exercise supply unusually convenient attribution answers. Revision history is appropriate; this repeated precision is signposting.
- P001/P002 correctly have distinct IDs, emails and departments despite sharing a name.
- P012/P013 have reciprocal HCM email histories, while GitHub retains the original addresses. However, GitHub also supplies the correct `linked_employee_id`. Stable-key joining is therefore recoverable; an unconditional `join_neither` oracle is too strong.
- P022/P027 share exactly two opportunities. Dates, products, industries, stages, amount bands and complementary **70/30 splits agree**.
- All PR repos use the specified Kestrel set; there are no duplicate `(repo, PR number)` objects. Nevertheless, global numbering chronology breaks: P017’s `billing-core#1701` is created in January 2025 after P004’s `#5484` in March 2024.
- `QA-2877` is two different issues: P012’s flaky-test quarantine and P016’s performance scenario. P005 also uses unlisted `LEDGER` Jira keys; P027 references `SE-41`.
- Manager reuse needs an organizational explanation: `KC-10388` manages both Data Engineering P001 and AE P022; `KC-10544` manages mobile P014 and CSM P023. P007 reports to P004, Billing’s engineering manager.
- P004’s 2023 ADR and P026’s 2023 hypercare mention Ledgerly before the March 2024 acquisition. These are unplanted chronology defects.

Exact hidden ability is intentionally unavailable for P010 and P025. Other private calibrations, notably P007 GCP, P019 incident management, P020 UX research and P021 Java, need explicit hold outcomes. Missing work evidence supports abstention, not proof of zero knowledge.

**S1.1 coverage**

Counts normalize `not_held`, `not_really_held`, false-negative variants and `decay`. They count declared traps, not independently validated tests.

| S1.1 row | Traps / PIDs | Declared fault_ids | Coverage gap |
|---|---:|---|---|
| Invented skill | 1 / 1 | F27 | Unverifiable AWS cert does **not** test a nonexistent evidence quote. Effective quote-integrity coverage absent. |
| Wrong person | 29 / 20 | F10-F14, F18, F21-F23, F33-F34; uncatalogued alias case | Good variety; Rahul oracle conflicts with stable IDs. |
| Wrong skill mapping | 21 / 17 | F06, F16, F25, F35 | F35 on P027 is a practice-boundary case, not the catalog’s mismatched job-family plant. |
| Skill not really held | 25 / 15 | F01, F04-F05, F08-F09, F15, F17, F26-F27 | Includes intentional invisible positives; score hold separately from absence. |
| Skill decay | 11 / 9 | F24, F28 | Exact retained levels often lack current demonstrations. |
| Level two or more off | 23 / 19 | F02, F06, F12-F13, F17, F19-F20, F25, F29-F30; uncatalogued control | Several are one-level differences; distinguish K3 exact-match failures from K4 tolerance. |
| Message misread | 3 / 3 | F06 | CV convention noise does not test interpretation of message wording. Requires pilot. |

Outside S1.1: duplicate counting **1**, Go positive control **1**, consent **1**. Total **116**. Catalog faults absent from this audited subset: **F03, F07, F31, F32, F36**. This does not imply absence from skipped personas.

**Top 10 fixes, ranked by impact**

1. Separate hidden ability labels from observable send/hold oracles; repair Rahul `join_neither`.
2. Recalibrate levels using autonomy, guidance and adoption, without scope or volume shortcuts.
3. Eliminate PID-coded identifiers and restore globally chronological repository/Jira numbering.
4. Replace calendar arithmetic and repeated yearly totals with coherent activity histories.
5. Add a genuine nonexistent-quote test for the blocking invented-skill row.
6. Repair Ledgerly chronology and conflicting `QA-2877`.
7. Replace copied reviews and mirrored Jira/PR prose with distinct, linked records.
8. Add current assessments for exact decay labels; allow uncertainty otherwise.
9. Reconcile manager assignments, CRM stages, Salesforce identifiers and ServiceNow durations.
10. Report message misreading as untested; separate declared trap counts from effective coverage.