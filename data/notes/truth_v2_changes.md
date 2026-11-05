# Truth v2 changes (P001-P032)

Scope: the 32 original personas. Twins (P0xx-T*) and P033+ are untouched. v1 backup is in `data/truth_v1/`. Every file in `data/truth/P001.json`..`P032.json` now has `"schema": "truth-v2"` and an `oracle` on every skill row and every decoy. Each oracle cites bundle `source_id`s from that persona's `manifest.json` plus a short description of the evidence (PR and Jira numbers are being renumbered by another job, so I did not cite them).

How I decided each oracle: read the bundle, apply the taxonomy level line literally (applied work first, guided applied work is level 2, a test alone is at most level 1), then the floor/ceiling rule (floor = level backed by 2+ independent groups, a measured result under 2 years, or work in 3+ months; ceiling minus floor 0/1 -> floor, 2 -> floor+1, 3+ -> hold). Listed-only or training-only skills that map correctly are `hold`. `not_extract` is kept for wrong mappings, generic or excluded items, disclaimed skills and evidence that belongs to someone else. Invisible-but-real skills are `hold` with `missing_source` (D-U4).

## 1. Counts

- Skill rows: 268 (267 v1 rows plus 1 new row). Oracle actions: send 145, hold 93, not_extract 19, do_not_message 11 (all of P021).
- Decoys: 66, each with an oracle: do_not_message 1, hold 30, not_extract 35.
- Hidden `true_level` changes: 15 (14 corrected rows plus the new P030 Snowflake row). Most are level-1 misuse fixed to level 2 for real guided work (D-U2).
- `would_accept_levels` edits: 13 rows (narrow sets like [3] on a K4 skill widened to the honest ±1 band, broken sets like [1,1,2] fixed, and rows whose hidden level moved).
- `assessed_level` set to null where no assessment file exists in the bundle (P007, P008, P009, P010, P029, P030, P031, P032, and the non-Python rows of P011).
- Trap expectations changed: 52 of 133 traps. Every trap that names a skill now equals that skill's oracle (checked by script); `join_neither` is no longer used anywhere because every identity case in P001-P032 has a stable key.
- Audit disagreements (docs 08 and 09) explicitly resolved on skill rows: 45, plus 9 trap-level ones. Skill rows: level changed 12; resolved as hold (or do_not_message) 23; resolved as send at the floor level 8; not adopted (kept v1 level) 2. P010 (7 rows, all hold per D-U4) and P009 Python (hold, not No) also follow the audits but are not tagged in the table.

## 2. Every skill row vs v1

`v1 -> v2` is the hidden `true_level` (`-` = not held). Oracle is the action and level an engine should produce from the bundle alone.

