---
doc_id: release-26-3-design-qa
space: PM
title: Release 26.3 design QA notes
created: 2026-03-03
last_edited: 2026-03-27
author: Divya Krishnamurthy
contributors: [Divya Krishnamurthy (design QA), Vishal Dsouza (engineering lead), Anita Fernandes (QA)]
page_views_90d: 33
---

## Scope
Design review of the items in sprint 26.6 and 26.7 before the 26.3 release cut on 25 March: invoice PO number field, exception queue reason in row, billing settings link. Planned in sprint planning on 2 March; this page tracks what I checked.

## How we worked
I joined the two sprint plannings and the Thursday refinement. Anita ran the regression suite and logged defects in Jira; I reviewed each ticket's build on staging against the agreed behaviour and wrote the findings here. Vishal's team fixed items inside the sprint where it was cheap and deferred the rest.

## Findings
- PO number field: label truncates at 20 characters in the PDF preview on Safari. Fixed in sprint.
- Exception queue reason: long reasons wrapped under the status chip on narrow screens. Fixed in sprint.
- Retry confirmation: the dialog reused the delete wording from another screen. Copy corrected after I explained the difference to Vishal; Anita retested.
- Billing settings link: works; focus order skips the link with keyboard navigation. Logged as a follow-up, not a blocker.

## Deferred
Empty state for the reason column when the payment has no failure reason. Product agreed it was not part of this release. Logged as a backlog item for the next sprint.

## Notes for next time
Staging data is thin; several checks needed hand-made records. Anita is writing a data seeding script. I will ask for design QA to be a named step in the definition of done for UI stories.
