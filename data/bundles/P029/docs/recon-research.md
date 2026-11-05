---
doc_id: recon-research
space: PM
title: Exception queue research
created: 2025-05-06
last_edited: 2025-07-22
author: Divya Krishnamurthy
contributors: [Divya Krishnamurthy (design research), Meenal Joshi (product manager), Arun Prakash (support lead), Imtiaz Sheikh (customer success, recruitment)]
page_views_90d: 42
---

## Question
Can finance operators identify which unmatched payments need attention without opening every row? Support reported that users exported the queue and annotated it offline, and three CSMs had mentioned the same habit in QBRs. Meenal wanted to know whether a smaller first release (reason shown in the row) would remove the export habit before committing engineering to the full triage view.

## Who did what
- Recruitment: Imtiaz pulled candidate accounts from customer success; Arun reviewed the recruitment script and consent wording. I made the final selection so that not every participant was a power user.
- Sessions: I facilitated all twelve. A second observer (Arun for five sessions, Meenal for four, a support analyst for three) captured hesitations and wrong selections in a shared sheet.
- Synthesis and recommendations: mine. Meenal edited the summary for the product review but did not change findings.

## Method
Twelve people from eight customer accounts: two administrators, ten daily reconciliation operators. Remote, 45 minutes, consent to take notes; sessions were not recorded and we kept no account numbers. Each participant was asked to find a duplicate payment and decide whether to retry or investigate. The facilitator avoided naming the status chips. We grouped observations by task, then checked the themes against the original notes rather than counting every remark as a separate failure.

The sample overrepresents experienced customers and says nothing about how often these problems occur across the full population. We did not recruit anyone from the EU region, where the queue is configured differently.

## Findings
Seven participants opened the detail drawer to find the reason for failure; four confused retry with re-import (the re-import button sits next to retry and has no confirmation). Participants who exported to a spreadsheet were mostly adding the reason column themselves, copied from the drawer.

## Follow-up
I changed the status wording in a paper prototype and ran a second round with five different operators. All five found the reason without opening the drawer; two still wanted a way to compare source references. Meenal accepted a smaller first release: reason in the row and an explicit retry confirmation. Compare-source-references goes into the discovery backlog, not this release. Support will watch related tickets after release; Arun owns that comparison.

## Open questions
- Does the in-row reason hold up for operators who filter by tenant? Not tested.
- Whether bulk retry is wanted, or only feared. Two participants asked, nine did not mention it.
