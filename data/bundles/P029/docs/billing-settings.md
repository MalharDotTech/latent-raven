---
doc_id: billing-settings
space: PM
title: Billing settings task review
created: 2026-02-10
last_edited: 2026-04-17
author: Divya Krishnamurthy
contributors: [Divya Krishnamurthy (design research), Meenal Joshi (product manager), Arun Prakash (support lead), Vishal Dsouza (engineering lead)]
page_views_90d: 38
---

## Setup
We tested a draft billing settings flow with six account administrators. Meenal asked whether moving the tax settings would reduce support contacts. Participants used a prototype with dummy company data and were asked to change an invoice address, find the tax ID, and invite a second administrator. I wrote the tasks and moderated each session. A support colleague took notes independently. We reviewed the notes together and resolved disagreements against the session notes.

## Who did what
I wrote the script, prototype and tasks. Arun's team supplied the contact-reason data and sat in on three sessions as note-takers. Vishal checked what was feasible in the release scope and told us on 24 March that the permission error states would not be ready. Meenal decided the scope after the readout.

## Observations
Five people found the address field, but three expected tax ID under company profile rather than billing. Two tried to invite a colleague from the billing screen and then navigated away. The prototype did not include permission error states, so this study cannot establish whether the full invite workflow is clear.

Support data from the prior two quarters shows tax and address questions as one of the larger contact reasons, but customer mix and release timing move that number, so we treat it as context, not proof.

## Decision
We recommended linking company profile from billing settings and adding a short description of who can edit tax details. Meenal deferred moving the actual tax field until the permissions work is complete. Engineering added the link to the release scope. Support will compare the next quarter's related contacts with the prior baseline, noting that customer mix and release timing may also affect the count. I sent the task script and anonymised notes to the product team on 17 April.

## Disagreement logged
Arun would have preferred moving the tax field now. The sessions did not test that, so the recommendation stays at the link and description. We will revisit once permission error states exist and can be tested.
