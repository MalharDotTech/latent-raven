# 04 - Data sourcing: legal input data and ground truth for 10-30 people in <24h

Date: 2026-11-05. Deadline: Fri 6 Nov 12:00 IST. Items marked (unverified) come from my background knowledge, not a page I opened.

## 1. TL;DR

- **LinkedIn verdict:** do not scrape iMocha employees' LinkedIn. It breaches LinkedIn's User Agreement, LinkedIn is actively suing scrapers, and it is personal data of identifiable people collected without their consent, so the downside outweighs a one-day shortcut.
- **Safe replacement for "real" people:** ask 5-10 iMocha-adjacent or friendly volunteers to donate a CV plus a public GitHub handle, in writing, and use their own self-rating as the label. Consent turns the legal problem into a form.
- **Core of the demo is synthetic:** 24 generated personas with a hidden ground-truth (skill, level, last-used) and artifacts derived from it, with traps planted per the S1.1 error budget. Labels exist before the inferrer sees anything, so the eval is honest by construction.
- **Taxonomies are free today:** ESCO and O*NET for mapping, SFIA 7 levels as the customer-scale example, Lightcast Open Skills for demo only (commercial use needs a licence).
- **Time:** about 9-11 working hours for the full recipe in section 4; the synthetic set alone is about 5.

## 2. Legal and ToS read (LinkedIn)

