# Persona dataset spec (v1)

Contract for every persona generator (Claude or Codex). Read fully before writing anything.

Purpose: realistic multi-source employee evidence for 32 synthetic employees of a fictitious customer, with hidden ground truth and planted real-world faults, to test any skill-inference engine against the WorkRaven eval contract (`docs/sprint/01-eval-contract-vs-engine.md`, L1 + L2).

## 0. Hard rules

1. **Grounded, not invented.** Certification names, codes, issuers, validity: only from `data/grounding/certifications.json`. Course titles: only from `data/grounding/courses.json`. Job titles: follow `data/grounding/job_ladders.json`. PR and ticket wording: imitate the style, length and mess of `pr_title_samples.json` and `issue_style_samples.json` (short, technical, sometimes cryptic, prefixes like `fix:`, ticket keys, typos). Universities and prior employers: from `names_and_universities.json`. Tech combos: plausible per `tech_cooccurrence.json`. Faults: from `docs/research/07-real-world-nuances.md` fault catalog (cite `fault_id`).
   **Fallback (grounding corpus is partial, see `data/grounding/README.md`):**
   - Certifications: only from `certifications.json`. If a needed cert is missing (e.g. SHRM, CIPD), omit it; do not invent.
   - Courses: only from `courses.json`; otherwise use an internal course prefixed `internal:` (e.g. `internal: Kestrel Sales Foundations`). Never invent a public course title.
   - Job titles, universities, prior employers: if not in the grounding files, use only widely known real entities you are certain exist (e.g. IIT Madras, VIT Vellore, PES University, TCS, Infosys, Wipro, Freshworks, Zoho, Razorpay, Flipkart). List each one you used in the batch note under "from model knowledge".
   - Names: realistic for the tech workforce (the Forebears list skews to general population; prefer names common among urban graduates).
2. **Skills from the taxonomy.** Truth labels use `skill_id`s from `data/taxonomy/customer_taxonomy.json` only. Levels use that skill's family scale (K4 = 1..4, K3 = 1..3).
3. **No label leakage.** Evidence files never contain the truth file's words or levels. A source may state a level only if real systems would (e.g. an HCM self-declared skill profile, an assessment report). Never write "this person is Level 3 in X" in a CV, PR or ticket.
4. **Fictitious people, real world.** Names realistic and diverse, never a real identifiable person. Employers, universities, cities, OSS projects may be real. Kestrel's internal repos, Jira projects, Confluence spaces are fictitious and consistent across personas (see §3).
5. **Anti-slop.** Real CVs are uneven: some terse, some bloated, some with typos, Indian English, inconsistent tense, tables, "Roles & Responsibilities", "Declaration". At most 2 of 6 personas per batch may have polished LLM-style CVs, and only when that is the planted fault. Avoid the words "spearheaded", "leveraged", "synergy", "passionate" unless the persona is planted as an LLM-written CV.
6. **Internal consistency.** Dates line up across CV, HCM, GitHub, Jira, certs. As-of date: **2026-10-31**. Every evidence item has a date. Volumes realistic for role and tenure.
7. **Do not touch** other personas' folders, the spec, taxonomy or grounding files.

## 1. Customer

**Kestrel Cloud Pvt Ltd** (fictitious). India-HQ B2B SaaS (billing, payments reconciliation and analytics platform for mid-market companies). ~1,800 staff. Offices: Bengaluru (HQ), Pune, Hyderabad, Berlin (EU, ~60 staff), Austin (US sales, ~40 staff). Founded 2015. Acquired "Ledgerly" (Pune, 40-person startup) in March 2024; Ledgerly staff kept legacy IDs `LGR-xxxx` for 6 months then got `KC-` IDs, some records duplicated. Uses Workday HCM (migrated from SAP SuccessFactors in 2023), GitHub Enterprise, Jira Cloud, Confluence, ServiceNow (internal IT + customer support), Salesforce, an LMS ("Kestrel Learn" on Docebo), and iMocha Tara assessments for some teams since 2025.

