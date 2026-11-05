---
doc_id: ARCH-adr-014-invoice-numbering
space: ARCH
title: ADR-014 Invoice numbering as a separate service
created: 2023-02-06
last_edited: 2023-11-21
author: Vikram Reddy
contributors: [Vikram Reddy, Sana Mirza]
page_views_90d: 41
---
# ADR-014 Invoice numbering as a separate service

Status: Accepted (2023-03-02)

## Context
Invoice numbers must be gapless per tenant per fiscal year in India (GST) and Germany. Today numbering is generated inside `billing-core` using a DB sequence per tenant-year, locked inside the invoice transaction. At 400 tenants this works; at 3,000 tenants the lock contention on `invoice_sequence` shows up as p99 latency during month-end runs. Additional tenant integrations add other numbering schemes.

## Options considered
1. Keep in billing-core, shard sequences. Simple, does not fix the gapless guarantee when a transaction rolls back.
2. Separate numbering service with reservation + confirm (two-phase). Gapless guaranteed by confirm step, rollback releases the number.
3. Pre-allocate blocks to each worker. Fast, not gapless.

## Decision
Option 2. Numbering service owns `(tenant, fiscal_year, series)` counters. Billing calls `reserve` then `confirm` after commit. Orphan reservations older than 15 min are voided by a sweeper and logged in an audit table (needed for auditors).

## Consequences
- One more network hop on invoice finalisation (budget: +15 ms p95)
- Need idempotency key on reserve (invoice draft id)
- Migration: backfill current counters; dual-run for one month-end close
- Additional numbering schemes migrate later, not part of this ADR

## Follow ups
Owner: Sana Mirza. Review with Finance on audit table retention before go-live.
