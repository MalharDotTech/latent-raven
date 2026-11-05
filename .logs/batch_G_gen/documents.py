# doc key, space, title, date, body. Source metadata is generated separately.
DOCS = {
'P035': [('review-flow','PM','Exception review - case study','2026-09-03','''The reconciliation review screen was the first flow I worked on from interview to handoff. The old screen mixed bank file status and user actions. In the first sessions people opened the same exception more than once because they could not see whether it had been handled. I put the status next to the amount and kept the action in the drawer, so the table could still be scanned quickly.

I recruited eight participants from the pilot group and used the same set of exceptions for the second round. Time on task went from 4m 12s to 2m 46s. Completion went from 61% to 78%. I counted a completed task when the participant selected the correct exception and finished the review without help. Some participants already knew the product, which made the second session easier for them.

The Figma prototype uses one amount component and variants for pending, reviewed and disputed status. The difficult bit was the long bank reference. On a narrow screen it pushed the amount into a second line. I tried two layouts and kept the reference under the bank name, with the amount right aligned.

For handoff I put the loading and empty states next to each screen instead of in a separate page. Engineering asked for examples with missing bank names and negative amounts. Those are in the file now. On the final build I checked the table at 1280 and 1440 widths and sent the spacing corrections. I would like to revisit keyboard order in the drawer next.''')],
'P036': [('partner-replay','SALES','Partner replay checks','2026-07-09','''Use a separate merchant in the pilot tenant for retry checks. Do not reuse a merchant whose opening balance is part of the finance acceptance sheet. Before starting, ask the partner to record their idempotency key and the UTC request time. We need both when looking up the request in the service logs.

Start with a successful small payment and save the response. Send the same key and body again. The second response should refer to the first payment and the ledger total must stay unchanged. Next send the same key with a different amount. Expect a conflict, with the request identifier in the error response. Do not carry that changed amount into the next test by accident.

For the timeout case, let the upstream simulator return a timeout after receiving the request. Retry with the original key. A successful HTTP response alone is not the acceptance check: compare the final posting count and amount as well. Keep the response body in the run attachment so we can distinguish a duplicate response from a second posting.

For finance signoff use the agreed bank value date, not the local date on the laptop. Ask the controller to confirm the two source totals before running the query. If a reversal is present, keep it in the detail attachment and show its effect on the net amount.

Review, 14 July: Priyanka Rao corrected the original draft which used a new key after timeout. Updated the request sequence and added the final posting-count check. The integration pod will use this sequence for the next pilot.''')],
'P041': [('fi-close','ENG','FI close extract checks','2026-06-11','''This procedure is for the finance close extract, not the operational reconciliation dashboard. Begin with the company code and posting period from the close calendar. Save the selection variant with the period in its name. Leaving last month's period in the variant is an easy mistake when the screen opens with the previous values.

Export the document detail with reversal reference and cost centre included. Keep the raw export on its own sheet. Do not delete reversed documents from the raw file; show the net effect in the reconciliation tab instead. The total on that tab should agree to the ledger report for the same company code and period. A cost centre report with a different selection is not a useful control total.

Parked documents are listed separately. For each item record the document number, blocking field and the AP owner. A corrected cost centre can have a validity date later than the original posting date. Check both before asking AP to repost, otherwise the same document will return in the next exception list.

Once the totals agree, paste values into the actuals input of the forecast workbook. The scenario formulas should not point directly to the downloaded file. Run the formula checks and compare opening cash to the signed close report. Save the workbook version before sending the finance review link.

Meenal review, 16 June: the draft did not distinguish parked documents from posted items. Corrected the extraction step and added the separate parked-document list. Also added company code to the checklist after a test export picked the wrong saved variant.''')],
'P042': [('bank-isolation','ARCH','Backfill isolation notes','2026-05-19','''We agreed to isolate replay work by bank rather than by tenant. A tenant queue would give more granular fairness, but the number of active queues and the operational burden are high for the actual traffic we have. Most of the damaging bursts come from one delayed bank file, so bank isolation addresses the immediate failure mode.

The capacity run used 600 files per hour, including one large bank and a long tail of small banks. At the current worker count we can keep that load inside the cutoff if no more than 80 jobs run concurrently. Raising concurrency beyond that made database wait time grow without increasing completed files. The service owner has kept the load input and output in the release attachment.

A bank that fails its acceptance check stays paused while the other banks continue. The pause must be visible on the operations screen. A quiet queue must not look like a healthy completed queue. On-call should check oldest item age and the number of rejected files before declaring recovery.

The rollout is flag-first. Create the queues, run shadow routing, then enable one bank. If we roll back, stop new routing and drain the enabled queue before switching the consumer. The team accepted that order after the staging exercise left a partial batch behind with the earlier sequence.

Delivery review, 2 June: Vivek recorded the decision and owners. Deepak completed the failure test with one bank unavailable; Leena checked that reporting totals stayed unchanged. Production validation passed the queue-age and latency checks. The remaining follow-up is to make the paused-bank message easier to find in the runbook.'''),
('oncall-guide','ENG','Replay handover steps','2026-09-17','''Start a handover with the oldest outstanding file and the bank cutoff, not just the alert count. An empty alert list can mean the input file never arrived. Compare expected files with the manifest and check whether any bank is paused. Record the last acknowledged partition before asking someone else to continue a replay.

The outgoing engineer should leave the current flag state, queue name and file identifiers in the handover ticket. Do not paste tokens or full customer payloads. Use the request ID when pointing to logs. The incoming engineer should confirm that they can find the same failed partition before the outgoing engineer signs off.

For recovery, run the smallest safe replay first and compare count and amount to the bank trailer. A successful task status is not enough. If the partition already has a success marker, stop and check the ledger acknowledgement rather than deleting the marker to make the task run again.

Escalate a cutoff risk to the service owner and the incident coordinator with the remaining file count and current processing rate. Keep a separate action for customer communication. Engineering recovery and customer updates tend to finish at different times.

Validation, 24 September: Deepak and Aditi used version 3 during the staging handover drill. Both found the paused bank and recovered the failed partition without a prompt. Aditi could not locate the flag name from the first draft; Vivek added the exact configuration path and repeated that step successfully. Version 4 is the current team handover link.''')],
}