| PID | Skill | v1 -> v2 | Oracle | Reason |
|---|---|---|---|---|
| P001 | python | 3 -> 3 | send 3 | Unchanged level; clean multi-group send. |
| P001 | pyspark | 3 -> 3 | send 3 | Unchanged; F10 bot PRs are about boto3/airflow-provider, not PySpark, so they do not move this skill. |
| P001 | spark | 3 -> 3 | send 3 | Unchanged. |
| P001 | airflow | 4 -> 4 | send 4 | Unchanged level; v1 trap said hold, which contradicted the evidence. Oracle is send 4. |
| P001 | aws | 3 -> 3 | send 3 | Unchanged. |
| P001 | sql | 3 -> 3 | send 3 | Unchanged. |
| P001 | data_modeling | 2 -> 2 | hold | Hidden 2 kept; bundle cannot pin it, so hold. |
| P001 | code_review | 3 -> 3 | send 3 | Unchanged. |
| P001 | technical_writing | 3 -> 3 | send 2 | Hidden 3 kept; audit 3->2/H resolved as send at 2 (Yes for her). would_accept widened [3] -> [2,3,4]. |
| P001 | docker | 2 -> 2 | hold | Hidden 2 kept; CV-only, so hold. |
| P001 | terraform | 1 -> 2 | send 2 | 1->2: merged, reviewed Terraform changes are the level 2 line, not level 1. |
| P002 | workday | 3 -> 3 | send 2 | Hidden 3 kept; oracle sends floor 2 (2 groups), not 3: no audited transactions in bundle. |
| P002 | hr_operations | 3 -> 3 | hold | Hidden 3 kept; no case records, so hold. |
| P002 | stakeholder_management | 3 -> 3 | hold | Soft skill, self + org only; hold. would_accept widened to K4 band. |
| P002 | talent_acquisition | 2 -> 2 | hold | Hidden 2 kept; org + training only, hold. |
| P002 | technical_writing | 2 -> 2 | hold | Hidden 2 kept; one artifact, hold. |
| P002 | python | 0 -> 0 | hold | Not held; course + self only -> hold (not sent). P001's Python must not be joined here. |
| P003 | servicenow | 3 -> 3 | send 3 | Unchanged; templated resolution notes do not add depth but the RITM changes do. |
| P003 | incident_management | 3 -> 3 | send 2 | Hidden 3 kept; bundle shows comms/escalation, not coordination of diagnosis, so oracle level 2 (still Yes). would_accept widened [3] -> [2,3,4]. |
| P003 | linux | 2 -> 2 | hold | Hidden 2 kept; test + self only, hold. |
| P003 | sql | 2 -> 2 | hold | Hidden 2 kept; audit 2->H. |
| P003 | technical_writing | 2 -> 2 | send 2 | Unchanged level; two groups at 2. |
| P003 | stakeholder_management | 2 -> 2 | hold | Hidden 2 kept; no direct evidence, hold. |
| P003 | kubernetes | 0 -> 0 | hold | Not held; listed-only, hold. |
| P003 | docker | 0 -> 0 | hold | Not held; listed-only, hold. |
| P004 | java | 2 -> 2 | hold | Hidden 2 kept; decayed beyond window and self-claims 2+ levels off, so hold (audit 09: hold, not send 2 to a Director-track EM). |
| P004 | spring_boot | 2 -> 2 | hold | Hidden 2 kept; decay, hold. |
| P004 | technical_leadership | 4 -> 4 | send 3 | Hidden 4 kept; bundle pins 3 (cross-team adoption only self-stated). 3 is still a Yes. |
| P004 | system_design | 3 -> 3 | send 3 | Unchanged level; v1 trap said hold, but ADR-014 + project allocation alone support 3 without the co-authored page. |
| P004 | stakeholder_management | 3 -> 3 | hold | Hidden 3 kept; self + indirect only, hold. |
| P004 | agile_delivery | 3 -> 3 | send 3 | Unchanged level; would_accept widened [3] -> [2,3,4]. |
| P004 | code_review | 2 -> 2 | send 2 | Unchanged level 2; current reviews pin 2. |
| P004 | technical_writing | 3 -> 3 | hold | Hidden 3 kept; audit 3->2/H resolved as hold. |
| P005 | go | 3 -> 3 | send 3 | Unchanged; genuine Go must not be over-corrected by the go-live decoys. |
| P005 | sql | 3 -> 3 | send 2 | Hidden 3 kept; bundle pins 2 (no SQL tuning evidence). Still a Yes. |
| P005 | kafka | 2 -> 2 | send 2 | Unchanged. |
| P005 | docker | 2 -> 2 | send 2 | Unchanged; thin but two groups. |
| P005 | observability | 2 -> 3 | send 3 | 2->3: production profiling and leak repairs are the level 3 line (Codex audit). |
| P005 | code_review | 2 -> 3 | send 3 | 2->3: substantive defect catches match level 3 line; volume not the criterion. |
| P005 | system_design | 2 -> 2 | send 2 | Hidden 2 kept (audit proposed 3); send 2 is a Yes under either reading. |
| P005 | cicd | 2 -> 2 | send 2 | Unchanged. |
| P005 | technical_writing | 2 -> 2 | hold | Hidden 2 kept; single artifact, hold. |
| P005 | kubernetes | 1 -> 2 | hold | 1->2: guided manifest change is level 2 work, not level 1; oracle hold because the only change is co-authored (F13). |
| P005 | python | 1 -> 2 | hold | 1->2 hidden (scripts are applied work, D-U2 forbids level 1 for it); oracle hold, CV-only. |
| P006 | javascript | 2 -> 2 | send 2 | Unchanged. |
| P006 | typescript | 2 -> 2 | send 2 | Unchanged. |
| P006 | react | 2 -> 2 | send 2 | Unchanged; CV polish must not lift level (F06). |
| P006 | nodejs | 1 -> 2 | hold | 1->2 hidden (bootcamp capstone is guided applied work, not level 1); oracle hold, CV-only. |
| P006 | sql | 1 -> 1 | hold | Hidden 1 kept (bootcamp knowledge); oracle hold. |
| P006 | java | 0 -> 0 | hold | Not held; listed-only, hold. |
| P006 | spring_boot | 0 -> 0 | hold | Not held; hold. |
| P006 | python | 0 -> 0 | hold | Not held; hold. |
| P006 | docker | 0 -> 0 | hold | Not held; hold. |
| P006 | kubernetes | 0 -> 0 | hold | Not held; hold (v1 trap said not_extract; it maps correctly, so hold). |
| P006 | aws | 0 -> 0 | hold | Not held; hold. |
| P006 | terraform | 0 -> 0 | hold | Not held; hold. |
| P006 | kafka | 0 -> 0 | hold | Not held; hold. |
| P006 | machine_learning | 0 -> 0 | hold | Not held; hold. |
| P006 | llm_engineering | 0 -> 0 | hold | Not held; hold. |
| P007 | python | 3 -> 3 | send 3 | Unchanged level. assessed_level removed: no assessment file in bundle. |
| P007 | machine_learning | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file in bundle. |
| P007 | llm_engineering | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file in bundle. |
| P007 | sql | 2 -> 2 | hold | Hidden 2 kept; mention-only, hold. assessed_level removed: no assessment file in bundle. |
| P007 | docker | 3 -> 3 | send 2 | Hidden 3 kept; a single image fix pins 2 (Yes either way). assessed_level removed: no assessment file in bundle. |
| P007 | gcp | 1 -> 1 | hold | Hidden 1 kept (decayed knowledge); hold. |
| P007 | technical_writing | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file in bundle. |
| P007 | code_review | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file in bundle. |
| P007 | system_design | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file in bundle. |
| P007 | terraform | - -> - | not_extract | Not held; co-authored page must not create the skill. |
| P008 | kubernetes | 3 -> 3 | send 3 | Unchanged level. assessed_level 3 removed: no assessment file exists. |
| P008 | terraform | 3 -> 3 | send 3 | Unchanged. assessed_level 3 removed: no assessment file exists. |
| P008 | aws | 3 -> 3 | send 3 | Unchanged. assessed_level 3 removed: no assessment file exists. |
| P008 | linux | 3 -> 3 | send 3 | Unchanged. assessed_level 3 removed: no assessment file exists. |
| P008 | observability | 3 -> 3 | send 3 | Unchanged. assessed_level 3 removed: no assessment file exists. |
| P008 | cicd | 3 -> 3 | send 3 | Unchanged. assessed_level 3 removed: no assessment file exists. |
| P008 | docker | 3 -> 3 | send 2 | Hidden 3 kept; one PR pins 2 (Opus: 3->2). Yes either way. assessed_level 3 removed: no assessment file exists. |
| P008 | incident_management | 3 -> 3 | send 3 | Unchanged; only one incident visible (no ServiceNow export) but timeline + corrective action meet the line. assessed_level 3 removed: no assessment file exists. |
| P008 | code_review | 3 -> 3 | send 3 | Unchanged; Opus suggested 2 because reviews are templated, but the level line (defects caught before merge) is met. assessed_level 3 removed: no assessment file exists. |
| P008 | go | - -> - | not_extract | Not held; must not be extracted. |
| P009 | sql | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P009 | dbt | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P009 | snowflake | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P009 | data_modeling | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P009 | code_review | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P009 | technical_writing | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P009 | spark | - -> - | not_extract | Wrong mapping (Spark AR). |
| P009 | python | - -> - | hold | Not held; training-only -> hold (absence is private info). |
| P010 | java | 4 -> 4 | hold | Hidden 4 kept; invisible-but-real (D-U4), hold. assessed_level removed: private assessor is not a bundle source. |
| P010 | spring_boot | 4 -> 4 | hold | Hidden 4 kept; D-U4 hold. assessed_level removed: private assessor is not a bundle source. |
| P010 | sql | 3 -> 3 | hold | Hidden 3 kept; D-U4 hold. assessed_level removed: private assessor is not a bundle source. |
| P010 | system_design | 3 -> 3 | hold | Hidden 3 kept; D-U4 hold. assessed_level removed: private assessor is not a bundle source. |
| P010 | code_review | 4 -> 4 | hold | Hidden 4 kept; D-U4 hold. assessed_level removed: private assessor is not a bundle source. |
| P010 | docker | 2 -> 2 | hold | Hidden 2 kept; D-U4 hold. assessed_level removed: private assessor is not a bundle source. |
| P010 | api_testing | 3 -> 3 | hold | Hidden 3 kept; D-U4 hold. assessed_level removed: private assessor is not a bundle source. |
| P010 | kafka | - -> - | not_extract | Not held; attribution trap. |
| P011 | python | 3 -> 3 | send 3 | Unchanged; underclaim trap (F29). |
| P011 | sql | 3 -> 3 | send 2 | Hidden 3 kept; one recent SQL change pins 2. Still a Yes. assessed_level removed: only a Python assessment exists. |
| P011 | pyspark | 3 -> 3 | send 3 | Unchanged. assessed_level removed: only a Python assessment exists. |
| P011 | airflow | 3 -> 3 | send 3 | Unchanged. assessed_level removed: only a Python assessment exists. |
| P011 | aws | 2 -> 2 | send 2 | Unchanged. assessed_level removed: only a Python assessment exists. |
| P011 | code_review | 3 -> 3 | send 3 | Unchanged. assessed_level removed: only a Python assessment exists. |
| P011 | data_modeling | 2 -> 2 | hold | Hidden 2 kept; indirect only, hold. assessed_level removed: only a Python assessment exists. |
| P011 | azure | - -> - | hold | Not held; hold. |
| P012 | selenium | 2 -> 3 | send 3 | 2->3: last independent Selenium fixes are 13 months old, inside the 2y window; elapsed time alone does not show lost independence (Codex). |
| P012 | playwright | 3 -> 3 | send 3 | Unchanged. |
| P012 | java | 2 -> 2 | send 2 | Unchanged. |
| P012 | typescript | 2 -> 2 | send 2 | Hidden 2 kept (Codex questioned the test-code cap); send 2 is a Yes either way. |
| P012 | api_testing | 3 -> 3 | send 3 | Unchanged; would_accept widened [3] -> [2,3,4]. |
| P012 | cicd | 2 -> 2 | send 2 | Unchanged. |
| P012 | code_review | 3 -> 3 | send 3 | Unchanged. |
| P013 | react | 3 -> 3 | send 3 | Unchanged. |
| P013 | typescript | 3 -> 3 | send 3 | Unchanged. |
| P013 | javascript | 3 -> 3 | send 3 | Unchanged; send 3, not the self-declared 4. |
| P013 | nodejs | 2 -> 2 | hold | Hidden 2 kept; one stale PR + CV, hold. |
| P013 | playwright | 2 -> 2 | hold | Hidden 2 kept; single PR, single group, hold. |
| P013 | code_review | 3 -> 3 | send 3 | Unchanged. |
| P013 | cicd | 1 -> 1 | hold | Hidden 1 kept (knowledge only; lint edits are not pipeline work); audit 1->H resolved as hold. |
| P014 | react | 3 -> 3 | send 3 | Unchanged; lead squash-merges and co-author trailers must not move credit. |
| P014 | javascript | 3 -> 3 | send 3 | Unchanged; would_accept widened [3] -> [2,3,4]. |
| P014 | typescript | 2 -> 2 | send 2 | Unchanged. |
| P014 | cicd | 2 -> 2 | send 2 | Unchanged. |
| P014 | code_review | 2 -> 2 | send 2 | Unchanged. |
| P014 | technical_writing | 2 -> 2 | send 2 | Unchanged. |
| P014 | observability | 1 -> 2 | send 2 | 1->2: reviewed breadcrumb instrumentation is applied work (level 2), not level 1. |
| P015 | aws | 2 -> 2 | send 2 | Unchanged; self 3 and 9-cert CV must not lift it (F29). |
| P015 | terraform | 2 -> 2 | send 2 | Unchanged. |
| P015 | kubernetes | 1 -> 2 | hold | 1->2 hidden (guided manifest edits are level 2 work, D-U2). Oracle hold resolves three contradictory v1 traps (hold / send 1 / not_extract). |
| P015 | docker | 1 -> 1 | hold | Hidden 1 kept (course knowledge); training + CV only, hold. |
| P015 | azure | 1 -> 1 | hold | Hidden 1 kept; lapsed + unverifiable, hold. |
| P015 | gcp | 0 -> 0 | hold | Not held; hold (mapping is correct, so not not_extract). |
| P015 | cicd | 2 -> 2 | send 2 | Unchanged. |
| P015 | linux | 2 -> 2 | hold | Hidden 2 kept; audit 2->H. |
| P015 | observability | 1 -> 2 | send 2 | 1->2: merged, reviewed alarm changes are guided application, not level 1. |
| P016 | performance_testing | 3 -> 3 | send 3 | Unchanged. |
| P016 | java | 1 -> 1 | hold | Hidden 1 kept (measured beginner); v1 traps said send 1, but the contract holds when measured and self sit 2+ apart, and she would reject level 1 anyway. |
| P016 | javascript | 2 -> 2 | send 2 | Unchanged. |
| P016 | observability | 2 -> 2 | send 2 | Unchanged. |
| P016 | api_testing | 2 -> 2 | hold | Hidden 2 kept; mapping-uncertain, hold. |
| P016 | cicd | 2 -> 2 | send 2 | Unchanged. |
| P016 | technical_writing | 2 -> 2 | send 2 | Unchanged. |
| P017 | system_design | 4 -> 4 | send 4 | Unchanged; level must come from reviews/docs, not PR volume. |
| P017 | code_review | 4 -> 4 | send 4 | Unchanged. |
| P017 | technical_leadership | 4 -> 4 | send 4 | Unchanged. |
| P017 | java | 4 -> 4 | send 4 | Unchanged. |
| P017 | go | 4 -> 4 | send 3 | Hidden 4 kept; own Go code shows guidance, so oracle states 3 (still a Yes). |
| P017 | sql | 3 -> 3 | send 2 | Hidden 3 kept; one tuning episode pins 2 (Yes either way). |
| P017 | aws | 2 -> 2 | hold | Hidden 2 kept; audit 2->H. |
| P017 | stakeholder_management | 3 -> 3 | hold | Hidden 3 kept; single record, hold. |
| P017 | technical_writing | 3 -> 3 | send 3 | Unchanged. |
| P017 | react | - -> - | hold | Not held now; stale self-mention -> hold. |
| P018 | nodejs | 3 -> 3 | send 3 | Unchanged. |
| P018 | javascript | 3 -> 3 | send 3 | Unchanged. |
| P018 | sql | 2 -> 2 | send 2 | Unchanged. |
| P018 | docker | 2 -> 2 | send 2 | Unchanged. |
| P018 | technical_leadership | 2 -> 2 | send 2 | Unchanged; title inflation must not lift it (F20). |
| P018 | code_review | 2 -> 2 | send 2 | Unchanged. |
| P018 | technical_writing | 2 -> 2 | hold | Hidden 2 kept; single artifact, hold. |
| P018 | aws | - -> - | hold | Not held; CV mention maps correctly so hold; the closure ticket must not be extracted. |
| P018 | kubernetes | - -> - | hold | Not held; hold. |
| P019 | security_fundamentals | 4 -> 4 | send 4 | Unchanged. |
| P019 | python | 3 -> 3 | send 3 | Unchanged. |
| P019 | api_testing | 3 -> 3 | send 3 | Unchanged. |
| P019 | aws | 3 -> 3 | send 3 | Unchanged. |
| P019 | terraform | 2 -> 2 | send 2 | Unchanged. |
| P019 | linux | 3 -> 3 | send 2 | Hidden 3 kept; evidence pins 2 (Opus: one ticket + old CV). Yes either way. |
| P019 | code_review | 3 -> 3 | send 3 | Unchanged. |
| P019 | technical_writing | 3 -> 3 | send 3 | Unchanged. |
| P019 | java | 2 -> 2 | hold | Hidden 2 kept; v1 expected send 2, but co-authored-only evidence is held (same rule as P005 Kubernetes). |
| P019 | incident_management | 3 -> 3 | hold | Hidden 3 kept; D-U4 invisible-but-real -> hold. |
| P019 | kubernetes | - -> - | not_extract | Not held; attribution. |
| P020 | product_discovery | 3 -> 3 | send 3 | Unchanged. |
| P020 | roadmapping | 3 -> 3 | send 3 | Unchanged. |
| P020 | stakeholder_management | 3 -> 3 | send 3 | Unchanged. |
| P020 | agile_delivery | 3 -> 3 | send 3 | Unchanged. |
| P020 | technical_writing | 3 -> 3 | send 3 | Unchanged. |
| P020 | ux_research | 3 -> 3 | send 2 | Hidden 3 kept; bundle pins 2 (designer corrections visible). Audit 3->2/H resolved as send 2. |
| P020 | sql | 2 -> 2 | send 2 | Unchanged. |
| P020 | system_design | - -> - | not_extract | Not held; co-authored page (F34). |
| P020 | go | - -> - | not_extract | Not held; reporter attribution. |
| P020 | figma | - -> - | not_extract | Not held; disclaimed. |
| P021 | kubernetes | 4 -> 4 | do_not_message (if consented: send 4) | Unchanged hidden 4; would send 4 if consent allowed. |
| P021 | terraform | 4 -> 4 | do_not_message (if consented: send 3) | Hidden 4 kept; bundle pins 3 if consent allowed. |
| P021 | observability | 4 -> 4 | do_not_message (if consented: send 4) | Unchanged. |
| P021 | aws | 3 -> 3 | do_not_message (if consented: send 3) | Unchanged. |
| P021 | linux | 3 -> 3 | do_not_message (if consented: send 3) | Unchanged. |
| P021 | python | 3 -> 3 | do_not_message (if consented: send 3) | Unchanged. |
| P021 | incident_management | 3 -> 3 | do_not_message (if consented: hold) | Hidden 3 kept; even with consent this would be hold (Codex 3->H). |
| P021 | technical_writing | 3 -> 3 | do_not_message (if consented: send 3) | Unchanged. |
| P021 | code_review | 3 -> 3 | do_not_message (if consented: send 3) | Unchanged. |
| P021 | java | 1 -> 1 | do_not_message (if consented: hold) | Hidden 1 kept (decayed); hold even with consent. |
| P021 | azure | - -> - | do_not_message (if consented: hold) | Not held; hold even with consent. |
| P022 | salesforce | 2 -> 2 | send 2 | Unchanged. |
| P022 | solution_selling | 2 -> 2 | send 2 | Unchanged; SE notes and CRM title must not lift it. |
| P022 | account_management | 1 -> 1 | hold | Hidden 1 kept; no account plan evidence, audit 1->H. |
| P022 | customer_onboarding | 0 -> 0 | hold | Not held; CV/self only, hold. |
| P022 | stakeholder_management | 2 -> 2 | hold | Hidden 2 kept; mapping uncertain, hold. |
| P022 | excel_modeling | 0 -> 0 | not_extract | Excluded generic. |
| P023 | customer_onboarding | 3 -> 3 | send 3 | Unchanged. |
| P023 | account_management | 2 -> 2 | send 2 | Unchanged. |
| P023 | salesforce | 1 -> 1 | send 1 | Unchanged; coordinator-created records must not lift it (F14). |
| P023 | stakeholder_management | 2 -> 2 | send 2 | Unchanged. |
| P023 | technical_writing | 2 -> 2 | hold | Hidden 2 kept; co-authorship (F34), hold. |
| P023 | servicenow | 0 -> 0 | not_extract | Not held. |
| P023 | solution_selling | 0 -> 0 | hold | Not held; audit 0->H because expansion records could mislead, hold not No. |
| P023 | sql | 0 -> 0 | hold | Not held; listed only. |
| P024 | servicenow | 2 -> 2 | send 2 | Unchanged; volume must not lift it (F17). |
| P024 | incident_management | 1 -> 2 | send 2 | 1->2: the escalation-with-update-cadence record is the level 2 line; level 1 is assessed-only. |
| P024 | linux | 0 -> 0 | hold | Not held; listed-only, hold. |
| P024 | sql | 0 -> 0 | hold | Not held; hold. |
| P024 | python | 0 -> 0 | hold | Not held; hold. |
| P024 | stakeholder_management | 0 -> 0 | not_extract | Not held; generic wording must not map. |
| P025 | talent_acquisition | 3 -> 3 | hold | Hidden 3 kept; D-U4 invisible-but-real -> hold. |
| P025 | workday | 2 -> 2 | hold | Hidden 2 kept; v1 expected send 2, but training + self cannot reach High. Audit: Workday 2 -> H. |
| P025 | hr_operations | 1 -> 1 | hold | Hidden 1 kept; listed-only, hold. |
| P025 | stakeholder_management | 2 -> 2 | hold | Hidden 2 kept; audit 2->H. |
| P025 | excel_modeling | 0 -> 0 | not_extract | Excluded generic. |
| P025 | technical_writing | 0 -> 0 | not_extract | Wrong mapping. |
| P026 | hr_operations | 4 -> 4 | send 3 | Hidden 4 kept; oracle 3 because only the SOP shows level 4 (title not used). 3 is still a Yes. |
| P026 | workday | 3 -> 3 | send 2 | Hidden 3 kept; audit 3->H resolved as send at floor 2 (two groups). |
| P026 | sap | 2 -> 2 | hold | Hidden 2 kept; decay + module ambiguity -> hold (audit 2->H). |
| P026 | stakeholder_management | 3 -> 3 | send 2 | Hidden 3 kept; bundle pins 2 (one decision record). Yes either way. |
| P026 | technical_writing | 3 -> 3 | send 3 | Unchanged. |
| P026 | excel_modeling | 0 -> 0 | not_extract | Excluded generic. |
| P026 | servicenow | 0 -> 0 | not_extract | Requester only. |
| P027 | api_testing | 2 -> 2 | send 2 | Unchanged; demo/POC use must not be read as QA practice (F35). |
| P027 | solution_selling | 2 -> 2 | send 2 | Unchanged. |
| P027 | salesforce | 1 -> 1 | send 1 | Unchanged; K3 exact 1. |
| P027 | technical_writing | 2 -> 2 | send 2 | Unchanged. |
| P027 | python | 1 -> 1 | hold | Hidden 1 kept; audit wants stronger evidence -> hold. |
| P027 | aws | 0 -> 1 | hold | 0->1 hidden: a verified current foundational exam contradicts 'no skill' (Codex). Oracle hold: knowledge-only, stale work. |
| P027 | customer_onboarding | 0 -> 0 | not_extract | Not held. |
| P028 | java | 2 -> 2 | send 2 | Unchanged. |
| P028 | spring_boot | 2 -> 2 | send 2 | Unchanged. |
| P028 | sql | 2 -> 2 | send 2 | Unchanged. |
| P028 | api_testing | 2 -> 2 | send 2 | Unchanged. |
| P028 | agile_delivery | 2 -> 2 | hold | Hidden 2 kept; thin, hold. |
| P028 | security_fundamentals | 1 -> 2 | hold | 1->2 hidden: the reviewed log-masking fix from a security finding is the level 2 line (D-U2). Oracle hold: single change. |
| P028 | kubernetes | - -> - | hold | Not held; hold. |
| P028 | llm_engineering | - -> - | hold | Not held; listed-only, hold. |
| P029 | ux_research | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P029 | figma | 3 -> 3 | hold | Hidden 3 kept; D-U4 invisible-but-real -> hold. assessed_level removed: no assessment file. |
| P029 | product_discovery | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P029 | stakeholder_management | 3 -> 3 | hold | Hidden 3 kept; hold. assessed_level removed: no assessment file. |
| P029 | technical_writing | 2 -> 2 | send 2 | Unchanged. assessed_level removed: no assessment file. |
| P029 | agile_delivery | 2 -> 2 | hold | Hidden 2 kept; participation only, hold. assessed_level removed: no assessment file. |
| P029 | roadmapping | - -> - | not_extract | Not held; disclaimed. |
| P030 | python | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P030 | sql | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P030 | airflow | 3 -> 3 | send 3 | Unchanged. assessed_level removed: no assessment file. |
| P030 | pyspark | 2 -> 2 | hold | Hidden 2 kept; decayed, hold. |
| P030 | data_modeling | 2 -> 2 | hold | Hidden 2 kept; hold. assessed_level removed: no assessment file. |
| P030 | agile_delivery | 2 -> 2 | hold | Hidden 2 kept; hold. assessed_level removed: no assessment file. |
| P030 | kafka | - -> - | hold | Not held; listed-only. |
| P030 | snowflake | (new) -> 2 | send 2 | New row: the bundle shows Snowflake work that v1 did not label; an engine will extract it. |
| P031 | python | 3 -> 3 | send 3 | Unchanged; title must not cap level (F20). assessed_level removed: no assessment file. |
| P031 | airflow | 2 -> 2 | send 2 | Unchanged. assessed_level removed: no assessment file. |
| P031 | sql | 2 -> 2 | send 2 | Unchanged. assessed_level removed: no assessment file. |
| P031 | api_testing | 2 -> 2 | hold | Hidden 2 kept; mapping weak, hold. assessed_level removed: no assessment file. |
| P031 | agile_delivery | 2 -> 2 | hold | Hidden 2 kept; participation only, hold. assessed_level removed: no assessment file. |
| P031 | technical_writing | 1 -> 2 | hold | 1->2 hidden: reviewed procedure docs are guided applied work (D-U2); v1 would_accept [1,1,2] fixed. Oracle hold: thin. assessed_level removed: no assessment file. |
| P031 | docker | - -> - | hold | Not held; listed-only. |
| P032 | excel_modeling | 3 -> 3 | send 3 | Unchanged hidden 3. v1 trap wanted hold, but the authored workbook process shows the level 3 line; only the CV Office line is generic. |
| P032 | sql | 2 -> 2 | send 2 | Unchanged. assessed_level removed: no assessment file. |
| P032 | stakeholder_management | 2 -> 2 | send 2 | Unchanged. assessed_level removed: no assessment file. |
| P032 | technical_writing | 2 -> 2 | send 2 | Unchanged. assessed_level removed: no assessment file. |
| P032 | agile_delivery | 1 -> 1 | hold | Hidden 1 kept; v1 would_accept [1,1,2] fixed to [1,2]; hold. assessed_level removed: no assessment file. |
| P032 | data_modeling | - -> - | not_extract | Wrong mapping. |
| P032 | python | - -> - | not_extract | Not held; nothing to extract. |