Email format: `firstname.lastname@kestrelcloud.com`; collisions get a digit (`priya.sharma2@`). Employee IDs `KC-10001`..`KC-12999`; contractors `KCC-5xxx`; Ledgerly legacy `LGR-0xxx`.

## 2. File layout

```
data/
  bundles/<PID>/            # ENGINE INPUT. Engines may read only this.
    manifest.json
    hcm.json
    cv_v1.md [cv_v2.md ...]
    github.json             (if any)
    jira.json               (if any)
    servicenow.json         (if any)
    salesforce.json         (if any)
    certs.json              (if any)
    lms.json                (if any)
    assessments.json        (if any)
    docs/<doc_id>.md        (if any; authored Confluence pages)
  truth/<PID>.json          # HIDDEN. Engines must never read.
```

PID = `P001`..`P032`.

## 3. Shared Kestrel world (use consistently)

- GitHub org `kestrel-cloud`. Repos: `billing-core` (Java/Spring Boot), `recon-engine` (Go), `ledger-api` (Go), `data-platform` (Python, PySpark, Airflow DAGs), `analytics-dbt` (SQL/dbt on Snowflake), `ml-forecasting` (Python), `web-console` (TypeScript/React), `mobile-app` (React Native), `infra-live` (Terraform, Helm), `platform-k8s` (Kubernetes manifests, Go operators), `qa-automation` (Java Selenium legacy, TypeScript Playwright since 2025), `perf-tests` (JMeter, k6), `ledgerly-legacy` (Node.js, from acquisition).
- Bots present in org: `dependabot[bot]`, `renovate[bot]`, `kestrel-release-bot`.
- Jira projects: `BILL`, `RECON`, `DATA`, `WEB`, `MOB`, `PLAT`, `QA`, `SEC`, `PM`.
- ServiceNow: `INC` (customer-facing incidents), `RITM` (internal IT requests).
- Confluence spaces: `ENG`, `DATA`, `ARCH`, `PM`, `PEOPLE`, `SALES`.

## 4. Schemas

All JSON. Dates ISO `YYYY-MM-DD` or `YYYY-MM`. Unknown = omit the field, don't invent.

### 4.1 manifest.json
```json
{"person_ref": "P001", "customer": "kestrel-cloud", "as_of": "2026-10-31",
 "sources": [{"source_id": "hcm_KC-10442", "source_type": "hcm", "path": "hcm.json"},
             {"source_id": "cv_2026_03", "source_type": "cv", "path": "cv_v2.md", "lineage_key": "cv-P001", "received": "2026-03-14"}]}
```
`source_type` ∈ `hcm | cv | github | jira | servicenow | salesforce | certs | lms | assessments | authored_doc`.

### 4.2 hcm.json (Workday export style; may contain real-world errors when planted)
```json
{"employee_id": "KC-10442", "legacy_ids": [], "worker_type": "employee|contractor|intern",
 "legal_name": "...", "preferred_name": "...", "emails": [{"email": "...", "from": "2021-06", "to": null}],
 "gender": "F|M|X|undisclosed", "location": "Bengaluru", "country": "IN", "department": "Data Platform",
 "manager_employee_id": "KC-10012", "hire_date": "2021-06-14", "rehire_dates": [],
 "job_history": [{"title": "Data Engineer II", "grade": "P2", "from": "2021-06", "to": "2023-03"}],
 "project_allocations": [{"project": "Recon v2 migration", "role": "Data Engineer", "from": "2023-04", "to": "2024-09", "allocation_pct": 80}],
 "self_declared_skills": [{"skill_text": "PySpark", "self_level": 3, "declared_on": "2025-04"}],
 "messaging_consent": {"notice_given": true, "opted_out": false, "eu_opt_in": null},
 "education": [{"institution": "...", "degree": "B.Tech", "field": "...", "year": 2019}]}
```
`self_declared_skills.self_level` uses the customer scale (real Workday skill profiles do this). Include for ~half of personas.

