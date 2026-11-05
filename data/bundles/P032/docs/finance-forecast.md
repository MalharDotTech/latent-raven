---
doc_id: finance-forecast
space: DATA
title: Cost forecast workbook notes
created: 2026-02-03
last_edited: 2026-07-16
author: Manoj Tiwari
contributors: [Manoj Tiwari (workbook owner), Lavanya Pillai (FP&A manager, reviewer), Deepak Anand (data analyst, actuals extract)]
page_views_90d: 42
---

## Monthly process
The workbook has separate assumptions, actuals and forecast sheets. Department owners update headcount start dates and vendor commitments in the assumptions tab by the fifth working day. The forecast sheet links those assumptions to monthly salary and expense formulas; it does not overwrite the imported actuals. Actuals arrive from Finance as a locked export. I compare the cost centre totals with the ledger control report before circulating the pack.

The sequence each month: lock the prior month snapshot (file copy with date in the name), paste the new actuals export into the actuals tab, refresh the lookup columns, run the checks tab, then roll the forecast forward one month. Lavanya reviews the pack on working day 8 and signs off the scenario summary.

## Checks
The reconciliation tab flags cost centres where actuals do not match the control report. Investigate the account mapping first, then ask Finance Operations about late journals. In June a cost centre had moved between departments but the mapping table had not been updated. I corrected the table, reran the checks, and retained the prior snapshot for the review.

Other checks on the tab: headcount in the salary build equals headcount in the HR report within two; no negative accruals; vendor commitments sum to the procurement register; the sum of department totals equals the company total (a tie-out that once failed because a department was missing from the roll-up range).

## Scenarios
The hiring scenario changes start dates and a salary inflation assumption, leaving the base case intact. A second scenario delays two vendor renewals. The CFO review uses the difference between each scenario and the base rather than an unlabelled overwritten total. Scenario switches live on one sheet and every scenario-dependent formula reads from the selected case, so there is a single place to change.

## Who does what
I own the workbook structure, formulas, the checks and the monthly pack. Department owners own their assumption rows. Deepak maintains the SQL extracts used for the actuals; I can adjust a filter with his review, and I ask him when a new cost centre needs a new extract. Lavanya reviews and presents to the CFO. The model remains a finance planning workbook, not a production data pipeline.

## Known weaknesses
- Two sheets still use hard-coded FX rates for EUR and USD; the plan is to link them to the treasury rate table by Q4.
- The workbook is slow to open (about 40 seconds) because of volatile lookups on the actuals tab.
- Only one person (me) knows how the scenario switch is wired. A recorded walkthrough for Lavanya is on my list.
