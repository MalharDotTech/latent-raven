---
doc_id: ENG-2891
space: ENG
title: "FI close extract checks"
created: 2026-06-11
last_edited: 2026-06-16
author: Ritika Shah
contributors: ["Meenal Shah"]
page_views_90d: 84
---

This procedure is for the finance close extract, not the operational reconciliation dashboard. Begin with the company code and posting period from the close calendar. Save the selection variant with the period in its name. Leaving last month's period in the variant is an easy mistake when the screen opens with the previous values.

Export the document detail with reversal reference and cost centre included. Keep the raw export on its own sheet. Do not delete reversed documents from the raw file; show the net effect in the reconciliation tab instead. The total on that tab should agree to the ledger report for the same company code and period. A cost centre report with a different selection is not a useful control total.

Parked documents are listed separately. For each item record the document number, blocking field and the AP owner. A corrected cost centre can have a validity date later than the original posting date. Check both before asking AP to repost, otherwise the same document will return in the next exception list.

Once the totals agree, paste values into the actuals input of the forecast workbook. The scenario formulas should not point directly to the downloaded file. Run the formula checks and compare opening cash to the signed close report. Save the workbook version before sending the finance review link.

Meenal review, 16 June: the draft did not distinguish parked documents from posted items. Corrected the extraction step and added the separate parked-document list. Also added company code to the checklist after a test export picked the wrong saved variant.
