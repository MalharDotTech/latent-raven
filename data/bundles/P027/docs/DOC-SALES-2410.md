---
doc_id: DOC-SALES-2410
space: SALES
title: Recon API - 20 minute demo walkthrough (Postman)
created: 2023-08-03
last_edited: 2026-05-22
author: Jason Lee
contributors: [Jason Lee, Rina Patel (PMM), Tomas Weber]
page_views_90d: 233
---
Collection: "Kestrel Recon API - Demo v5" in the SE team workspace. Environment variables: base_url, api_key, tenant_id. Always run against the demo tenant, never prod.

## Flow
1. POST /v2/auth/token - tests: status 200, token present, expires_in > 0
2. POST /v2/statements/import (sample bank CSV) - tests: 202 Accepted, body.job_id exists. Pre-request script stores job_id
3. GET /v2/jobs/{job_id} - poll (Postman `setNextRequest`) until status = completed or 30s
4. GET /v2/matches?job_id= - tests: matched_count / total >= 0.85 on the sample file, each match has confidence field
5. POST /v2/webhooks/test - receive on webhook.site, verify HMAC header

## Failure cases to show (customers always ask)
- Bad token: expect 401 with error.code = AUTH_EXPIRED
- Re-posting the same file with the same Idempotency-Key: expect 200 and the original job_id, not a new job
- Burst above limit: 429 with Retry-After header

## Running with Newman
`newman run recon-demo-v5.json -e demo-env.json --reporters cli,junit` - I run this before every customer call from my laptop. It is not wired into CI. Rina asked for it, backlog item PM-839.

## Small helper (python)
```
import requests, time
r = requests.post(f"{BASE}/v2/statements/import", files={"file": open("sample.csv","rb")}, headers=H)
job = r.json()["job_id"]
while requests.get(f"{BASE}/v2/jobs/{job}", headers=H).json()["status"] != "completed":
    time.sleep(2)
```
Review notes (Rina, May 2026): added the 429 case, shortened section 3.
