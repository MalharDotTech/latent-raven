# Batch A notes (P001-P006), generator claude-sonnet-5-5

Validator: `python3 -I scripts/validate_personas.py P001..P006` -> 0 errors, 0 warns.

## What is planted where
| PID | Persona | Sources | Planted |
|---|---|---|---|
| P001 | Priya Sharma, Sr Data Engineer, Blr | hcm, cv_v1 (2022), cv_v2 (2026), github, jira, certs (DVA-C02 verified), lms, tara (Python, SQL), 1 doc | Control positive. cv v1/v2 same lineage_key, Infosys block verbatim in both. Extras: 3 dependabot PRs with merged_by self (F10), "Fix bug"/General Jira (F16), name collision with P002 (F18), Kubernetes (basic) listed only (F01) |
| P002 | Priya Sharma, HRBP, Hyd | hcm (email priya.sharma2@), cv, lms, 1 doc (PEOPLE) | F18 name collision; Python course + self level 2, never used (F26); R&R CV with declaration (F06); SuccessFactors vs SAP mapping risk (F25) |
| P003 | Arjun Nair, Support L2, Pune | hcm, cv, servicenow (54 sampled records + monthly), jira (reporter only), certs (ITIL 4 expired 2025-03 per grounding validity; CSA verified), lms, tara Linux, 1 doc | Kubernetes in CV + 2019 Udemy course + HCM self level 2 (F01, F28); runbook "rollout restart" via ops console (F25); templated resolution notes (F17); reassigned tickets (F14) |
| P004 | Vikram Reddy, EM, Blr | hcm, cv (2025), github 2016-2026, jira, certs (PSM I), lms (leadership), 3 docs | Java/Spring decay since mid-2022 with huge old PR volume (F28); self declared 4; leadership real (F19); ARCH page created by him but written by engineers (F34); reporter/epic Jira rows with other assignees (F15) |
| P005 | Sneha Iyer, SDE-2 Go, Blr | hcm, cv (2026-05), github, jira, lms, tara Go 71%, 1 doc | Go ambiguity: go-live, go/no-go, go-to-market in CV, Jira (General component) and a PR title (F25); real Go evidence strong; co-authored helm PR (F13); bot PR (F10); "Fix bug" (F16) |
| P006 | Rohan Mehta, SDE-1, 14 mo | hcm, cv (3 pages, 27 skills), github, jira, certs (self reported, unverifiable), lms, tara JS 58% | LLM-style CV (F04), keyword stuffing (F05), CV length vs level (F06), AI overclaim (F08), unverifiable cert (F27), 44-minute Docker/K8s completion (F26), bot PR (F10), revert + redo PR |

Lineage extras with no catalog fault_id are labelled `none:*` in truth (`none:cv_lineage_duplicate`, `none:go_true_positive`).

## Hard cases (truth honest)
- P004: Java true 2 though 5 years of heavy history; engines using PR counts will give 3-4.
- P005: Go 3 genuine but name ambiguity may cause over-suppression; Kubernetes 1 thin and co-authored.
- P003: servicenow 3 rests on one RITM and CSA; most rows are templated.
- P001: python 3 not 4 (no adopted Python teaching, only Airflow standards).

## Grounding used
certifications.json: DVA-C02, ITIL 4 Foundation, ServiceNow CSA, PSM I, CLF-C02 (P006 self reported). courses.json: ETL in Python and SQL, Python Essential Training, SQL Essential Training, Agile Foundations, Docker Fundamentals for Developers (path), Git: Branches, Merges, and Remotes, Docker and Kubernetes for beginners. Employers from grounding: Infosys, Razorpay. job_ladders: P001/P005 use "Senior Data Engineer", SDE-I/II style (no DE/SDE ladder in corpus, so these titles are guesses).

## Guessed / from model knowledge
- Roster says P002 completed "Python for Everybody"; it is not in courses.json, so the LMS row uses grounded "Python Essential Training" (LinkedIn Learning) instead.
- Employers from model knowledge: Wipro. Institutions from model knowledge: RV College of Engineering, PES University, NIT Warangal, Pune Institute of Computer Technology, Institute of Public Enterprise (Hyderabad), Osmania University, Masai School, Jaihind College of Engineering (Kuran, SPPU; least certain).
- P006 pre-join internship employer left unnamed ("early-stage fintech startup").
- OSS: apache/airflow docs fix (P001) and gocarina/gocsv fix (P005) are plausible not verified PRs.
- Grounding certs file says ITIL 4 valid 3 years, so P003 ITIL shows expired 2025-03 (real ITIL 4 does not expire).
- PR numbers/Jira keys are synthetic and unique within the batch (per-persona residue digit); PR title ticket keys were relinked to Jira keys where an issue exists within 40 days. Many P004 old PRs reference tickets absent from his sampled Jira list.
- Servicenow monthly_activity field names are my own (spec gives none).
