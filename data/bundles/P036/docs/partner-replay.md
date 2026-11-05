---
doc_id: SALES-218
space: SALES
title: "Partner replay checks"
created: 2026-07-09
last_edited: 2026-07-14
author: Aman Bhatia
contributors: ["Priyanka Rao"]
page_views_90d: 35
---

Use a separate merchant in the pilot tenant for retry checks. Do not reuse a merchant whose opening balance is part of the finance acceptance sheet. Before starting, ask the partner to record their idempotency key and the UTC request time. We need both when looking up the request in the service logs.

Start with a successful small payment and save the response. Send the same key and body again. The second response should refer to the first payment and the ledger total must stay unchanged. Next send the same key with a different amount. Expect a conflict, with the request identifier in the error response. Do not carry that changed amount into the next test by accident.

For the timeout case, let the upstream simulator return a timeout after receiving the request. Retry with the original key. A successful HTTP response alone is not the acceptance check: compare the final posting count and amount as well. Keep the response body in the run attachment so we can distinguish a duplicate response from a second posting.

For finance signoff use the agreed bank value date, not the local date on the laptop. Ask the controller to confirm the two source totals before running the query. If a reversal is present, keep it in the detail attachment and show its effect on the net amount.

Review, 14 July: Priyanka Rao corrected the original draft which used a new key after timeout. Updated the request sequence and added the final posting-count check. The integration pod will use this sequence for the next pilot.
