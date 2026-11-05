# 07 Real-world nuances and fault catalog for synthetic employee evidence

Lane: plant the faults real employee data carries so WorkRaven's abstain logic is tested honestly. Error rows refer to S1.1 of `skill-proficiency-inference-engineering-plan.md`.

Verification labels used below:
- **[opened]** = I fetched the page and read the number there.
- **[snippet]** = number came from a search-result summary only; primary page not opened (treat as unverified).
- **[none]** = no source found. The number is a planning assumption, not a fact.

## 1. TL;DR

- CV lies are mostly small, not wholesale. India verification firms see roughly 6-13% discrepancy per check, with employment checks the worst (13% white-collar, AuthBridge, [opened]) and a "resume mismatch" rate of 17% [opened]. Plant mild embellishment (inflated tenure, title, skill list), not fictional careers.
- CV skill lists carry almost no weight alone. Self-assessed vs measured ability correlates only about .29 (meta-analyses, [snippet]). Design the engine so a CV-only skill can never reach a high level.
- Work-system data is attributed to the wrong person in structural ways: bots, squash merges, co-authors, private repos. GitHub only credits commits with an email linked to the account, on the default branch, in non-fork repos [opened]. A real contributor can be invisible and a non-contributor visible.
- HR and identity data is the weakest link for the "wrong person" row. Common surnames (Kumar ~1.2%, Sharma ~1.15%, Singh ~1.07% of Indians, one non-primary table, [snippet]) mean name-only joins will collide. Plant name changes, email changes, duplicates, contractor IDs.
- Certificates expire (AWS 3y, Microsoft 1y, Fundamentals never, all [opened]). Course completion is a weak signal (MOOC median completion 12.6%, [snippet]). A certificate says "passed an exam on date D", not "holds skill X today".
- Regulation shapes design: employment AI is Annex III high-risk under the EU AI Act [opened], DPDP s7 gives an employment ground [snippet], German works councils can block rollout [snippet], NYC LL144 needs bias audits [snippet]. Keep explanations, source quotes and swap tests (S1.3.7) as first-class outputs.

## 2. DOs and DON'Ts

DO
1. DO require a verbatim quote span for every claimed skill, because CV lies and LLM-written CVs make unquoted claims untrustworthy (F01, F04).
2. DO weight evidence by source reliability class (assessment > verified cert > work system > HCM > CV self-claim), because self-rating validity is about r = .29 (F29).
3. DO join identities on a stable key (employee ID plus verified email history), never on name alone, because common names collide and marriage changes names (F18-F23).
4. DO strip bots, auto-merges and release-manager merges before counting GitHub activity, because they attribute work to the wrong person (F10-F12).
5. DO treat "Co-authored-by" and pair-programming credit as partial authorship, because the trailer only counts when the email matches (F13).
6. DO apply a recency decay per skill family, with faster decay for fast-moving stacks, because skills lost about half of gains in 6.5-13 months of non-use ([snippet] F28).
7. DO check certificate validity dates and renewal state at the "as-of" date, because certs expire (F24).
8. DO abstain when the only evidence is one CV mention, a keyword list, or a course completion, because these are the cheapest and most inflated signals (F05, F26).
9. DO discount resume text that is generic or template-like, because LLM-written CVs make boilerplate skill lists common (F04).
10. DO run name, gender and university swap tests on the frozen set, because women under-rate themselves and any self-report-derived signal will carry that gap (F30, S1.3.7).

DON'T
1. DON'T credit a skill because a certificate "requires" it, because the cert proves an exam pass on a date, not current use (F25).
2. DON'T read CV length or bullet count as depth, because Indian "Roles & Responsibilities" CVs pad bullets (F06, S1.1 level row).
3. DON'T treat the HCM job title as truth, because titles lag, inflate, and differ by acquisition (F19, F20).
4. DON'T count a ticket close as individual skill evidence, because leads close tickets and tickets get reassigned (F14, F15).
5. DON'T use ServiceNow L1 resolution notes as skill proof, because they are copy-paste templates (F17).
6. DON'T treat Salesforce deal ownership as sole credit, because splits and overlay roles share the same deal (F33).
7. DON'T infer absence of a skill from empty GitHub, because private repos and enterprise accounts are invisible (F09).
8. DON'T use a yes/no confirmation prompt as ground truth, because acquiescence makes people say yes (F32).
9. DON'T store or display more personal data than the explanation needs, because DPDP and GDPR purpose limits apply (section 4).
10. DON'T ship a high-confidence label with no stated evidence path, because EU AI Act and LL144 expect explainability and audit (section 4).

