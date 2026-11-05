---
doc_id: DOC-SALES-2231
space: SALES
title: Customer Onboarding Playbook - Mid-Market (v3)
created: 2022-11-14
last_edited: 2026-08-19
author: Rahul Verma
contributors: [Rahul Verma, Aditi Bhosale, Karan Mehra, Neelam Joshi]
page_views_90d: 187
---
## Purpose
How a mid-market customer (1-5 entities, up to 6 bank feeds) goes from signed order form to "activated". Activated means the acceptance checks below are signed off by the customer's finance owner. Not for enterprise (see ENG space for the integration-led track).

## Phases and exit criteria
| Phase | Target days | Exit criteria |
|---|---|---|
| 0. Handoff | 0-3 | AE handoff note complete (buyer map, promised dates, custom terms). CSM reads the opp, not just the note |
| 1. Kickoff | 4-10 | Plan v1 shared, customer owner named for finance AND IT, sftp / API access request raised |
| 2. Data feeds | 10-25 | Statement import running for every bank account in scope, 2 clean days |
| 3. Matching rules | 20-32 | Auto-match >= 85% on last 30 days of customer data, exceptions queue reviewed with customer |
| 4. UAT | 28-38 | Customer runs one close cycle in parallel, signs UAT form |
| 5. Go-live | ~38 | Old process stopped, support runbook shared, QBR booked at day 90 |

## Things that slip (learned the hard way)
- sftp whitelisting at the customer end. Ask in kickoff, not at phase 2. Typical delay: 6-9 days
- Narration formats differing across branches of same bank. Get 3 sample files per account on day 1
- Finance owner on leave during UAT. Name a backup in kickoff

## Acceptance checks (used by every CSM since v2)
1. Every in-scope bank account has statements for the last full month
2. Auto-match rate on a customer-chosen week is recorded in the plan
3. Two customer users have resolved an exception end to end without us
4. Support has the account tagged, escalation contacts verified

## Changelog
- v3 (Aug 2026): added backup owner rule, removed SFTP-only path for API customers (Karan)
- v2 (Mar 2024): acceptance checks added after two disputed go-lives
