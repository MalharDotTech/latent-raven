---
doc_id: PM-2187
space: PM
title: "Exception review - case study"
created: 2026-09-03
last_edited: 2026-09-03
author: Tanvi Menon
contributors: []
page_views_90d: 70
---

The reconciliation review screen was the first flow I worked on from interview to handoff. The old screen mixed bank file status and user actions. In the first sessions people opened the same exception more than once because they could not see whether it had been handled. I put the status next to the amount and kept the action in the drawer, so the table could still be scanned quickly.

I recruited eight participants from the pilot group and used the same set of exceptions for the second round. Time on task went from 4m 12s to 2m 46s. Completion went from 61% to 78%. I counted a completed task when the participant selected the correct exception and finished the review without help. Some participants already knew the product, which made the second session easier for them.

The Figma prototype uses one amount component and variants for pending, reviewed and disputed status. The difficult bit was the long bank reference. On a narrow screen it pushed the amount into a second line. I tried two layouts and kept the reference under the bank name, with the amount right aligned.

For handoff I put the loading and empty states next to each screen instead of in a separate page. Engineering asked for examples with missing bank names and negative amounts. Those are in the file now. On the final build I checked the table at 1280 and 1440 widths and sent the spacing corrections. I would like to revisit keyboard order in the drawer next.
