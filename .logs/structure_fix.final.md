Implemented [fix_structure.py](/Users/malhar/swadharma/Code/imocha-raven/scripts/fix_structure.py) and validator v2.

- Renumbered 538 PRs, 427 Jira records, 172 ServiceNow records, and 172 Salesforce records.
- Repaired 14 calendar patterns, 17 ticket links, 32 PR chronology conflicts, and 3 Ledgerly references.
- Recomputed 1,731 monthly rows. One PR moved into the following month to follow its ticket.
- Saved 4,070 mapping entries in [id_remap.json](/Users/malhar/swadharma/Code/imocha-raven/data/notes/id_remap.json).

P001–P032: **zero ERRORs**. Seven regression tests pass; rerunning the repair changes no files.

Remaining WARN: P028’s intentional CV words, “dynamic” and “results-driven.” Creation chronology remains unverifiable for 25 references to unexported tickets.

Twins, P033+, and `data/truth/` were untouched.