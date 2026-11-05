---
title: Vendor landscape - skill and proficiency inference
lane: commercial vendors
date: 2026-11-05
for: CTO meeting, iMocha, Fri 6 Nov 2026 12:00 IST
---

# 01 - Vendor landscape: who infers skill + proficiency from multi-source evidence

Evidence grade: **P** = primary vendor doc opened, **M** = vendor marketing page opened, **S** = secondary/search snippet only (not verified; do not quote in the meeting). The iMocha PDF is marked Confidential/NDA; use internally only.

## 1. TL;DR

- Everyone infers **presence** (a skill is on the profile) from text and system signals. Almost nobody publishes how they infer **level**, and nobody publishes a **precision** number measured against employee agreement.
- The only "accuracy" figures found are marketing: Beamery "up to 90% accuracy" / "90% relevance on first review" (undefined metric), TechWolf "85%+ approval" (S), Microsoft "~80%" (S, unverified). All are weaker than, and measured differently from, a 95% Yes bar.
- The dominant validation pattern is "show the suggestion, let the employee accept or reject" (Microsoft, TechWolf, SAP, Workday). Rejection rate is their quality metric (Microsoft says so explicitly). Nobody gates what is sent by an evidence rule.
- iMocha's own engine maps a 0-100 weighted confidence score straight to a proficiency band (20-39 Beginner ... 80-100 Proficient). That conflates "how sure are we" with "how good is the person". WorkRaven's separate band vs level (STEP-4.8) fixes this.
- Differentiation: published stance of "send only High, independent-group evidence, abstain otherwise, measure Yes rate with guard metrics (flattery, slices)". No vendor documents abstention as a product contract or checks levels against assessments to detect flattery.

## 2. Comparison table

