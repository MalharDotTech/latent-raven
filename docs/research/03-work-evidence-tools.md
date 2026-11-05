# 03 - Work-evidence skill inference: tools, OSS, startups

Lane: tools that infer technical skill or proficiency from work artifacts (code, PRs, reviews, tickets, docs). Researched 5 Nov 2026. Pages I did not open are marked "not verified".

## 1. TL;DR

- Nobody found publishes a validated, per-skill proficiency model built from code evidence. Commercial dev-analytics tools (Flow, LinearB, Swarmia) measure team productivity, not "Alice is Level 3 Python". The slot WorkRaven targets (evidence-traced level, employee-confirmed) is open.
- The closest commercial analogue is TechWolf: infers levels from Jira, CRM, courses and tenure, weights recent and frequent work more, traces every level to its records, and treats the inferred level as a suggestion that needs validation before it feeds matching. That is WorkRaven's STEP-3/4 plus STEP-6 loop in market form. Gloat does similar with vaguer claims.
- Workera is the counter-position: "inference is a probability, not a measurement". It combines proctored assessment with ambient inference. Expect iMocha's CTO to hold the same view, so the demo must show assessments calibrating levels (plan STEP-7.2) and not claim inference replaces measurement.
- Ownership attribution is solved only approximately. git-fame counts surviving lines; CodeScene computes "main developer" from full contribution history (not blame) and itself flags that committer-name based authorship is biased and sometimes "inconclusive". Gaming defences in assessment vendors (CodeSignal Suspicion Score, proctoring) are about test cheating. For work evidence, the anti-gaming levers are independent-group corroboration, merged-and-reviewed-by-others filters, and the employee's own "No".
- Stack Overflow reputation and GitHub language byte counts are weak proxies: reputation tracks engagement and is gamed; bytes of code measure volume, not skill. Use as Low-band hints at most.

## 2. Tool table

| Tool | Evidence read | Skill vs level | Anti-gaming | Open source? | Link |
|---|---|---|---|---|---|
| Pluralsight Flow (ex GitPrime) | Commits, PRs; Impact (LOC-derived "diff delta"), churn; added language-level analytics tied to Skill IQ | Skill by language; level comes from separate Skill IQ adaptive test, not from commits. Official Impact formula not found | Not documented (lines-based metrics are known to be gameable; source is a rival, GitClear) | No | https://pluralsight.com/product/flow/code |
| Pluralsight Skill IQ | Adaptive test, 300+ tech skills, <15 min | Measured score | Not documented | No | brandonhall PDF in sources |
| CodeSignal certified | Proctored coding assessment, Coding Score | Measured level, language-agnostic | Suspicion Score (similarity, proctoring, behaviour); 628k question variants (vendor claim) | No | https://codesignal.com/certified-assessments/ |
| HackerRank | Test-case pass, code quality; skill score | Measured | Plagiarism, behavioural monitoring, proctoring (secondary source) | No | https://designgurus.io/answers/detail/does-hackerrank-check-for-cheating |
| Karat, Turing, Arc | Not verified (search returned nothing) | - | - | No | - |
| iMocha Tara | Conversational AI interview; "structured scoring on skills and responses" via Skills Intelligence Engine; transcripts; communication score | Page documents no scale or rubric. Positioned as complementing tests: test confirms skill, Tara shows how it is deployed | No anti-cheat or proctoring stated on the Tara page; SOC 2 / ISO 27001 are security only | No | https://www.imocha.io/ai-interviewer-tara |
| TechWolf | Jira, CRM, courses, project and tenure history | Skill + level (5 default, configurable 3-8, mappable to HRIS); recency and frequency weighted; evidence trace per level; only critical skills; thin data gives "required, no confident level" | Validation by employee/SME before levels feed matching | No | https://www.techwolf.ai/faqs/what-proficiency-scale-does-techwolf-use |
| Gloat Skill Intelligence Engine | Work output, learning, peer signals | Proficiency "on a spectrum" from project complexity, peer recognition, output quality (marketing, no method) | Not documented | No | https://gloat.com/use-cases-agents/skill-intelligence-engine-agent/ |
| Workera | Proctored assessment + "Skills Inferencing System" for ambient signal | Measured on rubrics (Evidence-Centered Design); argues inference alone is only a probability | Proctoring | No | https://workera.ai/research/methodology |
| CodeScene | Full git history, not just blame | Not skill: "main developer" per file, knowledge islands, knowledge loss, "inconclusive" authorship | Robust to reformat/rename vs blame; warns committer-name bias | Core is commercial; docs public | https://docs.enterprise.codescene.io/versions/5.4.4/guides/social/knowledge-distribution.html |
| Swarmia, LinearB | PRs, reviews; Swarmia knowledge distribution from review patterns, LinearB review assignment by code ownership (comparison-blog claims, not verified on vendor docs) | Team health, not skill levels | Not documented | No | https://pensero.ai/blog/swarmia-replacements |
| git-fame | Git history | Per-author surviving LOC share (default), or ins/del; no skill | `--ignore-rev` to skip bulk reformat commits; maintainer says do not judge people on LOC | Yes (Python) | https://github.com/casperdcl/git-fame |
| gitinspector | Not verified | - | - | Yes | - |
| BuilderGraph | Public GitHub: language by bytes, frameworks from package.json/requirements.txt, commit activity | Skill list only; no levels; 0-5 job-match score (40% required skills, 25% project relevance, 15% nice-to-have, 10% activity, 10% builder type) | None described; "verified" is undefined; no LICENSE file seen | Source visible, unlicensed | https://github.com/kvadou/buildergraph |
| RepoSkillMiner (ASE 2020) | Commits, NLP, framework usage | Technology skill per developer | Research prototype | Paper | https://sites.uom.gr/a.ampatzoglou/public_html/papers/kourtzanidis2020ase.pdf |
| CORRECT (arXiv 1807.02965) | Past PRs touching external libraries/technologies | Reviewer recommendation, 85-92% accuracy on 17k PRs | - | Paper | https://arxiv.org/pdf/1807.02965 |
| Stack Overflow rep | Votes, badges | Weak expertise proxy | Gaming documented; ~60-80% of suspicious accounts later lost reputation (arXiv 2111.07101) | Data dump public | https://arxiv.org/html/2111.07101v2 |
| Skillsync (YC W26) | Captures AI coding agent sessions | Turns sessions into reusable skills; moved away from GitHub-based engineer discovery | - | No | https://yespress.io/skillsync-yc-w26.md |

