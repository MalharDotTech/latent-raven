---
doc_id: ARCH-142
space: ARCH
title: "Review clinic notes - cancellation"
created: 2026-04-08
last_edited: 2026-09-24
author: "Karthik Subramanian (KC-10717)"
contributors: ["recon-maintainer-kc"]
page_views_90d: 188
---

The recurring review problem is a handler timeout with a worker still running. Please bring the worker's exit path to the review, not just the response deadline. In Go the context needs to reach the row iterator and any blocked channel send. A deferred cancel in the handler does not release a mutex held by a worker waiting on its receiver.

For the recon example, we moved the send outside the lock and selected between delivery and context cancellation. The maintainer added a test which stops the receiver while the scan is active and checks that the goroutine count returns to baseline. Ledger reused the fixture with its own iterator rather than importing a test-only helper across repositories.

Java has a different failure here: the task can swallow InterruptedException and continue retrying. Restore interrupted status where the operation cannot finish, and make the executor shutdown path observable. An unbounded queue can hide this for minutes in a quiet test environment. Billing now exercises a full queue and shutdown together.

Clinic follow-up, September: two newer reviewers found swallowed interrupts in separate billing changes before merge. I reviewed their explanations with the service lead; both described the exit condition correctly. The checklist now asks for the cancellation owner, the blocking call and a failure test. A tick against 'timeout configured' is not sufficient. Keep ordinary small changes out of the clinic queue; this is for changes that alter concurrency or failure handling.
