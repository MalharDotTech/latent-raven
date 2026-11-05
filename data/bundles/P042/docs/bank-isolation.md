---
doc_id: ARCH-407
space: ARCH
title: "Backfill isolation notes"
created: 2026-05-19
last_edited: 2026-06-02
author: Vivek Narang
contributors: ["Deepak Basu", "Aditi Jain"]
page_views_90d: 86
---

We agreed to isolate replay work by bank rather than by tenant. A tenant queue would give more granular fairness, but the number of active queues and the operational burden are high for the actual traffic we have. Most of the damaging bursts come from one delayed bank file, so bank isolation addresses the immediate failure mode.

The capacity run used 600 files per hour, including one large bank and a long tail of small banks. At the current worker count we can keep that load inside the cutoff if no more than 80 jobs run concurrently. Raising concurrency beyond that made database wait time grow without increasing completed files. The service owner has kept the load input and output in the release attachment.

A bank that fails its acceptance check stays paused while the other banks continue. The pause must be visible on the operations screen. A quiet queue must not look like a healthy completed queue. On-call should check oldest item age and the number of rejected files before declaring recovery.

The rollout is flag-first. Create the queues, run shadow routing, then enable one bank. If we roll back, stop new routing and drain the enabled queue before switching the consumer. The team accepted that order after the staging exercise left a partial batch behind with the earlier sequence.

Delivery review, 2 June: Vivek recorded the decision and owners. Deepak completed the failure test with one bank unavailable; Leena checked that reporting totals stayed unchanged. Production validation passed the queue-age and latency checks. The remaining follow-up is to make the paused-bank message easier to find in the runbook.