## 3. Fault catalog

Prevalence column: number, source label. "Assumed" means no source; set by us.

| ID | Fault | Source system | Real-world prevalence | S1.1 row | How to plant it |
|---|---|---|---|---|---|
| F01 | CV states skill never used or never held | CV | India: 17% resume mismatch white-collar (AuthBridge H2 2025, [opened] cxotoday); IT/ITES misrepresented resumes 18.8% [opened] | Skill not really held | 15-20% of CVs get 1-3 skills listed with no usage context anywhere else |
| F02 | Employment history discrepancy (dates, employer, designation) | CV vs HCM/BGV | 13% employment-check discrepancy white-collar [opened]; BFSI 29% employment misrepresentation [opened]; HireRight APAC employment verification issues 72% of employers report seeing them [snippet] | Level off | Shift one tenure by 6-18 months, or inflate title by one band in ~13% of personas |
| F03 | Education discrepancy / fake or unverifiable degree | CV, certs | 5% white-collar education discrepancy [opened]; telecom 6.7% fake or unverifiable [opened]; HireRight India 2014-15: 23% of 218,427 checks with discrepancy, 52% of those education [opened] | Not really held | 4-6% of personas have a degree that fails verification; the skill claim then rests only on the CV |
| F04 | LLM-written CV: polished, generic, keyword dense | CV | 46% of job seekers used ChatGPT on resumes/cover letters (Resume Builder 2023, quoted in SHRM [opened]); 31% of liars used AI (AI Resume Builder, [snippet]); LinkedIn applications +45%, 11,000/min (NYT, [snippet]) | Not really held / level off | 40% of 2024-26 CVs get uniform LLM style: skill list of 20+ items, no dates per skill, verbs like "leveraged" |
| F05 | Keyword stuffing / skills-section bloat | CV | Assumed (no primary number found) | Not really held | Skills section 25-60 items, 60-80% never appear in experience bullets |
| F06 | Indian CV convention noise: "Roles & Responsibilities" lists, CGPA/percentage, declaration line, photo/DoB/marital status, "Technical Skills: MS Office, Internet" | CV | Convention, no prevalence number | Invented / message misread | Template block with the declaration line and generic skills; R&R bullets describing team duties not personal work |
| F07 | Moonlighting / dual employment hides real time on tasks | CV, HCM | 12% discrepancy in 150k+ moonlighting checks FY24 (AuthBridge 2024 trends, [snippet]); IT dual employment 5% / 4.99% [opened] | Wrong person / level off | 4-5% of personas have a second concurrent employer on CV with overlapping dates |
| F08 | Overclaim of AI skills specifically | CV | Nearly half of 2023 job seekers exaggerated AI skills (Resume Builder via HR Dive, [snippet]) | Not really held | "Generative AI", "LLM" on CV with no work artifact; common in post-2023 CVs |
| F09 | Private-repo invisibility | GitHub | Count not available. GitHub shows only daily counts for private contributions if the user publicizes them [opened docs] | Not really held (false negative) | Strong engineer with near-empty public GitHub; evidence lives in Jira only |
| F10 | Bot commits/PRs counted as person (dependabot, renovate) | GitHub | Bot PRs ~13.3% of sampled PRs (LinearB, [snippet]); older academic estimate ~1/3 of PRs from bots, with merge 37% vs 72% for humans (BotSE 2021, [snippet]) | Wrong person | 10-15% of PRs in a repo are bot-authored; merged by a human who is then credited |
| F11 | Squash merge / maintainer merge credits the merger or erases per-commit authors | GitHub | No prevalence number. GitHub counts only commits on default branch; rebase credits both original author and rebaser [opened docs] | Wrong person | A senior merges 60% of a juniors' squashed PRs under one commit author |
| F12 | Release manager / tech lead merges others' PRs | GitHub | Assumed | Wrong person | One persona has high merge count, near-zero authored code |
| F13 | Co-authored-by / pair programming credit | GitHub | Credit only if the email is linked to the account [opened docs] | Wrong person | Commit has two trailers; one email is personal and unlinked, so one person is invisible |
| F14 | Ticket reassigned; final assignee did little | Jira | Assumed | Wrong person | Ticket has 3 assignee changes; changelog shows who wrote the comments and code links |
| F15 | Tickets closed by leads / bulk-closed at sprint end | Jira | Assumed | Not really held | 20% of a lead's closures are for tickets they never touched |
| F16 | Vague summaries and component misuse ("Fix bug", component = "General") | Jira | Assumed | Wrong mapping / message misread | 30% of tickets have summaries under 4 words; component not matching the real stack |
| F17 | L1 copy-paste resolutions, auto-routed incidents | ServiceNow | Assumed | Not really held / wrong person | Resolution note identical across 50 tickets; assignment by routing rule, not skill |
| F18 | Name collision (same name, different person) | Join across systems | Kumar ~1.23%, Sharma ~1.15%, Patel ~1.09%, Singh ~1.07% of surnames in one census-attributed table [snippet, non-primary]; other sites disagree (Singh 34.8M bearers, Forebears-based, [snippet]); "Rahul"/"Priya" frequency not found [none] | Wrong person | Create 2-5 employees named "Rahul Kumar" / "Priya Sharma" across 3 departments with different skills |
| F19 | Stale job title in HCM | HCM | Practitioner claim "8-12% of records inaccurate" has no study behind it [snippet, unverified] | Level off | Title still "Associate" 18 months after real promotion, or still "Developer" after moving to management |
| F20 | Title inflation / different grade systems after acquisition | HCM | Assumed | Level off | Acquired-company staff keep "Senior Manager" that maps to mid-level in parent |
| F21 | Contractor vs employee IDs; same person two IDs | HCM | Assumed | Wrong person | A contractor converts to FTE; old Jira/GitHub activity sits under the contractor ID |
| F22 | Name/email change after marriage or legal change | HCM, GitHub, email | Rehires, name changes and legacy migrations are noted causes of duplicates (MangoApps checklist, [snippet]); no rate | Wrong person | Post-marriage surname change; GitHub commits under old email stay unlinked |
| F23 | Duplicate employee records | HCM | 29% of organizations don't know their duplicate rate (landbase, vendor blog, [snippet]) | Wrong person | 2-3% of persons have two HCM rows (rehire, legacy ID) |
| F24 | Expired certification presented as current | Certs | AWS valid 3y, renewable; maintenance adds 1y [opened]; Microsoft role-based valid 1y, free renewal, Fundamentals never expire [opened]; GCP/CKA/PMP periods not verified [none] | Skill decay | Cert issued 4 years ago with no renewal in a person's CV and LMS |
| F25 | Cert or course "requires skill X" credited as skill X | Certs, LMS | Logic fault, no rate | Wrong mapping | Cert on "Azure Fundamentals" mapped to Azure administration at expert level |
| F26 | Course completed without learning | LMS | MOOC completion median 12.6% (Jordan 2015, [snippet]); those who finish may still learn little [none] | Not really held | LMS rows show "completed" with 3-minute duration, and no later use in work systems |
| F27 | Fake, purchased, or unverifiable certificate | Certs | GAO 2004: 463 federal employees held bogus degrees [snippet]; 76% of employers assume docs are genuine without verifying (older UK study, [snippet]); telecom fake/unverifiable credentials 6.7% [opened] | Invented skill | 3-5% of cert rows with no Credly/issuer verification URL or an invalid ID |
| F28 | Skill decay: skill last used years ago | CV, work systems | Gains lost by about half after ~6.5 months (accuracy), 13 months (speed) of non-use (2025 Psych Bulletin meta, [snippet]); d up to -1.4 after 365+ days nonuse for cognitive tasks (Arthur et al. 1998, [snippet]) | Skill decay | Java commits stop in 2018; CV still lists it as "expert" |
| F29 | Self-assessment poorly tracks ability | Self-report survey | Mean r ≈ .29 across 22 meta-analyses (SD .11) [snippet]; domain-specific higher | Level off | Self-ratings = true level + noise SD ~1 level; correlation ~.3 with measured |
| F30 | Gender gap in self-rating | Self-report | Equally performing women rate themselves lower than men (Exley and Kessler, QJE 2022, 4,000+ participants) [snippet]; effect size not obtained [none] | Level off | Apply a fixed negative offset to female personas' self-ratings, same evidence |
| F31 | Overclaiming (familiarity with nonexistent items) | Self-report, CV | Paulhus overclaiming technique uses fictitious foils; validity debated: Tonkovic et al. 2011 (N=382) correlates with impression management [snippet] | Invented skill | Some personas claim familiarity with fake tools in a skills checklist |
| F32 | Acquiescence on yes/no confirmations | Employee survey (message step) | Called the most prevalent response bias in surveys (Steinmetz and Posten citing Baumgartner and Steenkamp 2006, [snippet]); up to 50% inflation of belief prevalence in one study [snippet] | Message misread | Simulate employee reply: 15% say yes to any statement regardless of truth (assumed rate) |
| F33 | Salesforce credit splits and overlay roles | Salesforce | Assumed | Wrong person | Deal has AE (60%), SE overlay (20%), CSM (20%); skill "negotiation" credited to wrong one |
| F34 | Confluence authorship vs real author (page created by PM, content by engineers; edits by templates) | Confluence | Assumed | Wrong person | Page creator differs from 80% of content editors |
| F35 | HR job-family labels not matching actual work (title says QA, work is data engineering) | HCM vs work | Assumed | Wrong mapping | Title "Test Engineer" with PRs in pipelines |
| F36 | Mirrored/forked repos and monorepos inflate or blur activity | GitHub | Commits made in forks do not count toward profile contributions [opened docs] | Wrong person / wrong mapping | A fork has 400 commits mirrored from upstream; monorepo spans 6 stacks but one person owns one folder |

