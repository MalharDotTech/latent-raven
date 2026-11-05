# Grounding corpus (collected 2026-11-05)

| File | Count | Sources |
|---|---|---|
| certifications.json | 57 | aws.amazon.com, learn.microsoft.com, cloud.google.com, training.linuxfoundation.org, databricks.com, developer.hashicorp.com, scrum.org, istqb.org, redhat.com, peoplecert.org, coursera.org; others via search results (flagged in notes) |
| courses.json | 30 (target 50 missed) | Coursera, Udemy, LinkedIn Learning, NPTEL, Pluralsight pages and search results |
| job_ladders.json | 5 ladders (Infosys, TCS, Freshworks, Zoho, India PM generic) | designgurus, networkinterview, levels.fyi, weekday.works (secondary) |
| tech_cooccurrence.json | SO 2024 + 2025 marginals, Octoverse 2024 India facts | survey.stackoverflow.co, github.blog |
| pr_title_samples.json | 177 PRs, 10 repos; 30 bot, 37 with Co-authored-by, mean 3.04 reviews, 28 zero-review | gh api |
| issue_style_samples.json | 117 (Jira SPARK/KAFKA/FLINK + GitHub issues) | issues.apache.org/jira REST, gh api |
| cv_conventions.md | notes | search snippets from vendor guides |
| names_and_universities.json | 32 surnames, 35 forenames, 5 employers, 4 institutions | forebears.io, levels.fyi, nptel.ac.in |

Gaps are recorded in each file's `_meta`. Not covered: SO co-occurrence and India SO stats, HR/sales courses, QA/DE/CS/sales/HR/support ladders, regional name split, global names, 40 Indian universities with tier, global universities, 20 employers, Western CV conventions, SHRM/CIPD/CAPM.
