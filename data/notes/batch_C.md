# Batch C - QA, frontend, mobile, cloud, performance (P012-P016)

Generator: claude-sonnet-5-5. Scripts were run once; all files under data/bundles/P012..P016 and data/truth/P012..P016.

## What is planted where

| PID | Persona | Sources | Planted faults |
|---|---|---|---|
| P012 | Rahul Kumar, SDET II, Pune (KC-10412) | hcm, cv, github, jira, certs, lms | F28 Selenium decay vs Playwright rise (PRs 2019-24 Java, 2025+ TS, last legacy touch 2025-09); F29 HCM self-declared Selenium 4 (2022); F18 name twin + e-mail swap; F16 vague tickets ("test fix"); F25 ISTQB CTFL on file |
| P013 | Rahul Kumar, Sr Software Engineer frontend, Bengaluru (KC-11284) | hcm, cv, github, jira, lms | F18 swapped HCM mailbox (join_neither); F05 CV padding (Angular, Vue, Next.js, MongoDB, Figma); F06 Indian template CV; F29 JS self-declared 4; F16 "UI broken" tickets |
| P014 | Fatima Sheikh, Sr Software Engineer mobile, Hyderabad (KC-10896) | hcm, cv, github, jira, lms, 1 doc | F11 ~90% of her PRs squash-merged by lead; F13 pair co-authors both directions, plus `commit_trailers_not_linked_to_account` (personal gmail); F14 multi-assignee tickets; F10 two renovate PRs she merged; F25 "React Native" vs taxonomy `react` |
| P015 | Aditya Verma, Cloud Engineer, Bengaluru (KC-11902) | hcm, cv, github, jira, certs (9), lms (8), assessments | F27 6 of 9 certs PDF-only, one fails lookup; F01 CV "Advanced" K8s/Terraform; F24 AZ-104 lapsed 2026-01 but on CV; F26 long Udemy courses finished in 35-130 min; F29 self-declared 3 on five cloud skills; F25 GCP ACE PDF only |
| P016 | Meera Pillai, Sr Performance Test Engineer, Bengaluru (KC-11517) | hcm, cv, github, jira, certs, lms, assessments, 2 docs | F01 CV "Java (Expert)" vs Tara Java 38%; F29 HCM self-declared Java 4; F13 sole Java PR co-authored by a dev; F25 ISTQB; F16 "retest" tickets |

P012/P013 email swap: Workday records for both show the other's mailbox from 2024-03 (histories are mirror images). GitHub and Jira exports carry an extra `account_email` field with the original mailbox, and `linked_employee_id` is correct, so an e-mail join and an ID join disagree. Logins are `rkumar_kestrel` / `rkumar2_kestrel`.

## Extra non-schema fields (additive)
- github.json / jira.json for P012, P013: `account_email`.
- P014 github.json: `commit_trailers_not_linked_to_account` list (trailers with unlinked personal e-mail).

## Hard-for-engine truths
- P012 selenium true 2 while CV, HCM and 5 years of PRs say 3-4; P012 playwright 3 and typescript 2 (test code only).
- P016 performance_testing 3 (borderline 4); java 1 despite expert claims.
- P014 typescript 2 even though she has volume; ownership split across lead and pair.
- P015 mostly levels 1-2 with 9 certs; azure 1 and gcp 0.

## Grounding used
certifications.json: ISTQB CTFL v4.0 (P012, P016); AWS CLF-C02, SAA-C03, DVA-C02; Azure AZ-900, AZ-104; Terraform Associate; KCNA; CKAD; Google Associate Cloud Engineer (P015). courses.json: Git Essential Training, SQL Essential Training, Agile Foundations, Git: Branches, Merges, and Remotes, Learning Git and GitHub, plus the Udemy/Pluralsight titles for P015. Internal courses prefixed `internal:`. PR/ticket style imitated from pr_title_samples/issue_style_samples (ticket-key prefixes, terse fixes, "chore: bump").

## From model knowledge (not in grounding)
Universities: VIT Vellore (P012), PES University (P013), Osmania University (P014), Manipal Institute of Technology (P015), Anna University (P016). Employers: Infosys (P012, P016), Zoho (P013), TCS (P014), Freshworks (P016). Meta React Native Specialization (Coursera, 2020) on P014's CV as a CV-only claim, not in LMS.

## Guesses / judgement calls
- Employee IDs picked in KC-10xxx..11xxx; manager IDs are placeholders (KC-10230, KC-10980, KC-10544, KC-10410, KC-10312).
- Truth level for P012 selenium (2) and P016 performance (3 vs 4) are judgement calls; would_accept widened to reflect.
- `lms.json`/`assessments.json` use top-level keys `completions`/`assessments`.
- P015 PR volume (~35/yr) is below the table range on purpose (thin work).
- P015 CV says "Cloud Engineer" from Apr 2024 while HCM title was Associate until 2025-12 (mild title inflation, not listed as a trap).
- P014 CV received 2024-02 (promotion packet) rather than at hire so it can reference Kestrel work.