Honesty note on prevalence: "Assumed" rows (F05, F12, F14-F17, F19-F21, F33-F35) have no source. Do not cite them as real. Ask the hiring/IT teams at iMocha customers for actual rates, or sample real Jira/ServiceNow exports.

## 4. Regulatory constraints (short)

- **EU AI Act.** Annex III point 4 lists AI for recruitment or selection and for decisions on work relationships, promotion, task allocation and monitoring/evaluation of workers as high-risk [opened, artificialintelligenceact.eu]. Obligations were due 2 Aug 2026; the Digital Omnibus agreement moves Annex III to 2 Dec 2027 [snippet, law-firm summaries; confirm Official Journal text]. Implication: keep logs, human oversight, accuracy records, per-decision evidence trace.
- **India DPDP Act 2023.** Section 7 allows processing for employment purposes without consent [snippet]. Rules notified Nov 2025, main obligations phased in (one source says May 2027) [snippet, unverified]. No GDPR-style legitimate interest ground, so purposes beyond employment need consent or notice. Penalties up to 250 crore per breach quoted [snippet, unverified]. Implication: process only needed fields, document the employment purpose, retain minimally.
- **German works councils.** Section 87(1) No. 6 BetrVG gives co-determination over IT systems able to monitor behavior or performance; courts read it broadly, though a Hamburg labor court ruling on ChatGPT went narrower [snippet]. Implication: German customers likely need a works agreement before rollout; offer aggregate, non-surveillance framing and a data-flow document.
- **NYC Local Law 144.** Independent annual bias audit of automated employment decision tools, public summary of results, candidate/employee notice, daily violations, private right of action [snippet]. I could not confirm the 10-business-day notice or penalty amounts [unverified]. Implication: log selection rates by sex and race/ethnicity categories; inference tied to hiring or promotion triggers LL144.
- **What this implies for data and explanations.** (1) Show the source quote and system for each skill. (2) Never use protected attributes as inputs, but keep them in audit data. (3) Support employee correction, which doubles as the accuracy loop. (4) Do not use inferred skills for promotion or dismissal decisions in these regimes without the human oversight and audit steps above.