No 2025-26 startup found that ships a "verified skill passport from work artifacts". Searches surfaced only BuilderGraph, Skillsync, MeshKore. Do not claim a market scan beyond that.

How the field handles your four questions:
- Recency: only TechWolf states it (recent and frequent work weighs more). WorkRaven's 24-month window and 2-year tool decay (STEP-3.5) is more explicit than anything public.
- Ownership: surviving LOC (git-fame), full-history main developer (CodeScene), reviewer recommendation by prior library use (CORRECT). None handles AI-generated code or squash-merge attribution; WorkRaven's "merged PR authored by the person, reviewed by someone else" is stricter.
- Gaming: assessment vendors proctor; work-evidence tools mostly ignore it. WorkRaven's independent-group rule plus employee veto is differentiated.
- Levels: only TechWolf and Gloat map to levels from work data. Both are vague on validation. The plan's pinned floor/ceiling logic and ≥95% bar is a stronger claim than any competitor; state it as a target, not a result.

## 3. GitHub extraction recipe (demo)

Auth: fine-grained PAT or GitHub App; user must consent (plan STEP-5.8). Only public plus granted private repos are visible; GraphQL `restrictedContributionsCount` counts contributions you cannot see.

Rate limits (verified in docs): GraphQL primary 5,000 points/hour per user (10,000 for Enterprise Cloud org apps); cost ≈ requested nodes / 100, min 1; check with `rateLimit { cost remaining }`. Secondary: 100 concurrent, 2,000 points/min GraphQL, 900/min REST, about 80 content-creating requests per minute. Search API: 30 req/min authenticated (code search 10/min), max 1,000 results per query, `per_page` max 100, `incomplete_results` flag.

