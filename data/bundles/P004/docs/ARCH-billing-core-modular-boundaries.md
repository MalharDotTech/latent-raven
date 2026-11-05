---
doc_id: ARCH-billing-core-modular-boundaries
space: ARCH
title: billing-core modular boundaries (proposal)
created: 2025-05-20
last_edited: 2026-03-10
author: Vikram Reddy
contributors: [Sana Mirza, Dev Patel, Rhea Thomas, Vikram Reddy]
page_views_90d: 96
---
# billing-core modular boundaries (proposal)

Page created by Vikram; sections 2-5 written and revised by the engineers listed above (see page history).

## 1. Problem
`billing-core` has grown to 41 packages with cyclic dependencies between invoicing, tax and metering. A change to proration touches 3 modules. Build time 14 min.

## 2. Proposed modules
- `invoicing`: invoice aggregate, finalisation, numbering client
- `metering`: usage ingest, rating
- `tax`: provider adapters, jurisdiction strategies
- `ledger-bridge`: outbox, posting

## 3. Rules
- Modules depend only on `*-api` packages of other modules
- ArchUnit tests fail the build on cyclic dependencies
- DB tables are owned by one module; cross-module reads go through the api package

## 4. Migration plan
Strangler approach, one module per quarter, starting with `tax` (fewest inbound dependencies). Dev Patel to prototype ArchUnit rules in a branch.

## 5. Risks
Team velocity during migration (est. -15% for two quarters). Mitigation: no new feature work in `tax` while it moves.

## Open questions
Do we split deployables later? Decision deferred to Q3.