## 5. Sources

Opened and read (fetched page content):
- https://www.peoplematters.in/amp/article/background-verification/hirerights-latest-study-reveals-resume-fraud-india-11343
- https://cxotoday.com/press-release/authbridge-exposes-indias-hiring-red-flags/
- https://cxotoday.com/media-coverage/1-in-5-it-resumes-misrepresented-telecom-reports-11-hiring-discrepancies/
- https://www.shrm.org/mena/topics-tools/news/technology/how-to-spot-ai-generated-lies-on-a-resume
- https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors
- https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference
- https://aws.amazon.com/certification/recertification/
- https://learn.microsoft.com/en-us/credentials/certifications/renew-your-microsoft-certification
- https://artificialintelligenceact.eu/annex/3/

Search-result summaries only (primary page not opened; numbers are unverified):
- HireRight 2025 benchmark: https://hrreview.co.uk/hr-news/recruitment/nine-in-ten-of-employers-find-discrepancies-during-candidate-screening (fetch returned 403); businesswire release 403.
- AuthBridge Annual Trends Report 2024 PDF: https://authbridge.com/wp-content/uploads/2024/10/AuthBridges-Annual-Trends-Report_2024.pdf (fetch returned 403); First Advantage India Trends Q1 (9.59% overall, secondary).
- Resume lies surveys: https://www.hrdive.com/news/younger-workers-lying-on-resumes-got-the-job/749478/ ; https://www.monster.com/career-advice/research/credibility-gap
- Self-assessment meta-analyses and Dunning-Kruger: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8883889/ ; https://core.ac.uk/download/345080337.pdf
- Exley and Kessler: https://www.nber.org/digest/dec19/w26345.shtml ; https://academic.oup.com/qje/article-pdf/137/3/1345/44839891/qjac003.pdf
- Paulhus overclaiming: https://paulhuslab.psych.ubc.ca/research/overclaiming/
- Skill decay: https://Www.Gwern.net/doc/psychology/spaced-repetition/1998-arthur.pdf ; https://pubmed.ncbi.nlm.nih.gov/40455501/
- MOOC completion: https://www.irrodl.org/index.php/irrodl/article/view/2112/0
- Acquiescence: https://openaccess.city.ac.uk/id/eprint/24609/3/Steinmetz26Posten_revised.pdf ; https://margaretroberts.net/wp-content/uploads/2021/10/hillroberts_acqbiaspoliticalbeliefs.pdf
- Bots in PRs: https://assets.linearb.io/image/upload/v1727274292/Bot_Automation_Report.pdf ; https://2021.icse-conferences.org/details/botse-2021/botse-2021-papers/2/Bots-Don-t-Mind-Waiting-Do-They-Comparing-the-Interaction-With-Automatically-and-Ma
- Credential fraud: https://shrm.org/topics-tools/news/hr-magazine/fraud-factories ; https://learn.credly.com/blog/faqs-exploring-the-role-of-digital-credentials-in-fraud-prevention
- AI application volume: https://fortune.com/2025/11/18/hiring-job-seekers-recruiters-talent-acquisition-ai-doom-loop-application-technology/ ; https://www.semafor.com/article/06/24/2025/recruiters-swamped-with-ai-generated-job-applications
- HR data quality: https://www.mangoapps.com/templates/inspections/hris-data-integrity-audit-checklist ; https://www.qureos.com/glossary/hris (unsupported claim)
- Surnames: https://surnam.es/most-common-surnames-in-india ; https://www.wionews.com/web-stories/trending/7-most-common-surnames-in-india-1686738402044
- Regulation: https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines/ ; https://www.dpdpa.com/dpdpa2023/chapter-2/section7.html ; https://www.barandbench.com/view-point/from-consent-to-compliance-navigating-the-implications-of-dpdp-act-on-employment-practices ; https://roedl.com/insights/ki-systeme-arbeitsverhaeltnis-betriebsrat ; https://perkinscoie.com/en/news-insights/nyc-adopts-final-rules-for-law-governing-automated-employment-decision-tools.html

Not found at all (no number given): GCP, CKA, PMP validity periods; HCM error rates from a primary study; "Rahul Kumar"/"Priya Sharma" counts; Jira/ServiceNow/Salesforce/Confluence fault rates; Mabe and West 1982 original (secondary only); size of Exley-Kessler gap; SpringVerify data; Naukri CV-format prevalence.
