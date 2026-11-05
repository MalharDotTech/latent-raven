# Real CV observations (R001-R008) - what real data looks like

> 8 real people, 11 documents (10 CVs + 1 public portfolio case study), collected 2026-11-05 from friends of the author with their documents. Raw files are gitignored (`sample real employee data /`, `data/real/`). This file is PII-free: people are R-ids, no names, contacts or employers that identify them. Use it as the realism seed for synthetic generation and as the reference the synthetic set is compared against.

## RO.0 Who is in the set

| RID | Role family | Seniority | Sources | In taxonomy? |
|---|---|---|---|---|
| R001 | Data engineer moving to AI | ~2y full-time + apprenticeship | 2 CV versions (DE, AI) | yes |
| R002 | Data engineer, fresher | internships + projects | 2 CV versions (general, DE) | yes |
| R003 | Product / UI-UX designer (pharmacy degree) | ~2y + freelance | CV + portfolio case study | partly (figma, ux_research, product_discovery) |
| R004 | Senior solutions engineer, payments | 6y | 1 CV | partly (sales_cs K3, api_testing, java, spring_boot, sql) |
| R005 | Mechanical design engineer, fresher | trainee | 1 CV | no |
| R006 | Civil engineer, fresher | 2 x 1-month internships | 1 CV | no |
| R007 | Civil engineer, fresher | 2 short internships | 1 CV | no |
| R008 | Civil engineer, fresher | 2 x ~3-week internships | 1 CV (scanned image) | no |

Skew, said out loud: one city, mostly one age band (22-30), friends of one person, 4 of 8 freshers. This is a pilot, not a population sample.

## RO.1 Fault patterns seen in real documents

| ID | Pattern | Seen in | Count | Synthetic set had it? |
|---|---|---|---|---|
| RO-01 | Tailored CV versions: same facts re-skinned for a target role (section order, headline, which projects are shown) | R001, R002 | 2/8 | yes (lineage), but versions differed by time, not by target role |
| RO-02 | Same job, different dates across the person's own CV versions (Jan-Apr 2025 vs Aug 2024-Jun 2025) | R002 | 1/8 | no |
| RO-03 | Skills-section inflation: listed tools with no supporting bullet anywhere (Snowflake, Databricks, dbt, PySpark, PL/SQL, MongoDB; Java, Kubernetes, Cassandra) | R001, R002, R004 | 3/8 | yes, but planted as one obvious keyword-stuffed persona; in reality it is the norm, 30-60% of the list |
| RO-04 | Certificate issuer confusion or damage: vendor cert attributed to a prep-course site; truncated cert names; typos in cert titles; no dates or credential IDs | R002, R005 | 2/8 | partly (unverifiable PDFs) |
| RO-05 | Concurrent roles: full-time job + side consulting; degree overlapping full-time work; full-time + 3 freelance gigs | R001, R002, R003, R004 | 4/8 | rare |
| RO-06 | Shared entities across people: two people list the same small D2C brand; two share university, batch and a community project with different roles (co-founder vs web developer) | R003+R004, R001+R002 | 2 pairs | no; synthetic people barely touch each other |
| RO-07 | Career pivots: degree field does not predict role (pharmacy -> designer; ECE -> data; Java engineer -> solutions -> sales consulting) | R001, R003, R004 | 3/8 | weak |
| RO-08 | Rhetoric-heavy, JD-mapped CV prose ("demonstrates the ability to...", "direct parallel to...", "a core SE function") | R004 | 1/8 | yes (P006, P028), but cartoonish |
| RO-09 | Explicit self-rating: percentage bars per tool (AutoCAD 60%, STAAD Pro 20%); portfolio skill bars | R003, R007 | 2/8 | no |
| RO-10 | Exposure dressed as experience: 15-45 day internships described as "I saw the work", site visits listed under certificates, seminars as projects | R006, R007, R008 | 3/8 | no |
| RO-11 | Off-taxonomy workforce: AutoCAD, SolidWorks, STAAD Pro, FEA, GD&T; only MS Office matches, and it is on the exclude list | R005-R008 | 4/8 | no; every synthetic persona was in-taxonomy |
| RO-12 | Protected or irrelevant attributes in the CV: date of birth, gender, marital status, photo, full home address, declaration | R005, R008 (R006, R007 partial) | 4/8 | partly (cv_conventions) |
| RO-13 | Extraction faults before any inference: two-column layout interleaves text; scanned image with no text layer; icon glyphs; URL split across lines; email spelling differs from name | R003, R007, R008, R002, R006 | 5/8 | no; synthetic CVs are clean markdown |
| RO-14 | Specific quantified claims with no attached artifact (row counts and timings, conversion %, currency amounts to the cent) | R001, R003, R004 | 3/8 | yes, but less specific |
| RO-15 | Self-authored corroboration: portfolio case study repeats CV dates and numbers with more detail; live sites exist | R003 | 1/8 | no |
| RO-16 | Current or future-looking end dates ("Nov 2026", "Oct 2026", "Present") on the as-of month | R001, R003, R004 | 3/8 | partly |

## RO.2 What this changes for the engine

- **CV-only people mostly cannot clear the floor.** STEP-4.3 needs 2+ independent groups, a recent measured result, or work in 3+ separate months. A CV is one self-authored group; two CV versions share a lineage and count once. For 6 of 8 real people the reference engine would hold almost everything. That is correct behaviour and a coverage finding: friends' real data is a CV-path test, not a precision test.
- **Self-authored is one group.** R003's portfolio repeats the CV. It adds detail (process, A/B numbers, dates) but the same author wrote both. Independence needs an artifact someone else controls: a live site, a public repo, a reviewer, an employer system.
- **Off-taxonomy must be a first-class outcome.** Half the real set has no taxonomy skill. The right output is zero sends plus an "unmatched skills" list for the customer's taxonomy owner, never a forced mapping (AutoCAD is not `figma`; FEA is not `performance_testing`).
- **Extraction is a fault layer.** Two-column PDFs and scans break text before the reader sees it. Quotes must be checked against the extracted text, and extraction quality should be recorded per source.
- **Ignore protected attributes.** DOB, gender, marital status and photos are in real CVs. The engine must never read them; the fairness twins test that.

## RO.3 What this changes for synthetic generation

- Make skills-list inflation the default (30-60% unsupported), not one planted persona.
- Generate CV versions targeted at different roles, with small date drift between versions.
- Add concurrent roles, career pivots and shared entities between personas (same side business, same university batch, same community project).
- Include off-taxonomy employees (facilities, mechanical, civil, design craft) and freshers whose experience is exposure.
- Render some CVs with extraction damage (column interleave, broken URLs, glyph noise) instead of clean markdown.
- Keep prose plain. Real CVs here are mostly short, typo-prone and uneven; only one is rhetoric-heavy.
