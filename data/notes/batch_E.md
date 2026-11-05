# Batch E notes (P022-P027, GTM / support / HR) - generator claude-sonnet-5-5

Sales/CS skills use the K3 scale (exact-level rule). All dates within the as-of 2026-10-31. Open Salesforce opps carry past-due close dates (slipped) on purpose, to avoid future dates.

| PID | Role | Sources | Planted |
|---|---|---|---|
| P022 Arvind Shetty | AE, Mumbai remote, KC-11874 | hcm, cv, salesforce, lms | F33 split credit with overlay SE (70-80% owner, SE notes inside his opps; 2 deals shared with P027 by identical opp_id); F29 self 3 vs true 2 on K3; F02 CV start May 2022 vs HCM Aug 2022; F19 HCM title stale vs CRM user title |
| P023 Pooja Desai | CSM, Pune, KC-10931 | hcm, cv, salesforce, lms, 2 docs | F14 ~60% of activities created by CS ops coordinator ("per Pooja"); F34 playbook has 4 contributors; F25 Zoho CRM beside Salesforce on CV; onboarding true K3 level 3 |
| P024 Ramesh Yadav | L1 Support, Pune, KC-11602 | hcm, cv, servicenow (96 sampled + monthly counts ~1,600/yr), certs (ITIL 4), lms | F17 auto-routed copy-paste resolutions; F26 6 and 4 minute SQL/Python course ticks; F01 Linux in CV/HCM only; F16 vague customer-pasted summaries |
| P025 Neha Kulkarni | TA Specialist, Pune, KC-12248 | hcm, cv, lms only | F09-style thin evidence (should hold, not No); F19 stale HR Executive title; F06 Indian CV noise; F25 Workday Recruiting vs HCM |
| P026 Sunita Rao | HR Ops Lead, Bengaluru, KC-10077 | hcm, cv, servicenow (RITMs she raised), lms, 2 docs | F25 SAP HCM/SuccessFactors vs FI display access ambiguity; F28 SAP decay (last use Dec 2023); F19 title path; F29 stale self-ratings |
| P027 Jason Lee | Sr Sales Engineer, Austin, KC-12011 | hcm, cv, salesforce, certs (AWS CCP), lms, 2 docs | F33 overlay credit 15-30%; F35 demo-grade API testing vs QA practice; F25 AWS foundational cert; US-based (no EU opt-in needed) |

## Format guesses
- Salesforce schema extended: `other_roles_on_deal`, `record_type`, `technical_win`, `created_by` / `assigned_to` on activities, `monthly_activity`.
- ServiceNow: `assignment_method` (auto_rule/manual), `escalated_to`, `monthly_activity` counts; P024 sample is 96 records out of ~4,900 (spec lists samples, not full exports). P026 file is RITMs raised by the user (`requested_by_self`).
- `fault_id` F29 is used for self-rating inflation / K3 exact-level checks; "K3 exact-level" has no catalog row.

## Taxonomy judgement calls
- `sap` is "SAP ERP"; P026's SuccessFactors Employee Central work is treated as the HCM module scope, level 2 after decay, never FI.
- P025 truth is level 3 on talent_acquisition though little evidence exists; this is intentionally HARD.

## Grounding
- Certs: ITIL 4 Foundation (P024), AWS Certified Cloud Practitioner (P027) from certifications.json.
- Courses from courses.json: SQL Essential Training, Python Essential Training; all other courses are `internal:`.
- From model knowledge: Freshworks, Wipro BPS, Tech Mahindra BPO, Zoho, Infosys, TeamLease Services, Bajaj Auto, Rackspace Technology; University of Mumbai, NMIMS, Savitribai Phule Pune University, Fergusson College, Symbiosis Institute of Business Management, Bangalore University, Christ University, University of Texas at Austin.
- No job-ladder grounding exists for sales, support or HR; titles are generic.
