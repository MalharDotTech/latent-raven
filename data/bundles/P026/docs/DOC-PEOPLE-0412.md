---
doc_id: DOC-PEOPLE-0412
space: PEOPLE
title: Joiner - Mover - Leaver SOP (HR Ops) v4
created: 2018-02-12
last_edited: 2026-07-09
author: Sunita Rao
contributors: [Sunita Rao, Meghana Reddy, Farhan Qureshi]
page_views_90d: 141
---
## Scope
Every employee lifecycle change processed by HR Ops in Workday. Owner: HR Ops Lead. Review: twice a year, or after any audit finding.

## Joiner
1. Offer accepted event is triggered by Talent Acquisition. HR Ops does NOT start pre-boarding until background verification status = Clear.
2. Create pre-hire, verify PAN / bank / address documents against checklist J-3. Two-person check for bank details.
3. Hire business process: manager approval, then HR Ops, then Payroll vendor. SLA: 2 working days after receipt of clear documents.
4. Trigger IT RITM bundle (laptop, email, GitHub access where role requires). Don't raise it before the hire BP is complete or access gets provisioned for a cancelled hire. This has happened twice.

## Mover
- Transfer, promotion and comp change: initiated by manager, approval chain differs for M1+ (see BP table in Appendix B)
- Effective date cannot be back-dated more than 30 days without HR head approval
- Check: cost centre, supervisory org, grade, work location

## Leaver
1. Resignation entered by manager or HR Ops on employee's mail
2. Notice period calculation uses the calculated field NP_END (do not overtype)
3. Exit checklist: assets, access removal (IT RITM), F&F inputs to payroll vendor by 5th
4. Terminate event only after last working day is confirmed in writing

## Controls tested in audit
Sample of 25 transactions per quarter is re-performed by a second HR Ops person; exceptions logged in the control tracker. Last quarter: 0 exceptions of 25. Previous quarter: 1 (wrong cost centre) corrected same day.

## Validation
v4 walk-through done with two new HR Ops joiners in March 2026; both completed a mock mover case without help. Steps 3 and 4 of Joiner reworded after their questions.