## 3. Trap expectation changes

New field `evidence_expectation` on a trap says what the engine must do with the planted evidence item (ignore a bot PR, not join by name, not credit a co-author) when the skill itself still sends or holds. `v1_expected_engine_behavior` keeps the old value.

| PID | Trap (fault:skill) | v1 | v2 | Reason |
|---|---|---|---|---|
| P001 | none:cv_lineage_duplicate:airflow | hold | send_at_level_4 | v1 hold contradicted Airflow true 4 with strong work+doc evidence. |
| P001 | F18:python | join_neither | send_at_level_3 | Stable key present; D-U3: stable key wins, so the correct behaviour is a normal send, not join_neither. |
| P001 | F10:aws | not_extract | send_at_level_3 | Bot PRs bump boto3/amazon provider, not PySpark; retargeted to aws. Skill still sends. |
| P001 | F16:python | not_extract | send_at_level_3 | Evidence-level not_extract; skill outcome is send 3. |
| P002 | F18:python | join_neither | hold | Stable key present on both records; D-U3 gives a clean join, so the skill outcome (hold) is the expectation, not join_neither. |
| P002 | F06:workday | send_at_level_3 | send_at_level_2 | Workday oracle is send at floor 2 (doc + rollout allocation). |
| P003 | F25:kubernetes | not_extract | hold | Evidence-level not_extract; Kubernetes skill outcome is hold. |
| P003 | F14:incident_management | not_extract | send_at_level_2 | Evidence-level not_extract; skill still sends at 2 from his own INCs. |
| P004 | F28:java | send_at_level_2 | hold | Decayed Java with self 4 vs evidence 2: hold, not send 2. |
| P004 | F28:spring_boot | send_at_level_2 | hold | Same decay for Spring Boot. |
| P004 | F19:technical_leadership | send_at_level_4 | send_at_level_3 | Oracle sends 3 (bundle pins 3); still a Yes for him, and not down-levelled to code evidence. |
| P004 | F34:system_design | hold | send_at_level_3 | Skill outcome is send 3 from ADR-014 and project role; the trap is about not crediting the co-authored page. |
| P004 | F15:java | not_extract | hold | Java skill outcome is hold. |
| P005 | F25:go | not_extract | send_at_level_3 | Evidence-level not_extract; Go skill outcome is send 3. |
| P005 | F16:go | not_extract | send_at_level_3 | Evidence-level; skill sends 3. |
| P005 | F10:go | not_extract | send_at_level_3 | Evidence-level; skill sends 3. |
| P006 | F05:kubernetes | not_extract | hold | Kubernetes maps correctly from the CV; listed-only skills are holds, not not_extract. |
| P006 | F10:javascript | not_extract | send_at_level_2 | Evidence-level; JavaScript still sends 2. |
| P012 | F28:selenium | send_at_level_2 | send_at_level_3 | Selenium oracle now send 3 (last independent use inside 2y window); decay is real but does not reach level 2 yet. |
| P012 | F29:selenium | send_at_level_2 | send_at_level_3 | Engine must not send 4; send 3. |
| P012 | F18:playwright | join_neither | send_at_level_3 | Stable key (linked_employee_id) is present, so D-U3 gives a clean join; join_neither was too strong (Codex). |
| P012 | F16:selenium | not_extract | send_at_level_3 | Evidence-level; skill sends 3. |
| P012 | F25:selenium | not_extract | send_at_level_3 | Evidence-level; skill sends 3. |
| P013 | F18:react | join_neither | send_at_level_3 | Stable key present; join_neither too strong (Codex, Opus). |
| P014 | F14:react | not_extract | send_at_level_3 | Evidence-level; React still sends 3. |
| P015 | F01:kubernetes | send_at_level_1 | hold | Contradictory v1 traps on Kubernetes unified to hold (measured Beginner vs self/CV 3+). |
| P015 | F24:azure | not_extract | hold | Azure maps correctly; lapsed unverifiable cert -> hold, not not_extract. |
| P015 | F26:kubernetes | not_extract | hold | Unified with Kubernetes oracle hold. |
| P015 | F25:gcp | not_extract | hold | GCP cert PDF maps correctly to gcp; no work -> hold. |
| P016 | F01:java | send_at_level_1 | hold | Java: measured Beginner vs self 4/CV Expert -> hold, not send 1. |
| P016 | F29:java | send_at_level_1 | hold | Same Java oracle. |
| P016 | F13:java | send_at_level_1 | hold | Same Java oracle. |
| P016 | F25:performance_testing | not_extract | send_at_level_3 | Evidence-level; performance_testing still sends 3. |
| P017 | F12:react | not_extract | hold | Evidence-level; React skill outcome is hold. |
| P018 | F15:aws | not_extract | hold | AWS skill outcome is hold (CV mention maps correctly). |
| P019 | F13:java | send_at_level_2 | hold | Java oracle is hold (co-authored only), not send 2. |
| P022 | F19:solution_selling | not_extract | send_at_level_2 | Evidence-level; solution_selling still sends 2. |
| P023 | F25:salesforce | not_extract | send_at_level_1 | Evidence-level; Salesforce outcome is send 1. |
| P024 | F26:sql | not_extract | hold | SQL maps correctly from the CV; listed-only -> hold. |
| P024 | F16:incident_management | hold | send_at_level_2 | Evidence-level; v1 hold contradicted the held skill. Skill sends 2 from the P1 escalation records. |
| P025 | F06:hr_operations | not_extract | hold | hr_operations maps correctly from the skills line; listed-only -> hold. |
| P025 | F25:workday | send_at_level_2 | hold | Workday oracle is hold (training + self only), not send 2. |
| P026 | F28:sap | send_at_level_2 | hold | SAP decayed past 2y and the module is ambiguous; hold rather than send 2. |
| P026 | F19:hr_operations | send_at_level_4 | send_at_level_3 | Oracle states 3 (level 4 shown by one group only); 3 is a Yes. |
| P026 | F29:workday | send_at_level_3 | send_at_level_2 | Workday oracle is floor 2. |
| P027 | F25:aws | not_extract | hold | AWS maps correctly; oracle hold (knowledge-only cert, stale work), not not_extract. |
| P028 | F32:java | hold | send_at_level_2 | Message-misread is an answer-scoring behaviour; the skill oracle is send 2. |
| P028 | F14:java | hold | send_at_level_2 | Evidence-level; Java still sends 2. |
| P030 | F23:python | join_neither | send_at_level_3 | D-U3: a rehire record is a stable key, so join, not join_neither. |
| P030 | F16:sql | hold | send_at_level_3 | Evidence-level; SQL still sends 3. |
| P031 | F16:sql | hold | send_at_level_2 | Evidence-level; SQL still sends 2. |
| P032 | F06:excel_modeling | hold | send_at_level_3 | Bundle shows the level 3 line in authored work; hold was too strict. |