### 4.3 cv_vN.md
Plain markdown transcription of the CV as the person submitted it (at hire or later update). Mess allowed. Two versions only when planted (lineage).

### 4.4 github.json
```json
{"login": "psharma-kc", "account_type": "enterprise", "linked_employee_id": "KC-10442",
 "pull_requests": [{"repo": "kestrel-cloud/data-platform", "number": 1832, "title": "...", "state": "merged",
   "created": "2025-01-08", "merged": "2025-01-10", "merged_by": "self|other|bot", "author_type": "human|bot",
   "files_ext": {".py": 6, ".yaml": 1}, "additions": 240, "deletions": 31,
   "co_authors": [], "review_comments_received": 4, "labels": ["data"]}],
 "reviews_given": [{"repo": "...", "pr_number": 1840, "date": "2025-01-12", "state": "APPROVED|CHANGES_REQUESTED|COMMENTED", "comment_count": 3, "sample_comment": "..."}],
 "monthly_activity": [{"month": "2025-01", "merged_prs": 9, "reviews": 14, "by_ext": {".py": 30, ".sql": 4}}],
 "public_profile": {"personal_repos": [...], "oss_contributions": [...]} }
```
List 15-40 individual PRs (most representative + the traps), and `monthly_activity` for the full tenure.

### 4.5 jira.json
```json
{"issues": [{"key": "DATA-2231", "type": "Story|Bug|Task|Epic|Sub-task", "summary": "...", "description_excerpt": "...",
  "component": "...", "priority": "...", "status": "Done", "resolution": "Done|Won't Do|Duplicate",
  "reporter_is_self": false, "assignee_history": [{"assignee": "self|other", "from": "2025-02-01"}],
  "resolved_by_self": true, "created": "...", "resolved": "...", "story_points": 3, "labels": []}],
 "monthly_activity": [{"month": "2025-02", "resolved_as_assignee": 6, "reported": 2}]}
```

### 4.6 servicenow.json / salesforce.json
ServiceNow: incidents/requests with `number`, `short_description`, `category`, `assignment_group`, `resolved_by_self`, `resolution_notes_excerpt`, `reassignment_count`, `opened`, `resolved`, `priority`. Salesforce: opportunities/activities with `opp_id`, `account_industry`, `stage`, `amount_band`, `role` (owner|overlay_se|csm|sdr), `credit_split_pct`, `close_date`, `products`, `notes_excerpt`.

### 4.7 certs.json
```json
{"certificates": [{"name": "<exact from grounding>", "issuer": "...", "code": "...", "issued": "2024-05",
  "expires": "2027-05", "evidence_form": "badge_url|pdf_upload|self_reported",
  "badge_url": "https://www.credly.com/badges/<uuid>", "verification_status": "verified|unverifiable|failed|not_checked"}]}
```

### 4.8 lms.json
Kestrel Learn completions: `course_title` (from grounding or internal clearly marked `internal:`), `provider`, `completed`, `time_spent_minutes`, `quiz_score_pct` (if any), `assigned_by` (self|manager|compliance).

