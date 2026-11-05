---
doc_id: DOC-PEOPLE-0733
space: PEOPLE
title: HCM cutover runbook - HR Ops tasks (SuccessFactors to Workday)
created: 2023-05-22
last_edited: 2024-02-26
author: Sunita Rao
contributors: [Sunita Rao, Meghana Reddy, Rajiv Menon (IT)]
page_views_90d: 6
---
Cutover weekend: 30 Sep - 1 Oct 2023. This page records HR Ops tasks only, IT tasks are in the ARCH space.

## T-14 to T-1
- Freeze: no org changes in SuccessFactors from 15 Sep except emergency approvals by HR head
- Extract final data: active workers, positions, comp, job history 2016-2023. Reconciliation sheet owner: Meghana
- Run 3 mock loads in the Workday tenant. Mock 2 failed on the location hierarchy (Hyderabad-2). Fixed in mock 3
- Sign-off criteria: headcount matches to the person (1,714), 0 mismatches on grade and manager for 100-record sample, payroll vendor file test passed

## Cutover
- 18:00 Sat: SuccessFactors set read only
- Load and validate, 3 checkpoints, go / no-go with HR head at 02:00 Sun
- Mon 2 Oct: hypercare desk open

## Hypercare (4 weeks)
Top issues: manager hierarchy for Pune staff, notice period field, Berlin entity tax id. Daily 15 min stand-up.

## After
SuccessFactors archive access (read only, HR Ops + audit) until 31 Dec 2023; data export retained for 7 years in the compliance store.
