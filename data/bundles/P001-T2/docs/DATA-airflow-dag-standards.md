---
doc_id: DATA-airflow-dag-standards
space: DATA
title: Airflow DAG authoring standards (v2)
created: 2024-10-22
last_edited: 2026-06-09
author: Ayesha Khan
contributors: [Ayesha Khan, Karan Bhatt]
page_views_90d: 212
---
# Airflow DAG authoring standards

Applies to every DAG in `data-platform`. Enforced by pre-commit (`dag-lint`) and a CI check.

## 1. Naming
`<domain>_<entity>_<cadence>` e.g. `billing_events_hourly`. task_ids are stable: changing a task_id resets run history in the UI and breaks clears. If you must rename, say so in the PR description.

## 2. Idempotency
Every task must be safe to re-run for the same logical date. Writes go to `s3://.../dt=<ds>/` and are replaced, never appended. Use `MERGE` for table targets. Do not use `datetime.now()` inside a task; use `data_interval_start`.

## 3. Retries and alerts
- default_args: retries=2, retry_delay=5m, retry_exponential_backoff=True
- tier1 DAGs must set `sla` and `on_failure_callback=notify_oncall`
- No `retries=0` without a comment saying why

## 4. Sensors
Use `mode="reschedule"` for anything waiting more than 5 minutes. Poke blocking sensors starve worker slots (see DATA incident from Dec 2022).

## 5. XCom
Pass paths and small dicts only. Never push a DataFrame.

## 6. Backfills
Use `scripts/backfill_cli.py --dry-run` first. The CLI refuses to start if a backfill for the same DAG and overlapping range is running.

## 7. Data quality
Tier1 DAGs end with `dq_check_group` (row count, freshness, null thresholds). Thresholds live in `dq/thresholds.yaml`, not in the DAG.

## Open questions
- dataset-aware scheduling vs sensors for silver->gold (see DATA-2852)