| Vendor | Sources read | Presence method | Proficiency method | Confidence / abstain | Validation loop | Public accuracy claim | Link (grade) |
|---|---|---|---|---|---|---|---|
| iMocha Skills Intelligence (existing) | Resume/LinkedIn/HR profile, certs (Credly etc.), LMS, Jira/GitHub, AI interview, manager rating | NLP to 25k+ skill taxonomy via semantic similarity; cert-to-skill dictionary | Confidence 0-100 mapped to 4 bands (Beginner/Intermediate/Experienced/Proficient); decay half-lives 6-36 months | 0-100 additive score, configurable weights (Certs 25, Projects 25, AI Interview 20, Learning 10, Manager 10, Resume 10); unrecognised certs flagged, not inferred; no send-threshold abstention documented | Manager endorse/flag, HR override, employee dispute to human review | None quantitative; "explainable, no black box" | iMocha AI Inference Engine PDF (P, NDA) |
| Microsoft People Skills (ex Viva Skills; LinkedIn Skills Graph) | M365 Graph: documents, emails, chats, meetings, profile, job title, top contacts; last 90 days only; M365 only | LLM assigns closest taxonomy skills to profile+activity; LinkedIn Skills Graph used as taxonomy | No level documented | No score exposed; AI-restricted (sensitive) skills blocked | User edits/confirms; confirm/reject rates tracked as quality metric; 30-day refresh | "accurate in aggregate"; no number (a secondary report says ~80%, S) | learn.microsoft.com people-skills-ai-inferencing and data-and-ai-guidelines (P) |
| TechWolf | HRIS, job architecture, LMS, performance data, Jira/GitHub/Salesforce/Slack-type work systems; external labour data | AI models over work-system text, mapped to taxonomy (incl. Workday Skills Cloud) | Claimed ("infers proficiency levels"), method not published | Not exposed; "nothing lands on a profile unreviewed" | Employee accept/reject in Teams/Slack; job-owner review console | None on its pages; "85%+ approval" in a Teams marketplace listing (S) | techwolf.ai Workday FAQ, blog (M) |
| Workday Skills Cloud | Learning courses, projects, job history, anytime feedback, skills on profile; not certifications | Hourly suggestion job (up to 10 skills per source) from text + history | Calculated level 1-5 (Beginner..Expert) from source weights set by admin; needs self/peer ratings enabled | No confidence shown; skill "sources" shown as validation | Worker adds evidence; endorsements; self/peer ratings | None | doc.workday.com types-of-skills (P) |
| Gloat (Skill Validation Agent) | Work output, projects, peer endorsements, assessments, certs, manager observations; soft skills from collaboration patterns and meeting dynamics | Matches skills to work evidence (demo: 40% verifiable) | Confidence 1-5 per validated skill; adaptive micro-assessments | 1-5 score, "multiple evidence types score higher"; formula unpublished | 5-minute micro-assessments 2-3x/week; continuous update | None on accuracy; demo stats only (23% of self-reported skills "overstated") | gloat.com skill-validation-agent (M) |
| Eightfold | Resume text, public profiles, similar-career peers, job descriptions; assessments write proficiency | Deep-learning inference incl. "Likely skills" from title+company | Via skill assessments / peer input (community post); no scale in article | Four buckets: Validated, Likely, To Validate, Missing; threshold adjustable (S) | Recruiter/interviewer probe "to validate" skills | "highly accurate and reliable", no number | eightfold.ai skills validation article (M) |
| Lightcast (Open Skills / Skills API) | Free text submitted (job ads, resumes) | Entity extraction to 33k+ skills | None (taxonomy only) | Per-skill `confidence` 0-1, `confidenceThreshold` default 0.5, trace with matched text offsets | None built in | No vendor number; Nesta study: ~12% false positives per job ad for Lightcast vs ~27% average across tools (S, small sample) | docs.lightcast.io skills extract (P); Nesta pipeline page (S) |
| Beamery | Role/job data, candidate and employee profiles | Proprietary inference engine over roles | "proficiency levels" claimed on AI page; not in release | Not exposed | Not described | "up to 90% accuracy"; "90% relevance on first review" (metric undefined) | beamery.com job architectures release (M) |
| SAP SuccessFactors | HR profile/performance goals text; ontology (Emsi/O*NET lineage) | ML skill inference; new skills added to Attributes Library for admin confirmation | Employees add and rate; little documented | None documented | Employee reviews/rates suggestions; admin confirms new skills | None | sap.com skill inference pages (S) |
| Cornerstone Skills Graph | Profiles, job descriptions, LMS | AI/ML detection over 50k+ skills | Self-rating plus peer ratings | Not documented | Peer ratings | None | cornerstoneondemand.com press release (S) |
| Degreed, Fuel50 | Learning activity (Degreed); expert-curated ontology with proficiency descriptions (Fuel50) | n/a verified | Degreed "tracks proficiency" (S); Fuel50 level descriptions (vendor claim) | Not documented | Manager/employee rating (S) | None | not opened; low confidence |
| retrain.ai | CVs, job descriptions | Semantic extraction, 300M JD taxonomy | Not documented | Not documented | n/a | None; one low-confidence source says the company wound down in 2025 | trainingindustry.com (S) |

Gaps in this table: Eightfold, SAP, Cornerstone, Degreed, Fuel50 and retrain.ai were reached only through search or thin marketing pages; I did not find primary engineering docs or patents for them in the call budget.

## 3. Steal list (24h demo)

- **Quote-trace on every claim** (Lightcast `trace` returns matched text and offsets; iMocha PDF "explainability" list). Show the exact quote and source locator per evidence item. Improves STEP-1 (quote check) and STEP-6 ("Based on").
- **Confidence threshold as a dial, with abstain as default** (Lightcast `confidenceThreshold`; Eightfold "To Validate" bucket). Demo a slider that moves skills between Sent / Waits, with Yes-rate shown for each. Improves STEP-3 and STEP-5.
- **Four-bucket UI: Validated / Likely / To validate / Missing** (Eightfold). Map to High / Medium / Low / Disputed so HR sees why something was held. Improves STEP-3 bands.
- **Employee accept/reject as the logged quality metric, per slice** (Microsoft confirm/reject rates; TechWolf Teams assistant). Build the Teams card and the Yes-rate dashboard first; it is the proof artifact. Improves STEP-6 and STEP-7.
- **Source-weights config + decay half-lives by skill volatility** (iMocha PDF: 6/12/24/36 months). Reuse as the registry defaults for STEP-3.5 decay (WorkRaven plan uses ~2y tools / ~5y domain; align the two and say so). Improves STEP-3.
- **Exclude/sensitive skill list** (Microsoft AI-restricted skills, removed within 24h). Direct analogue of STEP-5.3 plus a sensitive list for protected-class proxies. Improves STEP-5.
- **Micro-assessment as tiebreaker for held skills** (Gloat 5-minute assessments; iMocha already owns Tara). Auto-offer a 5-minute check when evidence floor and ceiling are 3+ apart. Improves STEP-4 and the STEP-7.2 level calibration.
- **Unrecognised items flagged, not forced** (iMocha unrecognised certs rule). Same stance as STEP-2.2; demo the "new skill names" queue. Improves STEP-2.

