# Batch F

As of 2026-10-31. All people, internal records and contributions are synthetic.

- P028: CV promotional profile and keyword inventory (F04/F05), self-ratings versus Tara (F29), yes-to-everything response behaviour (F32), three-minute LMS completion (F26), reassigned billing ticket (F14).
- P029: research authored pages are the main work artifacts; private design-tool use is unavailable in export (F09); contributors are explicitly distinguished (F34). Roadmap ownership is not established.
- P030: archived and current HR rows link two IDs (F23); former Spark work precedes a nontechnical break (F28); unsupported Kafka mention (F01); generic tickets (F16).
- P031: internship title understates independently demonstrated pre-joining Python work (F20); unsupported Docker familiarity (F01); generic issue labels (F16). Public project/PR references are fictional synthetic records, not assertions about actual Apache PRs.
- P032: CV convention and ordinary Office mention (F06); detailed authored workbook explains real modelling, which is excluded from this batch's generic-office send scope despite taxonomy's narrower non-generic Excel modelling entry; avoid conflating it with data modelling. Old orientation is not current delivery evidence (F28).

Grounding consulted: taxonomy; certifications, courses, job ladders, names and universities, technology co-occurrence, PR titles, issue styles, and CV conventions; fault catalog. Internal course names are explicitly marked internal.

From model knowledge: VIT Vellore and Freshworks. Guesses: HR IDs, dates, reporting lines, exact study results, assessment scores, work activity, private skill details and all external contribution identifiers are invented for these synthetic employees. The roster's “Excel modelling (generic/exclude)” conflicts with the taxonomy's explicit non-generic Excel-modelling definition: the truth records actual modelling skill while the batch-specific expected action holds it for the requested coverage scenario. F09 is used for missing private design artifacts by analogy with private-repository invisibility; F20 is used for title-based miscalibration of an intern although the catalogue's canonical example is acquisition title inflation.

Validator note: the P028 CV slop warning is intentional: polished LLM-style copy is an explicit roster fault.

## Repair pass (quality rewrite, P028-P032)

Why: first-pass bundles were mechanical (regular PR date steps, "(8)" title suffixes, near-identical file mixes, thin docs). All five bundles rewritten with scripted-but-seeded generation: PR dates cluster by sprint cadence and month (Dec/Oct-Nov dips, release-month peaks, leave gaps), titles are hand-written and varied, file-extension mixes and sizes vary, PR numbers rise with date per repo, monthly_activity covers full tenure and is at least the listed PR count per month. No true_level values changed.

- P028: github 40 PRs + 22 reviews (mostly shallow approvals), jira 29 issues (BILL-1491 keeps the reassigned first ticket), full monthly series 2022-06..2026-10; CV kept LLM-style but longer (core competencies, expert tags, vague achievements); HCM allocations, 11 self-declared skills at 4, education; LMS expanded to 10 rows (3-minute Kubernetes orientation kept); added a low-scoring Tara Kubernetes fundamentals result (consistent with kubernetes not held). Truth refs re-pointed to new PR/ticket ids.
- P029: 2 docs expanded and 4 new authored docs (recruitment playbook, invoice-template interviews, Q1 2026 readout, release 26.3 design QA) with named collaborators and explicit who-did-what; roadmap shown as PM-owned; no design-tool name appears in any source. New lms.json (9 rows), richer CV (Roles and Responsibilities, methods, tools without a prototyping tool), HCM allocations/skills/education. Truth refs added for docs.
- P030: 38 PRs (pre-break PySpark era, post-break Python/Airflow/SQL), 28 Jira issues renumbered to a consistent DATA sequence, monthly series with zero rows for the 2022-09..2024-04 gap, 17 reviews, github legacy_employee_ids field, archive HCM enriched (older self-declared PySpark 3), current HCM self-declared PySpark 2, LMS 10 rows, CV with career-break statement and Kafka listed without work. Truth refs updated.
- P031: github.json now has a real public_profile (4 personal repos incl. data-checks, 13 OSS contributions to apache/airflow, tenacity, pandas, pytest; plus review/triage counts) with a synthetic_note; 30 internal PRs and 22 Jira issues over 6 months, monthly series, 10 reviews; CV, HCM project/education, LMS 6 rows. Docker still only on CV. Public identifiers are plausible synthetic placeholders, not assertions about real PRs. Truth sql refs kept to generic tickets.
- P032: finance-forecast expanded, 3 new authored docs (headcount inputs, cost-centre mapping change log, variance commentary guide), fuller CV (Roles and Responsibilities, declaration, Office list), HCM allocations/skills/education, LMS 9 rows. Docs avoid "data model" wording. Truth refs added.

From model knowledge (added): Manipal Institute of Technology, College of Engineering Pune, IDC School of Design IIT Bombay, Christ University, Symbiosis Institute of Business Management, Wipro; OSS repos apache/airflow, jd/tenacity, pandas-dev/pandas, pytest-dev/pytest. All fictitious people (e.g. Rakesh Pillai, Meenal Joshi, Lavanya Pillai).