- **User Agreement (unverified, from memory):** it prohibits scraping and automated collection of member data, and fake accounts. This is a contract term, not a statute. Breach alone is enough for LinkedIn to act.
- **hiQ v. LinkedIn:** the 2019 Ninth Circuit ruling said scraping public pages is generally not a CFAA violation, but the Supreme Court vacated it in light of Van Buren. The court then found hiQ breached the User Agreement (scraping plus fake profiles). It ended Dec 2022 with a consent judgment: stop scraping, destroy data and derived code and algorithms, reportedly $500,000. So "public data is fair game" lost on contract grounds, and the remedy included destroying models built on it. Not binding precedent, per the Morgan Lewis and ZwillGen write-ups.
- **Proxycurl:** LinkedIn sued in Jan 2025 (fake accounts, scraping). Proxycurl shut down on 4 Jul 2025 and the founder cites the cost of fighting. Successors either dropped LinkedIn (NinjaPear) or remain LinkedIn-only (reported, Enrich Layer). Any third-party "LinkedIn API" in 2026 carries the same exposure and you would be the one holding the data.
- **India DPDP Act 2023 / Rules 2025:** Rules notified 13-14 Nov 2025. Section 3(c)(ii) excludes personal data the person made public themselves, but it is not a blanket licence: commentary says inference, profiling and commercial use are not expressly cleared. One source says the relevant provisions only bite from about 13 May 2027 (not confirmed against the gazette). Either way, profiling named iMocha employees for a pitch, with no notice, is the exact fact pattern a lawyer will flag. Also a trust problem: the demo is for a company whose staff would be the subjects.
- **Risk read:** legal risk is moderate for a one-off, but reputational risk with the buyer is high and the gain is small (N=10-30 profiles that carry no proficiency ground truth anyway). LinkedIn gives claims, not truth. Skip it.
- **Safer ladder:** (1) consent-based donation, (2) public GitHub only via the official API (GitHub's ToS permits API use within rate limits; do not harvest emails), (3) self-donated profile PDFs ("Save to PDF" by the owner), (4) synthetic personas. Use 1 + 4 for the demo.

## 3. Dataset table

| Dataset | What it has | License | Usable for | Link |
|---|---|---|---|---|
| Kaggle Resume Dataset (snehaanbhawal) | ~2,400 LiveCareer resumes (text + PDF), category labels | Unclear on mirrors; check Kaggle page. Scraped from LiveCareer, so treat as research-only | Extraction (CV parsing realism); no skill levels | https://baselight.app/u/kaggle/dataset/snehaanbhawal_resume_dataset |
| CareerCorpus | Annotated version of those resumes | CC-BY-4.0 | Extraction eval (span labels) | https://data.mendeley.com/datasets/wzzwn37gmd/1 |
| HF PROFESSORSAM25/resumes | Token-classification resumes, real + synthetic mix | MIT (per card) | Extraction | https://huggingface.co/datasets/PROFESSORSAM25/resumes/blob/main/README.md |
| ResumeBench (EMNLP 2025) | 2,500 synthetic resumes, 50 templates, 30 fields, 5 languages, built for parsing eval | Check paper/repo | Extraction, template for synthetic design | https://preview.aclanthology.org/setup/2025.emnlp-main.1626 |
| RJDB (arXiv 2311.06383) | 50k+ GPT-4 job description / resume / skill triples from a skill-occupation graph | Check repo | Skill mapping, synthetic method | https://arxiv.org/pdf/2311.06383v1.pdf |
| SkillSpan (NAACL 2022) | 14.5K sentences, 12.5K hard/soft skill spans from job postings | Repo shows no licence in my results; cite paper, confirm before redistributing | Extraction (STEP-1 span finder) | https://github.com/larkinbb/SkillSpan |
| JobSkape | Synthetic job postings for skill matching | Open-source (confirm) | Mapping, synthetic method | https://preview.aclanthology.org/setup/2024.nlp4hr-1.4 |
| ESCO | EU skills/occupations taxonomy, multilingual, no proficiency scale | Open, attribution (unverified) | Taxonomy (STEP-2) | https://esco.ec.europa.eu |
| O*NET | US occupations with skill importance and level ratings (0-7 scale) | CC BY 4.0 (unverified) | Taxonomy, level priors | https://www.onetcenter.org/database.html |
| Lightcast Open Skills | 33k+ skills, free API; Wikipedia-derived text is CC BY-SA | Free for individual / non-profit with attribution; **commercial use needs licence** | Taxonomy for demo only | https://docs.lightcast.io/lightcast-api/docs/free-api-access |
| SFIA | 7 responsibility levels, skill descriptions | Free to view, commercial use licensed (secondary source; verify) | Customer-scale example for the level ladder | https://sfia-online.org |
| Public GitHub (REST API) | Repos, PRs, languages, commit dates for consenting or famous OSS maintainers | GitHub ToS; code carries its repo licence | Evidence source (STEP-1 PRs) | https://docs.github.com/rest |
| Stack Exchange dump | Q&A with votes, tags, user ids | CC BY-SA (2.5/3.0/4.0 by date); official dump now behind login and AI-training restriction; community dump to 2026-03-31 exists | Evidence-style text with tag-level skill signal; attribution required | https://huggingface.co/datasets/flymin/stackexchange_20260331 |
| Credly / Open Badges | Public badge page with skills, criteria, Verify box; accepts OB 2.0/3.0 | No documented public API; scraping tools are unofficial | Cert verification demo using 2-3 badges you own or donors share | https://learn.credly.com/blog/credly-supports-open-badge-3.0 |

Caveat: none of these has per-person proficiency ground truth. Real labels only come from SFIA-style rubrics, assessments, or donors. That is why section 4 is synthetic.

## 4. Synthetic eval recipe (traps mapped to S1.1)

Related work worth stealing: an arXiv hiring-pipeline paper builds PII-free synthetic resumes with a **claim sheet** (atomic facts, typed) plus an **absence list** of plausible but false items as fabrication traps (https://arxiv.org/pdf/2608.26171, title seen in search only, not opened). ResumeBench and RJDB show template-driven generation from a skill graph.

**Honest-eval rules**

- Two-stage generation. Stage A writes the hidden persona: `{person_id, skills: [{skill, level_SFIA_or_customer_scale, last_used, held: bool}], role, tenure}`. Stage B renders artifacts from Stage A only. The inferrer never sees Stage A.
- Different model or different prompt family for the generator vs the inferrer, and strip generator tells (no "Level 4" words, no labelled templates, vary format, typos, locale of names).
- Freeze a held-out split of 8-10 personas before you tune any threshold. Report on held-out only. Tune on the rest.
- Artifacts encode level through behaviour (review comments, design scope, PR size and spread, incident ownership), not through adjectives.
- Calibrate realism against 3-5 real donated CVs and the Kaggle set (sentence length, section order).
- Disclose in the demo: synthetic, with known limits. Say the 95% number is not claimed on synthetic data; it is a pipeline sanity check.

**Trap map (S1.1 rows)**

| S1.1 cause | Planted trap | Ground truth | Pass condition |
|---|---|---|---|
| Invented skill | Add a skill to the CV whose evidence quote does not exist in any source, plus an LLM-bait near-synonym | Not held | Zero claims with failed string match; invented skills never sent |
| Wrong person | Two "Priya Sharma" with different employers/cities; one CV and one PR set that belong to the other | Joined only to correct id | Identity join refuses the ambiguous pair, no cross-contamination |
| Wrong skill mapping | "Spark" in a Spark AR job, "Go" the verb, "R", "Swift" in a banking context, "Excel" as a generic skill | Mapped to correct taxon or dropped | Mapping test set accuracy |
| Skill not really held | Skill listed once in a skills blob, no work evidence | held=false | Withheld |
| Skill decay | Java at SFIA 5 in 2015-2017, none since; Python continuous | last_used set | Decay rule drops or downgrades Java |
| Level two or more off | Padded 6-page CV for a junior vs terse 1-page CV of a staff engineer; certificate-only claimant | Level set in Stage A | Level within 1 and exact-match tracked; length not a feature |
| Message misread | Not testable synthetically | - | Needs real pilot (out of scope for demo) |

Also seed guard-metric cases (S1.3): generic skills (email, MS Office) and a flatterer who overstates (self-rating minus truth).

## 5. Recommended 24h data plan

Cohort: 24 synthetic personas + 6 consented real-ish profiles = 30. Sources per person: CV (all), GitHub-style PR/commit log (about 70%), Jira-style tickets (about 50%), certificates (about 40%, 2 with real Credly pages), Teams/Slack snippets (optional). Labels: 3-6 skills per person, level on the customer's scale (use SFIA 1-7 or a 5-level mapping), `held`, `last_used`.

| Block | Hours | Output |
|---|---|---|
| 1. Freeze schema, level scale (SFIA-derived), skill list (ESCO/Lightcast subset, 40 skills) | 1.0 | `schema.json`, `skills.csv` |
| 2. Stage A persona generator + trap injector (script, seeded) | 2.0 | `truth/personas.jsonl` (hidden, separate dir) |
| 3. Stage B renderers: CV (3 templates, PDF + text), PRs, tickets, certs, with trap overlays | 3.0 | `artifacts/<person_id>/*` |
| 4. Spot-check 6 personas by hand, fix leaks (grep for "Level", skill names in file names) | 1.0 | leak report |
| 5. Consent flow: send message to 6-10 volunteers (CV + GitHub handle + self-rating of 3 skills, written yes). Use only public GitHub API | 2.0 elapsed, 0.5 effort | 4-6 real profiles with self-labels |
| 6. Split: 16 tune / 8 held-out (mix of traps), freeze with a hash of the truth file | 0.5 | `split.json` |
| 7. Eval harness: precision of sent claims, trap catch rate per S1.1 row, exact and +-1 level, spread | 1.5 | one-page table for the demo |

Total about 9-11 hours of effort, with the consent step running in parallel. If time slips, drop real donors and tickets first; keep CV + PRs + traps.

## 6. Sources opened (via search; pages not individually fetched)

- https://nubela.co/blog/goodbye-proxycurl/
- https://www.socialmediatoday.com/news/linkedin-wins-legal-case-data-scrapers-proxycurl/756101/
- https://www.startuphub.ai/ai-news/startup-news/2025/the-1-linkedin-scraping-startup-proxycurl-shuts-down
- https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn
- https://www.morganlewis.com/blogs/sourcingatmorganlewis/2022/12/linkedin-v-hiq-landmark-data-scraping-suit-provides-guidance-to-data-scrapers-and-web-operators
- https://www.zwillgen.com/alternative-data/hiq-v-linkedin-wrapped-up-web-scraping-lessons-learned/
- https://www.natlawreview.com/article/linkedin-s-data-scraping-battle-with-hiq-labs-ends-proposed-judgment
- https://www.india-briefing.com/news/india-dpdp-act-publicly-available-personal-data-46899.html/
- https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf
- https://www.mondaq.com/india/data-protection/1708434/operationalising-indias-data-protection-regime-analysing-the-newly-notified-dpdp-rules-2025
- https://arxiv.org/abs/2204.12811 (SkillSpan)
- https://docs.lightcast.io/lightcast-api/docs/free-api-access and https://legal.lightcast.io/lightcast-legal/open-terms-of-use
- https://data.mendeley.com/datasets/wzzwn37gmd/1
- https://huggingface.co/datasets/PROFESSORSAM25/resumes/blob/main/README.md
- https://preview.aclanthology.org/setup/2025.emnlp-main.1626
- https://arxiv.org/pdf/2311.06383v1.pdf
- https://arxiv.org/pdf/2402.03242 (JobSkape)
- https://arxiv.org/pdf/2608.26171
- https://www.devclass.com/development/2024/07/30/stack-exchange-restricts-access-to-dump-of-user-contributed-data-critics-complain-this-contradicts-license/1625192
- https://learn.credly.com/blog/credly-supports-open-badge-3.0
- https://apify.com/crawlerbros/credly-badge-scraper (unofficial)

Not verified: LinkedIn User Agreement text, ESCO/O*NET/SFIA licence pages, GitHub ToS, DPDP gazette dates. Check these before any external claim.