### 4.9 assessments.json
iMocha Tara / vendor results: `vendor`, `assessment_name`, `skill_text`, `date`, `raw_score_pct`, `percentile`, `vendor_proficiency_label` (vendor's own words, not the customer scale), `proctoring_flags`.

### 4.10 docs/<doc_id>.md
Front matter: `doc_id, space, title, created, last_edited, author, contributors, page_views_90d`. Body: realistic excerpt (150-600 words), real technical content consistent with persona's level. Planted faults may include copied or co-authored pages.

### 4.11 truth/<PID>.json (HIDDEN)
```json
{"pid": "P001", "summary": "2-3 sentence backstory, private",
 "archetype": "...", "batch": "A", "generator": "claude-sonnet-5-5 | codex gpt-6.1-sol ...",
 "skills": [{"skill_id": "python", "has_skill": true, "true_level": 3, "self_perceived_level": 3,
   "would_accept_levels": [2, 3, 4], "assessed_level": 3,
   "last_used": "2026-10", "evidence_refs": ["github:#1832", "cv_v2:Experience/Kestrel"],
   "why": "one line: what in the evidence establishes this, honestly"}],
 "decoys": [{"skill_text": "Kubernetes", "mapped_skill_id": "kubernetes", "has_skill": false, "why": "listed only + 2019 intro course"}],
 "traps": [{"fault_id": "F07", "s11_row": "skill_not_really_held", "skill_id": "kubernetes",
   "plant": "what was planted where", "expected_engine_behavior": "hold|not_extract|send_at_level_N|join_neither|do_not_message"}],
 "answer_behavior": {"reply_probability": 0.7, "yes_to_everything": false, "flattery_bias": 0,
   "notes": "accepts one level up readily"},
 "messaging_allowed": true}
```
- `true_level` = what a fair expert assessor would rate today (decay included).
- `would_accept_levels` = levels the person would answer "Yes" to; models flattery (overclaimers accept higher, underclaimers lower).
- Include 6-15 `skills` per persona (all real skills, held or not-held-but-plausible) and 1-6 `decoys`.
- Every planted fault appears in `traps` with `expected_engine_behavior`.

## 5. Volumes (realistic ranges)

| Role, tenure | GitHub PRs/yr | Reviews/yr | Jira resolved/yr | Certs | LMS courses |
|---|---|---|---|---|---|
| IC engineer 2-6y | 60-200 | 40-250 | 40-120 | 0-3 | 2-8 |
| Senior/staff/principal | 20-120 | 150-500 | 20-80 | 0-4 | 1-5 |
| Eng manager | 0-30 | 20-150 | 5-40 (mostly reporter) | 0-2 | 3-10 (leadership) |
| QA/SDET | 30-120 | 20-80 | 80-200 (bugs) | 0-2 (ISTQB) | 2-6 |
| Support L1/L2 | 0 | 0 | ServiceNow 600-2,000 | 0-2 (ITIL) | 3-8 |
| Sales/CS | 0 | 0 | Salesforce 20-80 opps or 15-40 accounts | 0-2 | 2-6 |
| HR/Finance | 0 | 0 | few | 0-2 | 3-10 |

## 6. Roster

Batch → generator → personas. Traps reference the fault catalog when available; S1.1 rows in brackets.

### Batch A - Engineering core (Claude Sonnet)
| PID | Persona | Planted faults |
|---|---|---|
| P001 | Priya Sharma, Senior Data Engineer, Bengaluru, 6y total, 4y at Kestrel. Python, PySpark, Airflow, AWS. Verified AWS Certified Developer. Tara Python 2026. | Control positive. CV v1 (2022) + v2 (2026) same lineage [duplicate counting] |
| P002 | Priya Sharma, HR Business Partner, Hyderabad. Workday HCM, talent processes. Email `priya.sharma2@`. LMS "Python for Everybody" completed, never used | Same-name collision [wrong person]; course-only Python [not held] |
| P003 | Arjun Nair, Support Engineer L2, Pune. ServiceNow heavy. CV lists Kubernetes; 2019 intro course | Listed-only + stale course [not held] |
| P004 | Vikram Reddy, Engineering Manager, Bengaluru. Java/Spring expert 2014-2021, no code since 2022; design docs, hiring | Decay of Java [decay]; leadership real; old PRs high volume |
| P005 | Sneha Iyer, SDE-2 backend, `recon-engine` + `ledger-api` in Go | "Go" ambiguity [wrong mapping]; Go genuinely L3 |
| P006 | Rohan Mehta, SDE-1, 14 months, bootcamp grad, tier-3 college | LLM-polished keyword-stuffed CV with 25+ skills [not held, level off via CV length] |

### Batch B - Data, ML, platform (Codex gpt-6.1-sol)
| PID | Persona | Planted faults |
|---|---|---|
| P007 | Ananya Krishnan, ML Engineer, `ml-forecasting`; LLM app work 2025-26; Confluence design docs | GCP ML Engineer cert expired 2024 [contradiction/decay]; authored docs strong |
| P008 | Mohammed Faizal, SRE, `infra-live`, `platform-k8s`; CKA verified; on-call | Merges dependabot/renovate/release-bot PRs → inflated PR counts [not held / level off via volume] |
| P009 | Kavya Rao, Data Analyst → Analytics Engineer (2025); dbt, SQL, Snowflake | "Spark" in CV = Spark AR college project [wrong mapping] |
| P010 | Siddharth Joshi, contractor (`KCC-`), Java/Spring senior, works in client-dedicated private repos outside Kestrel GitHub | Real skill, thin visible evidence [should hold, not "No"]; contractor ID |
| P011 | Deepa Menon, Data Engineer, returned 2026-02 after 3-year career break | Underclaims (self 2, true 3) [flattery inverse]; recency boundary |

### Batch C - QA, frontend, mobile (Claude Sonnet)
| PID | Persona | Planted faults |
|---|---|---|
| P012 | Rahul Kumar, SDET, Pune. Selenium Java 2019-2024, Playwright TS since 2025 | Selenium decaying vs Playwright rising [decay, level off] |
| P013 | Rahul Kumar, Frontend Engineer, React/TS, Bengaluru | Same name; HCM email swapped with P012 in one record [wrong person → join neither] |
| P014 | Fatima Sheikh, Mobile engineer, React Native | Pair programming; many PRs co-authored; squash-merged by lead [ownership] |
| P015 | Aditya Verma, Cloud Engineer, 2.5y | Cert collector: 7-9 certs in 2y, several PDF-only unverifiable; thin work [not held, level off] |
| P016 | Meera Pillai, Performance Test Engineer, JMeter/k6 | CV claims "Java expert"; Tara Java 2026 score 38% [contradiction] |

### Batch D - Leadership, architecture, security, EU (Codex gpt-6-astra)
| PID | Persona | Planted faults |
|---|---|---|
| P017 | Karthik Subramanian, Principal Architect; few PRs, 400+ reviews/yr, ADRs | Level from reviews/docs, not PR volume [level off if counted by PRs] |
| P018 | Nikhil Bansal, ex-Ledgerly "Tech Lead" at 2.5y, `LGR-` legacy + `KC-` ID | Title inflation [level off]; duplicate HCM IDs [wrong person risk] |
| P019 | Lakshmi Narayanan ("N. Lakshmi" in some systems), Security Engineer | South Indian name order variance across systems [identity]; SEC tickets |
| P020 | Anjali Gupta → Anjali Kapoor (name + email change 2025-07), Product Manager | Identity continuity [wrong person / split]; PM evidence as Jira reporter + PRDs |
| P021 | Tom Fischer, SRE, Berlin (EU) | No EU opt-in → `do_not_message` [consent]; otherwise strong evidence |

### Batch E - GTM, support, HR (Claude Sonnet; sales/CS family uses K3 scale)
| PID | Persona | Planted faults |
|---|---|---|
| P022 | Arvind Shetty, Account Executive, Mumbai-based remote | Deal credit split with overlay SE [ownership]; K3 exact-level rule |
| P023 | Pooja Desai, Customer Success Manager | Onboarding skill strong; Salesforce activity logged by assistant [attribution] |
| P024 | Ramesh Yadav, L1 Support, 1,500+ ServiceNow tickets/yr | Auto-routed, copy-paste resolutions: volume ≠ depth [level off] |
| P025 | Neha Kulkarni, Talent Acquisition Specialist | Thin evidence, mostly HCM + LMS [should hold]; non-tech skills |
| P026 | Sunita Rao, HR Ops Lead, 15y, SAP SuccessFactors → Workday | "SAP" ambiguity (HCM vs FI) [wrong mapping]; SAP decaying since 2023 migration |
| P027 | Jason Lee, Sales Engineer, Austin (US) | Overlay SE credit; API testing demos; US-based |

### Batch F - Adversarial and edge cases (Codex gpt-6.1-terra)
| PID | Persona | Planted faults |
|---|---|---|
| P028 | Harsh Agarwal, Backend SDE-2 | Overclaimer (self 4 everywhere), LLM-written CV, Tara shows 2; `yes_to_everything: true` |
| P029 | Divya Krishnamurthy, UX Researcher / Product Designer | Evidence mostly authored docs; Figma not in any source [sparse, hold] |
| P030 | Imran Qureshi, Data Engineer, boomerang (left 2022, rehired 2024), two employee IDs | Duplicate HCM records [wrong person]; skill gap across break [decay] |
| P031 | Shreya Ghosh, Data intern (6 months) with strong pre-joining OSS Python | Title ≠ level (true Python 3 as intern) [level off if title used] |
| P032 | Manoj Tiwari, FP&A Analyst | Excel modelling (generic/exclude), basic SQL; almost nothing sendable [coverage] |

Counterfactual twins (name / gender / university swaps for the fairness test) are generated later by script, not by hand.

## 7. Done when (per batch)

- All files for each PID exist, JSON valid (`python3 -I -m json.tool`).
- Every trap in the roster planted and listed in `truth/<PID>.json`.
- No truth wording or truth levels leak into `bundles/`.
- A batch note at `data/notes/batch_<X>.md`: what was planted where, grounding files used, anything you had to guess.

## 8. v2 decisions (user, 2026-11-05) - these override earlier sections

- **D-U1 Truth split.** Every skill row carries two layers: hidden ability (`true_level`) and the observable oracle (`oracle`). Precision on sends is scored against `true_level` + `would_accept_levels`; holds and non-sends are scored against `oracle`.
- **D-U2 Levels follow the level lines literally, applied work first.** A level is the level line the evidence shows. Applied work (merged changes, resolved incidents, shipped designs, closed deals) sets the level. A scored test can support the floor (STEP-4.3) but on its own shows at most level 1. Applied work with guidance is level 2, never level 1. Do not use level 1 for real applied work.
- **D-U3 Identity.** A stable key wins: employee ID, a `linked_employee_id` on a system account, a rehire or name-change record in HCM. Name alone never merges. Email alone merges only when no stable key conflicts. No stable key and ambiguous match: join neither. Name or email changes with a persistent ID are one person (history stays with them).
- **D-U4 Invisible-but-real skills.** When the person has the skill but the bundle cannot show it, the oracle is `hold`. A hold is correct, counted as coverage, never as a precision error. Record which missing source would have shown it (`missing_source`).
- **D-U6 Real pilot set.** Real people live in `data/real/` (gitignored), bundles `R0xx`, no truth files. Their ground truth is their own Yes/No on engine output, collected later. Realism patterns from them are in `docs/research/10-real-cv-observations.md` (RO-01..RO-16).

### 8.1 truth v2 schema (`truth/<PID>.json`)
```json
{"pid": "P033", "schema": "truth-v2", "summary": "...", "archetype": "...", "batch": "G", "generator": "...",
 "skills": [{"skill_id": "python", "has_skill": true, "true_level": 3,
   "self_perceived_level": 3, "would_accept_levels": [2, 3, 4],
   "oracle": {"action": "send|hold|not_extract|do_not_message", "level": 3, "accept_levels": [2, 3, 4],
              "basis": "which bundle evidence supports this action, by source_id", "missing_source": null},
   "last_used": "2026-10", "evidence_refs": ["gh_x:#1832"], "why": "..."}],
 "decoys": [...], "traps": [... as before, expected_engine_behavior must equal the oracle action for that skill ...],
 "unmatched_skills": ["AutoCAD", "SolidWorks"],
 "answer_behavior": {...}, "messaging_allowed": true}
```
- `oracle.action = send` requires `oracle.level`; `accept_levels` = level ±1 on K4, exact on K3, intersected with what the person would accept.
- `not_extract` = the bundle mentions it but it must not become a skill (decoy, wrong mapping, excluded generic).
- `unmatched_skills` = real skills the person has that the taxonomy does not cover (expected output: route to review, never force-map).
- Twins inherit the source truth unchanged.