Endpoints and fields:
- Merged PRs per language: Search `GET /search/issues?q=is:pr+is:merged+author:LOGIN+merged:>=2024-11-01+language:python` (the `language:` qualifier on PR search is repo-language, so treat it as approximate; not confirmed in the docs page I fetched, test it). Safer: list PRs, then `GET /repos/{o}/{r}/pulls/{n}/files` and map file extensions to language. Fields: `merged_at`, `user.login`, `author_association`, `additions`, `deletions`, `changed_files`, `requested_reviewers`.
- Reviews given: GraphQL `user.contributionsCollection(from,to){ pullRequestReviewContributionsByRepository{ repository{ nameWithOwner primaryLanguage{name} } contributions{ nodes{ pullRequestReview{ state submittedAt body } pullRequest{ author{login} } } } } }`. REST alternative: `GET /repos/{o}/{r}/pulls/{n}/reviews` and `/comments`.
- Commit months: `contributionsCollection.commitContributionsByRepository` or `GET /repos/{o}/{r}/commits?author=LOGIN&since=...`. Window `from/to` max one year per call, so loop the 24 months in two or more calls.
- Languages per repo: `GET /repos/{o}/{r}/languages` (bytes, repo-wide, not per author; do not use as the person's skill).
- Attribution: commit list gives `commit.author` vs `commit.committer`, top-level `author` (may be empty if email unmatched), and `verification.verified`. Co-author trailers are only in `commit.message`; parse them yourself.

Signal to level kind (STEP-4.B):

| Signal | Level kind |
|---|---|
| Few or no merged PRs in language; only stars, forks, learning repos | Knows (cap per S3: not from GitHub alone; send nothing) |
| Merged PRs where review requested changes before approval, small diffs, author_association is CONTRIBUTOR or new MEMBER | Applies with help |
| Merged PRs in 3+ separate months within 24 months, approved without heavy revisions, in production repos | Applies alone |
| Many reviews given (APPROVED or CHANGES_REQUESTED with substantive comments) on others' PRs in that language, CODEOWNERS membership, maintainer or MEMBER/OWNER association, authored design or README docs | Leads or teaches |

Treat the 3+ separate months rule as the High-band gate (plan 3.A); one reviewer-heavy month is not enough.

Gotchas:
- Squash merges: PR author is correct, but commit author on main may be the merger.
- Bots (dependabot, renovate) and bulk reformat or vendored/generated files inflate counts; filter `user.type == "Bot"`, exclude lockfiles and generated paths.
- Search `language:` is repo-level; a Python PR in a mixed repo is mis-tagged. Use the file-extension route for anything shown to the employee.
- 1,000-result search cap: shard by date range.
- Private-repo work hidden unless scoped; absence of evidence is not absence of skill, so hold, never down-level.
- Self-merged PRs and solo repos: count as "Did the work" but not as independent review evidence.
- Quote rule (STEP-1.1): store PR title or review comment text as the quote; string-match it back to the API payload.

## 4. Steal list for a 24h demo

1. TechWolf's "level 4, based on 12 records" evidence trace as the message UI; already in the plan's "Based on" line. Show it first.
2. git-fame style surviving-line share, run on one demo repo, as an ownership check beside merged-PR counts. Cheap: `pip install git-fame`.
3. CodeScene's idea of "inconclusive" authorship: render a Hold state instead of guessing. Matches STEP-4.A hold.
4. Reviews-given as the leads-or-teaches signal (CORRECT uses prior technology touches; you add review depth).
5. Hardcode one real GitHub user (consenting teammate), 24 months, one language, produce the Teams-style card with level line plus 3 evidence items and the three buttons. Skip fitted weights; show the rule table.
6. Bring the Workera objection yourself: "inference proposes, employee confirms, Tara calibrates level." Offer Tara results as the ground-truth set (GT.A assessment set); this is the iMocha-specific hook.
7. Do not copy: LOC-based Impact scores, GitHub byte-count language rankings, Stack Overflow reputation as evidence.

## 5. Sources (opened or returned by search)

- https://pluralsight.com/product/flow/code
- https://gitclear.com/pluralsight_flow_was_gitprime_three_competitive_alternatives
- https://institute.brandonhall.com/wp-content/uploads/2023/03/SPP-Pluralsight-032023mc.pdf
- https://www.imocha.io/ai-interviewer-tara (fetched)
- https://www.imocha.io/smartrecruiters-with-imocha
- https://codesignal.com/certified-assessments/
- https://codesignal.com/cheating-and-fraud/
- https://designgurus.io/answers/detail/does-hackerrank-check-for-cheating
- https://www.techwolf.ai/faqs/what-proficiency-scale-does-techwolf-use (fetched)
- https://gloat.com/use-cases-agents/skill-intelligence-engine-agent/
- https://workera.ai/research/methodology
- https://docs.enterprise.codescene.io/versions/5.4.4/guides/social/knowledge-distribution.html
- https://pensero.ai/blog/swarmia-replacements
- https://github.com/casperdcl/git-fame (via PyPI https://www.pypi.org/project/git-fame/1.5.0/)
- https://github.com/kvadou/buildergraph (fetched)
- https://yespress.io/skillsync-yc-w26.md
- https://sites.uom.gr/a.ampatzoglou/public_html/papers/kourtzanidis2020ase.pdf
- https://arxiv.org/pdf/1807.02965
- https://arxiv.org/html/2111.07101v2
- https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits-for-the-graphql-api (fetched)
- https://docs.github.com/en/rest/search/search (fetched)
- https://docs.github.com/en/rest/commits/commits (fetched)
- https://docs.github.com/en/graphql/reference/objects (fetched; field list only)

Not verified: Karat, Turing, Arc, Sourcegraph, gitinspector, LinearB/Swarmia vendor docs, GitHub `language:` PR-search semantics, Flow Impact formula.
