# Rahul Verma
Senior Data Engineer | Bengaluru
rahul.verma@kestrelcloud.com

## Summary
Data engineer, 6 years. Batch and near-real-time pipelines on Python/PySpark/Airflow, AWS. Last 4 years at Kestrel Cloud on the billing and reconciliation data platform.

## Skills
Python, PySpark, Spark SQL, Apache Airflow, SQL (Snowflake, Athena, PostgreSQL), AWS (S3, Glue, EMR, IAM, Lambda), dbt (reading/reviewing), Terraform (basic), Docker, Kubernetes (basic), Git, Jenkins, GitHub Actions

## Experience

**Kestrel Cloud Pvt Ltd, Bengaluru** - Senior Data Engineer (Oct 2024 - present); Data Engineer II (Nov 2022 - Sep 2024)
- Owner of ingestion + silver layer DAGs for billing events (approx 60 DAGs); on-call rotation for data platform
- Led Airflow 1.10 -> 2.x upgrade of 140 DAGs with 2 other engineers; wrote DAG authoring standards (Confluence DATA space)
- Recon v2 data migration: moved recon ledger tables from MySQL dumps to partitioned parquet on S3, PySpark jobs, backfill tooling
- Cut billing_events_silver runtime from 3h10m to 55m (partition pruning, broadcast joins, small-file compaction)
- Reviewer on data-platform repo (~150 reviews/year); mentor to 2 junior engineers
- Added data quality checks (row count, freshness, null thresholds) to all tier-1 DAGs

**Infosys Limited, Bengaluru** - Systems Engineer
Jul 2020 - Oct 2022

Client: US retail bank (data modernisation programme)
- Developed ETL jobs in Python and Hive to load daily transaction files into the data lake
- Wrote PySpark scripts for aggregation of card transactions (approx 400 GB/day)
- Involved in migration of cron based scheduling to Airflow
- Used AWS S3 and EMR for batch processing, wrote shell scripts for housekeeping
- Worked with onsite coordinator for requirement clarification and daily status mails
- Fixed production issues as part of support rotation, raised RCA documents

## Certifications
- AWS Certified Developer - Associate (DVA-C02), Mar 2024

## Education
B.E. Computer Science and Engineering, RV College of Engineering, 2020 (CGPA 8.4/10)

## Personal Details
Languages known: English, Hindi, Kannada
