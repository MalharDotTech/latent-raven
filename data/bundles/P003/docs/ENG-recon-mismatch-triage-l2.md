---
doc_id: ENG-recon-mismatch-triage-l2
space: ENG
title: Recon mismatch triage - L2 checklist
created: 2025-03-04
last_edited: 2026-02-12
author: Arjun Nair
contributors: [Arjun Nair, Sandeep Kulkarni]
page_views_90d: 188
---
# Recon mismatch triage - L2 checklist

Use when a customer reports "numbers do not match". Do not guess, go in this order.

1. **Confirm the window.** Ask for tenant id, the date range and which side they compare with (ERP, bank statement, our dashboard). Note timezone. Many mismatches are IST vs UTC cutoff.
2. **Check job state** in ops console: Recon > Jobs. If state is RUNNING for more than 4h, see RB-114 (restart worker). Do not restart a job in the middle of month end close without telling the CSM.
3. **Check source files.** Missing day, duplicate file name, BOM at start of CSV, extra header row from the bank. KB0010388.
4. **Compare counts before amounts.** Total count in source file vs ingested count. If counts differ, it is an ingestion issue (RECON ticket). If counts match and amounts differ, look at matching rules.
5. **Matching rules.** Check rule order and tolerance. Rule priority changes need CSM approval for the tenant.
6. **Partial payments and refunds.** Settlement posted next day shows as a timing difference. Confirm using txn reference, not amount.
7. **Escalate** to RECON queue with: tenant, window, job id, file names, counts, what you already tried. Tickets without job id get bounced.

## Do not
- edit ledger entries directly (use reversal through admin console after finance approval)
- share raw SQL output with customers; export from the reporting tool

## Contacts
Berlin shift lead for EU tenants. Platform SRE for anything about pods, clusters, nodes (we have no access).
