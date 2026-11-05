---
doc_id: ARCH-118
space: ARCH
title: "ADR 118 - retry ownership"
created: 2025-03-07
last_edited: 2026-08-24
author: "Karthik Subramanian (KC-10717)"
contributors: ["billing-maintainer-kc", "recon-maintainer-kc"]
page_views_90d: 159
---

Status: accepted. Billing and recon both have a retry loop today. We cannot tell a caller that a timeout means the invoice was rejected: the commit may have happened before the response disappeared.

The operation key belongs to the caller and is scoped by tenant and currency. Billing stores it with the invoice and an outbox row in one transaction. Recon consumes the published event with its own duplicate guard. There is no transaction spanning the two services. This leaves a delivery delay, which we can measure and replay; it avoids holding billing locks while a remote worker is unavailable.

Rejected option: a new operation key for every retry. That makes a network failure look like a new financial operation. Also rejected: publish before commit, even if the broker acknowledgement looks reliable. The rollback case then sends an event for an absent invoice.

Karthik's review action: each service lead to draw the unknown-result branch before implementation. Billing added the lost-response branch; recon added the consumer-crash-after-write branch. Both revisions were accepted in the March clinic. The May shadow replay reconciled invoice totals and duplicate counts; no unexplained difference remained in the pilot sample.

2026-08-24 check: both teams still use the failure table in design reviews. Ledger now has a separate retention decision because its replay window is longer. Do not copy the billing window into that service without checking retention and support recovery. Owner names and stopping conditions are required on the rollout sheet.
