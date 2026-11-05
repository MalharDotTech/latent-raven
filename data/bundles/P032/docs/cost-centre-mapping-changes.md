---
doc_id: cost-centre-mapping-changes
space: DATA
title: Cost centre mapping table - change log and how to update
created: 2024-05-21
last_edited: 2026-05-12
author: Manoj Tiwari
contributors: [Manoj Tiwari (FP&A), Deepak Anand (data analyst), Rukmini Iyer (finance operations)]
page_views_90d: 31
---

## Why this exists
The cost forecast workbook maps ledger accounts and cost centres to departments with a lookup table. When a cost centre moves, the table has to change or the department totals drift away from the ledger control report. This page records changes and the steps to apply one.

## Applying a change
1. Rukmini sends the change note from Finance Operations (cost centre code, old department, new department, effective month).
2. I update the mapping table in the workbook and add a row to the change log below, including the effective month and who requested it.
3. Rerun the checks tab. The reconciliation block should return to zero differences. If it does not, look for a second cost centre moved in the same note.
4. If the actuals extract filters by department, I ask Deepak to confirm the filter list. He owns the extract; I have edited the department filter in the query a few times, always sending him the diff before it is used for the pack.

## Change log (recent)
| Effective | Cost centre | From | To | Requested by |
|---|---|---|---|---|
| 2025-04 | 4120 | Platform | Data Platform | Rukmini |
| 2025-10 | 5310 | Support | Customer Success | Rukmini |
| 2026-03 | 2280 | Engineering (Pune) | Engineering (Hyderabad) | Rukmini |
| 2026-06 | 4410 | Product Design | Product | Rukmini |

## What went wrong in June 2026
The note for 4410 came after the actuals export was locked. The department totals were off by the cost centre amount until I added the row and reran the checks. I kept the pre-correction snapshot, showed the difference to Lavanya, and now ask Rukmini to send notes before working day 3.

## Boundaries
The extract query and the warehouse tables belong to the Data team. In this workbook the mapping table is my responsibility; anything that changes how actuals are pulled goes through Deepak.