## 4. Gaps nobody solves

- **Proficiency is the weak spot.** Microsoft, Beamery, SAP, Cornerstone publish no method. Workday's level is a weighted average of self and peer ratings, which are biased upward. iMocha's confidence-to-band mapping makes a heavily corroborated beginner look "Proficient" and a lone strong GitHub record look "Beginner".
- **No precision defined as agreement.** "Approval", "relevance on first review", "accuracy in aggregate" are undefined. None states the denominator, whether non-replies count, or whether yes-to-everything users are excluded.
- **No flattery control.** Employees rarely reject a flattering level. Only Gloat even hints at overstatement (23%, a demo number). No vendor says it calibrates level against independent assessments (STEP-7.2).
- **Abstention is implicit.** Vendors drop low scores but none publishes a coverage-vs-precision trade-off or a stop rule when a slice degrades (STEP-7.6).
- **Independence of evidence is not modelled.** iMocha's scoring is additive across sources; two correlated sources (CV and LinkedIn, commits and reviews) are not documented as counted once (STEP-3, S3.1).
- **Privacy stance is uneven and unproven.** Microsoft reads emails, chats and meetings (last 90 days). TechWolf reads work systems incl. Slack-type tools. WorkRaven's "never read email/chat" is a clean differentiator for EU works councils, but costs recall; say so.
- **Staleness of public claims.** Most pages are marketing with no method or test set; treat all vendor numbers as unverified.

## 5. Sources (opened)

- iMocha AI Inference Engine (Confidential): https://mochaworks.imocha.io/hubfs/Trust%20Center%20-%20iMocha/iMocha_AI_Inference_Engine.pdf
- Microsoft People Skills AI inferencing: https://learn.microsoft.com/en-us/microsoft-365/copilot/people-skills-ai-inferencing
- Microsoft People Skills responsible AI FAQ: https://learn.microsoft.com/en-us/microsoft-365/copilot/people-skills-data-and-ai-guidelines
- Workday types of skills / calculated proficiency: https://doc.workday.com/admin-guide/en-us/human-capital-management/skills-and-skills-cloud/skills/reference--types-of-skills.html
- TechWolf Workday FAQ: https://www.techwolf.ai/faqs/why-are-workday-skills-cloud-profiles-empty
- TechWolf blog: https://www.techwolf.ai/resources/blog/how-ai-maps-workforce-skills-without-bias
- Gloat Skill Validation Agent: https://gloat.com/use-cases-agents/skill-validation-agent/
- Eightfold skills validation: https://eightfold.ai/?p=2923
- Lightcast skills extract API: https://docs.lightcast.io/lightcast-api/reference/classification_post_release_skills_extract
- Beamery release: https://beamery.com/resources/news/beamery-unveils-job-architectures-powered-by-skills-intelligence-to-help-businesses-close-critical-skills-gaps-faster

Search-snippet only (not opened, grade S): Nesta ojd_daps_skills pipeline summary (https://nestauk.github.io/ojd_daps_skills/pipeline_summary), SAP skill inference pages (sap.com), Cornerstone Skills Graph press release, retrain.ai (trainingindustry.com), Degreed, Fuel50. Microsoft's "180-day refresh" and "~80% accuracy" snippets conflict with the opened learn page (30-day refresh); use the opened page.