## 4. Schema additions beyond 8.1

- `oracle.if_consented` (P021 only): what the engine would decide if the EU opt-in existed, so skill inference and the consent gate are scored separately.
- `identity_expectation` (top level, identity personas P010-P014, P018-P020, P030): which stable key joins the records.
- Trap `evidence_expectation` and `v1_expected_engine_behavior` (see section 3). Decoys also carry an `oracle`.
- `unmatched_skills` filled for 24 personas (for example HCM SuccessFactors, React Native mobile specifics, JMeter/k6, Postman, sourcing).

## 5. Judgment calls for you to decide

- Self-rating 2+ levels off (STEP-4.9). I did not treat it as a pre-send hold, because GR.5 files it under answer handling. If you read it as an engine rule, P018 technical_leadership (self 4 vs 2), P023 salesforce (self 3 vs 1), P028 (self 4 everywhere vs 2) and a few others would flip from send to hold.
- Listed-only skills that map correctly are `hold`, not `not_extract` (for example P006 Kubernetes, P015 GCP and Azure, P018 AWS). v1 used both for the same pattern. If you want `not_extract` to mean 'never becomes a candidate skill', several traps flip back.
- Co-authored-only evidence is held (P005 Kubernetes, P019 Java, P023 technical_writing). v1 sent P019 Java at 2.
- Hidden level kept above the oracle level: where the bundle pins a lower level than the private story (P004 technical_leadership 4, P021 terraform 4, P026 hr_operations 4, P017 go 4), I kept the hidden level and sent the floor. Both are Yes for the person, but you may prefer the oracle to state the hidden level when one group clearly shows it.
- Single authored page: I hold technical_writing when one page is the only group (P002, P005, P018) and send the floor when a second group exists (P001, P003, P014). This is a mechanical line, not a strong belief.
- New P030 Snowflake row (send 2): the bundle shows Snowflake work that v1 never labelled. I added no other new rows; there may be similar gaps elsewhere.
- P001 aws: send 3 vs 2. Mechanical floor/ceiling gives 2 (cert + reviewed infra PRs); I chose 3 because she operates S3/IAM pipelines on-call. Both are Yes for her.
- P001 technical_writing: send 2 vs hold. One strong authored page enforced by CI plus the Jira task to write it.
- P002 workday: send 2 (floor from authored guide + rollout allocation) vs hold (Codex audit: no audited transactions).
- P003 incident_management: send 2 vs hold. P1 comms-owner record could argue 3; I sent the floor 2.
- P004 system_design: send 3 vs hold. v1 trap wanted hold because the 2025 page is co-authored; I kept ADR-014 + project allocation as enough for 3.
- P004 code_review: sending 'code review level 2' to a Director-track EM is accurate but may be a relationship risk (Opus open question).
- P005 sql: sent at 2 (SQL embedded in Go service work) though hidden is 3.
- P008 code_review 3: reviews are templated (generator artifact); Opus would rate 2.
- P012 selenium: raised hidden 2->3 and oracle send 3 (Codex view). This undoes the planted decay trap; if you want the trap to bite, keep hidden 2 and send 2 (both are Yes for him).
- P015 kubernetes: hidden 1->2 per D-U2 (guided helm edits) despite a 44% fundamentals test. If you read the test as proof he only 'explains', keep 1.
- P017 stakeholder_management: hold vs send 3 (one strong Finance decision record).
- P019 java: hold (co-authored only) vs send 2 (v1).
- P023 salesforce: K3 exact level 1 rests on her own third of the activity records; if you think attribution makes any level unpinnable, switch to hold.
- P026 hr_operations: send 3 (floor/ceiling) vs 4 (the SOP alone meets the level-4 line). Both are Yes for her.
- P027 aws: hidden now 1 (verified Cloud Practitioner). Oracle hold; a strict 'verified cert + CV' route would send level 1, which he would accept.
- P032 excel_modeling: the roster calls Excel 'generic/exclude', but the repaired bundle has a detailed workbook process; I send 3. If you want P032 to stay a near-zero-coverage persona, set hold.
