---
doc_id: ENG-recon-matcher-worker-pool
space: ENG
title: Recon matcher - worker pool and shutdown
created: 2024-07-02
last_edited: 2026-07-30
author: Ayesha Khan
contributors: [Ayesha Khan, Arun K]
page_views_90d: 63
---
# Recon matcher: worker pool and shutdown

How the settlement matcher in `recon-engine` schedules work and stops cleanly. Written after RECON-2934 (workers restarting every ~6 hours).

## Shape
`Dispatcher` reads batches from the tenant-sharded queue and fans out to N `matchWorker` goroutines over a buffered channel (size 2N). Each worker owns a short-lived DB transaction per batch.

## What was wrong
- Workers were started with a `context.Background()` derived from the request, so cancelled requests left goroutines blocked on channel send.
- `time.NewTicker` in the retry loop was never stopped (fixed again in 2026-06).
- No bound on in-flight batches, so heap grew until the OOM killer restarted the pod.

## Rules we follow now
1. Every goroutine gets a context from `errgroup.WithContext`; there is exactly one place that waits (`Dispatcher.Run`).
2. Channels are closed by the sender only.
3. `defer ticker.Stop()` next to the `NewTicker`.
4. Backpressure: dispatcher pauses reads when queue depth > 80% (RECON-2938).
5. Run `go test -race ./...` in CI; flaky shutdown tests get fixed, not retried.

## Debugging checklist
- `curl localhost:6060/debug/pprof/goroutine?debug=2` (needs DEBUG_PPROF=1)
- Look for many goroutines in `chan send` with the same stack
- Compare heap profile before/after a 1h soak

## Open
Per-tenant concurrency limits (noisy neighbour). Not started.
