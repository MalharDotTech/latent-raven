"""Handwritten employee prose; structure and identifiers are assigned by generate.py."""
PEOPLE = {
'P033': dict(name='Nirav Deshpande', eid='KC-11682', gender='M', city='Pune', department='Billing Engineering', title='Software Development Engineer II', grade='P3', hire='2022-11-14', manager='KC-10264', institution='Savitribai Phule Pune University', degree='B.E.', field='Computer Engineering', year=2022, project='Billing adjustments', repo='billing-core', project_key='BILL', ext=['.java','.sql','.yaml'], rates=(9,8,7)),
'P034': dict(name='Sravya Dutta', eid='KC-12146', gender='F', city='Hyderabad', department='Data Platform', title='Data Engineer', grade='P2', hire='2024-06-10', manager='KC-10176', institution='JNTU Hyderabad', degree='B.Tech', field='Electronics and Communication Engineering', year=2023, project='Settlement ingestion', repo='data-platform', project_key='DATA', ext=['.py','.sql','.yaml'], rates=(9,7,7)),
'P035': dict(name='Tanvi Menon', eid='KC-12307', gender='F', city='Bengaluru', department='Product Design', title='Product Designer', grade='P2', hire='2024-10-07', manager='KC-10561', institution='Osmania University', degree='B.Pharm', field='Pharmacy', year=2022, project='Reconciliation workspace', project_key='PM', rates=(0,0,5)),
'P036': dict(name='Aman Bhatia', eid='KC-11529', gender='M', city='Bengaluru', department='Solutions Engineering', title='Solutions Engineer', grade='P3', hire='2022-09-12', manager='KC-10731', institution='VIT Vellore', degree='B.Tech', field='Computer Science and Engineering', year=2020, project='Payments integration pod', project_key='RECON', rates=(0,0,4)),
'P037': dict(name='Sanket Jadhav', eid='KC-11863', gender='M', city='Pune', department='Workplace', title='Facilities Engineer', grade='P2', hire='2023-02-13', manager='KC-10647', institution='College of Engineering Pune', degree='B.Tech', field='Civil Engineering', year=2018, project='Pune office fit-out', project_key='PM', rates=(0,0,3)),
'P038': dict(name='Devansh Sahu', eid='KC-12754', gender='M', city='Pune', department='Platform Engineering', title='Graduate Engineer Trainee', grade='P1', hire='2026-04-01', manager='KC-10471', institution='Savitribai Phule Pune University', degree='B.E.', field='Information Technology', year=2025, project='Platform enablement', repo='platform-k8s', project_key='PLAT', ext=['.yaml','.py','.sh','.md'], rates=(5,2,5)),
'P039': dict(name='Pallavi Kulkarni', eid='KC-12018', gender='F', city='Pune', department='Quality Engineering', title='QA Engineer', grade='P3', hire='2023-08-07', manager='KC-10230', institution='Shivaji University', degree='B.E.', field='Computer Science and Engineering', year=2021, project='Billing and reconciliation QA', repo='qa-automation', project_key='QA', ext=['.java','.xml','.json','.yml'], rates=(7,4,11)),
'P040': dict(name='Isha Sethi', eid='KC-12072', gender='F', city='Bengaluru', department='Web Engineering', title='Software Engineer', grade='P2', hire='2023-09-11', manager='KC-10326', institution='PES University', degree='B.Tech', field='Computer Science and Engineering', year=2023, project='Merchant console', repo='web-console', project_key='WEB', ext=['.tsx','.ts','.css','.js'], rates=(10,8,7)),
'P041': dict(name='Ritika Shah', eid='KC-12109', gender='F', city='Bengaluru', department='Finance', title='Financial Analyst', grade='P2', hire='2024-01-08', manager='KC-10682', institution='University of Mumbai', degree='B.Com', field='Accounting and Finance', year=2022, project='FP&A and management reporting', project_key='PM', rates=(0,0,2)),
'P042': dict(name='Vivek Narang', eid='KC-11058', gender='M', city='Bengaluru', department='Reconciliation Engineering', title='Engineering Manager', grade='M1', hire='2020-11-09', manager='KC-10037', institution='NIT Surathkal', degree='B.Tech', field='Computer Science and Engineering', year=2017, project='Reconciliation services', repo='recon-engine', project_key='RECON', ext=['.md'], rates=(1,7,1)),
}
CVS = {
'P033': [('2026-10-16', '''NIRAV DESHPANDE
Pune | nirav.deshpande@kestrelcloud.com
Software Development Engineer II

Experience: 3 years 11 months

Kestrel Cloud Pvt Ltd      Nov 2022 - Present
SDE II, Billing
- Working on Java / Spring Boot billing services. Changes in invoice adjustments, refunds and posting jobs.
- Fixed the month-end worker running out of heap while exporting a large account. Took heap dump on staging and changed the read to batches.
- Maintain adjustment API, transaction boundaries and readiness checks. I do the deployment checks for our pod on alternate releases.
- SQL query changes for invoice search. Added the index after checking explain output on the month-end snapshot.
- Added RestAssured checks for duplicate requests and partial refunds. Review other developers changes in billing-core.
- Updated the Docker build with help from our platform engineer when the service moved to Java 21.

Technical skills
Java, Spring Boot, SQL, API testing, Code review, Docker, Kafka, Kubernetes, AWS, Python

Education
B.E. Computer Engineering, Savitribai Phule Pune University, 2022. 8.04 CGPA

Personal projects: expense sharing application during final year.
Languages: English, Hindi, Marathi
Notice period 60 days
''')],
'P034': [('2026-09-09', '''Sravya Dutta
Hyderabad / sravya.dutta@kestrelcloud.com
DATA ENGINEER

Python | SQL | Airflow | Snowflake

Kestrel Cloud Pvt Ltd, Hyderabad         June 2024 - Present
Data Engineer
Daily settlement file ingestion and recovery of missing partitions. Maintaining Python parser modules and Airflow dags. Have handled backfill for three bank feeds after file format changes. Added exception handling for dates coming as strings as well as numbers.
Snowflake tasks: query profile checks, warehouse sizing for the morning load, row count reconciliation. SQL models for settlement and refund facts.

TCS, Hyderabad                         Aug 2023 - May 2024
Assistant System Engineer
Worked on SQL data checks for a retail reporting project. Python file validation utility, changes reviewed by module lead.

PROJECT WORK
Settlement feed restart: read the last successful file manifest instead of using yesterday's date. On failure the rerun starts from the file that was not committed.

B.Tech ECE, JNTU Hyderabad, 2023 (7.9/10)
Tools also used: dbt, Git. Basic data modelling.
Updated September 2026
'''), ('2026-09-23', '''SRAVYA DUTTA   |   Analytics Engineer
Hyderabad
sravya.dutta@kestrelcloud.com

SQL, Snowflake, dbt, data modelling; Python, Airflow

EMPLOYMENT
Kestrel Cloud Pvt Ltd | Data Engineer | Jun 2024 - Current
- Settlement and refund fact models, matching source totals by bank and value date.
- Maintains SQL transformations. Query profile review for the morning dashboard and removal of the join fan-out in refunds.
- Built two dbt models with the analytics lead, source freshness and uniqueness checks added in the same change.
- Supports Python parsers and Airflow backfills for settlement feeds.

TCS | Assistant System Engineer | Nov 2023 - May 2024
SQL checks for retail reporting, Python file validation under module lead.

Selected work
Refund reporting: agreement on grain is one row per refund event; a retry is not another refund. Worked on the model and validation queries.
Settlement restart: track committed file manifests so failed loads can be restarted.

Education: B.Tech, Electronics and Communication Engineering
JNTU Hyderabad, 2023, 7.9 CGPA
''')],
'P035': [('2026-10-05', '''Tanvi Menon
Product designer, Bengaluru
tanvi.menon@kestrelcloud.com
Portfolio: tanvimenon.design/work

Kestrel Cloud | Product Designer | Oct 2024 - Present
Reconciliation workspace, onboarding and bulk actions.
Designed the exception review flow. The pilot reduced time on task from 4m 12s to 2m 46s, and completion went from 61% to 78%. 8 moderated sessions. Took interviews, made flows, prototype and handoff screens.
Maintain Figma components for status, amount and empty states. Check designs after implementation, usually one round of fixes for spacing and table wrapping.

Freelance (alongside job)
Apr-Jun 2025: Aruvi Dental, appointment enquiry screens and mobile layout.
Nov 2025-Jan 2026: Paper Fern Studio, catalogue and checkout prototype.
Jun-Aug 2026: Kora Tutors, signup pages and an information architecture pass.
Earlier: freelance landing pages, May 2023-Sep 2024.

Tools / skills
Figma             █████████░ 90%
UX Research       ███████░░░ 70%
Product discovery ███████░░░ 70%
Stakeholder management  ████████░░ 80%
Technical writing, Agile delivery

Education: B.Pharm, Osmania University, 2022 (76%).
Google UX Design Professional Certificate, Coursera, 2023.
I moved into design after doing patient information leaflets for a college project.
''')],
'P036': [('2026-10-14', '''AMAN BHATIA
Solutions Engineer - Payments | Bengaluru
aman.bhatia@kestrelcloud.com

6 years in software and customer facing engineering

Kestrel Cloud Pvt Ltd, Solutions Engineer           Sep 2022 - Present
Payments integration pod
Demonstrates the ability to convert ambiguous payment reconciliation requirements into a clear technical solution, a core SE function. Discovery with finance and integration teams is a direct parallel to consultative solution selling. My responsibilities span discovery, solution mapping, proof of concept, implementation readiness and adoption.

A recent multi-bank evaluation involved a single settlement across two merchant IDs. I ran the technical sessions, agreed the daily acceptance totals with their controller and maintained the issue list through pilot signoff. I handle objections around delayed files and duplicate webhooks using a sample flow rather than slides alone.
Maintain our partner API smoke collection and SQL acceptance checks. Salesforce opportunity stages and next steps updated after each technical checkpoint. Work with AE on the final commercial handoff.

Infosys, Systems Engineer                         Aug 2020 - Aug 2022
Java and Spring Boot development for a payments gateway connector. SQL support queries and integration testing. Change requests and production support under the technology lead.

Other work
Mitti Cart | Co-founder, part time | Jan 2025 - Present
Small home linen store with Isha Sethi. I handle suppliers, payment settlements and order exceptions. We pack on weekends. Website and product pages are handled by Isha.

Skills: Solution selling, Salesforce CRM, Customer onboarding, API testing, SQL, Java, Spring Boot, Stakeholder management, Technical writing.
B.Tech CSE, VIT Vellore, 2020
''')],
'P037': [('2026-08-17', '''BIO DATA
SANKET JADHAV
Facilities Engineer
Pune, Maharashtra
sanket.jadhav@kestrelcloud.com

Qualification: B.Tech Civil Engineering, College of Engineering Pune, 2018
Percentage : 72.40

WORK EXPERIENCE
Kestrel Cloud Pvt Ltd, Pune    February 2023 to till date
Workplace / Facilities Engineer
Pune office fit-out: 2 floors, 286 workstations. Checking vendor measurements against drawings. Daily site supervision, ceiling levels, partition setting out, checking fire door locations with consultant.
Prepared BOQ quantities and checked running bills. AutoCAD revisions for pantry and meeting rooms. Snag list before possession, water ponding test and as-built collection.

Larsen & Toubro    July 2018 - January 2023
Site Engineer
Finishing works on commercial building. Site measurements, material reconciliation, contractor bill checking and daily progress register.

SKILLS
AutoCAD, Site supervision, Vendor management, Quantity surveying, BOQ estimation, Snagging, MS Office.

PERSONAL INFORMATION
Date of birth : 17 July 1996
Marital Status : Married
Languages known : Marathi, Hindi, English
Nationality : Indian

DECLARATION
I hereby declare that the information furnished above is true to the best of my knowledge and belief.
Place: Pune
Date: 17/08/2026
Sanket Jadhav
''')],
'P038': [('2026-10-12', '''DEVANSH SAHU
Graduate Engineer Trainee
Pune  |  devansh.sahu@kestrelcloud.com
  https://github.com/devansh-
sahu

OBJECT IVE
To work in platform engineering and develop my technical knowl�dge.

EDUCAT ION
B.E. Information Techno logy, Savitribai Phule Pune University
2025       CGPA 7.41 / 10

EXPERI ENCE
Kestrel Cloud Pvt Ltd          Apr 2026 - Present
Graduate Engineer Trainee
Platform team. Added namespace quota yaml and checks with mentor.
Python script for config validation. Linux service checks on staging
with senior engineer. Pipeline change for manifest validation.
Wrote the setup steps after feedback from buddy.

TCS | Summer internship | 04 Aug 2025 - 22 Aug 2025
Observed the deployment window and daily support call. I saw how
the team checked logs and how Docker image is taken to test server.
Attended induction and made daily diary of activities.

PRO JECTS
Kubernetes scheduling - seminar, college technical week, Feb 2025.
Go in cloud systems - seminar presentation, Mar 2025.

TECHNICAL SK ILLS
Python   Kubernetes   Linux   CI/CD   Technical documentation
Docker, Go

Languages: Hindi, English
Date 12.10.2026
''')],
'P039': [('2026-10-08', '''Pallavi Kulkarni
QA Engineer | Pune
pallavi.kulkarni@kestrelcloud.com

5 years experience - Web and API testing

Kestrel Cloud Pvt Ltd (Aug 2023 - Present)
QA Engineer
* Selenium WebDriver with Java for merchant billing screens, TestNG and Maven.
* Maintains the nightly suite and fixes flaky tests. Repeat runs before marking a flaky ticket done.
* RestAssured checks for adjustment and reconciliation APIs, including auth, retries and invalid requests. Found the duplicate refund issue during release testing.
* SQL queries to compare API totals with the test database. Queries checked with the developer for joins on tenant and invoice.
* Added the report upload and retry stages in GitHub Actions with build engineer. Review test PRs, especially data setup and parallel execution.
* Test fixture API changes in Java; controller and validation tests with reviewer feedback.

Infosys (Aug 2021 - Jul 2023)
Systems Engineer
Manual regression and Selenium scripts for a retail portal. Defect reporting, retesting, test data preparation.

Skills: Selenium, Java, API testing, SQL, CI/CD, Code review

Certificate
Certified Tester Foundation Level (CTFL) v4.0 - Udemy, Jun 2024

B.E. Computer Science and Engineering, Shivaji University, 2021. 78.6%
Notice period: 60 days
''')],
'P040': [('2026-10-19', '''ISHA SETHI                              EXPERIENCE
Software Engineer                       Kestrel Cloud Pvt Ltd
Bengaluru                               Sep 2023 - Present
isha.sethi@kestrelcloud.com              Merchant console, React + TypeScript.
                                        Built refund detail and exception list screens.
SKILLS                                  Fixed stale responses replacing the newer filter
React                                   result. Type narrowing around optional bank fields.
TypeScript                              React profiler used on the long exception table;
JavaScript                              row actions were recreating every render.
API testing                             API checks for error states and retry button,
Code review                             reviewed with QA. Build pipeline changes with
CI/CD                                   release engineer.

EDUCATION                               OTHER WORK
PES University                          Mitti Cart | Jan 2025 - Present
B.Tech CSE, 2023                         Co-founder / web developer, part time
8.12 CGPA                               Small home linen shop, with Aman Bhatia.
                                        React catalogue, size selection and checkout
                                        status pages. Aman handles suppliers and
                                        payment settlement. Mostly evenings, weekend
                                        order packing when needed.

SELECTED WORK                           ABOUT
Refund screens, 2025-26                  Frontend engineer, 3 years experience.
Merchant filters, 2024                   Prefer working close to QA for edge cases.
Invoice download, 2023                   Updated 19 Oct 2026
''')],
'P041': [('2026-10-07', '''Ritika Shah
FP&A Analyst
Bengaluru | ritika.shah@kestrelcloud.com

Kestrel Cloud Pvt Ltd          Jan 2024 - Present
Financial Analyst
Monthly cost forecast, headcount bridge and management reporting. Excel models with base/upside/downside scenarios, actuals to budget variance and checks back to the ledger.
SAP FI month-end reconciliation, parked document queries, cost centre corrections and follow-up with AP. Some SQL for invoice and headcount extracts, queries reviewed by the data team.

Identified Rs.1,37,42,680 of annualised savings in the FY25 vendor review. Reduced forecast preparation from 3.8 days to 1.6 days. Forecast MAPE improved from 11.3% to 6.1% for the infra cost line.

TCS, Finance Executive          Aug 2022 - Dec 2023
Monthly MIS, expense schedules and cost centre reporting.

Skills
Excel financial modelling, SAP FI, SQL, data modelling, stakeholder management, technical documentation.

B.Com (Accounting and Finance), University of Mumbai, 2022, 81%
Languages: English, Hindi, Gujarati
''')],
'P042': [('2026-10-28', '''Vivek Narang
Engineering Manager, Reconciliation
Bengaluru  |  vivek.narang@kestrelcloud.com

Experience
Kestrel Cloud Pvt Ltd
Engineering Manager                         Jan 2023 - Oct 2026
Software Engineer                           Nov 2020 - Dec 2022

Team of 8, reconciliation services. Planning, design reviews and production readiness. I track dependencies with billing and data, and help engineers cut work into releases. Recent work includes backfill isolation and bank file replay limits.
Keep decision notes and follow up on retro actions. Review PRs around failure handling and rollout, with service owners doing the implementation reviews. Ran the last two quarterly recovery exercises with the on-call team.
Earlier worked on Go services for recon workers, cancellation and retry handling. Go was my main language through 2022; most of my time now is in reviews and team delivery.

Infosys | Systems Engineer / Senior Systems Engineer
Aug 2017 - Oct 2020
Backend services and support for transaction processing.

Skills: Technical leadership, Code review, Agile delivery, Stakeholder management, System design, Technical writing. Go (last full-time coding role 2022).

B.Tech CSE, NIT Surathkal, 2017
Profile updated Oct 2026
''')],
}

# title | issue summary | concrete implementation / outcome | extensions
# Records have no IDs or calendar dates; the generator links them to event slots.
WORK = {
'P033': [
('fix: reject empty adjustment reason','Blank reason accepted on adjustment','Spring Boot controller validates trimmed reason. Integration checks cover a blank and a whitespace-only request.','.java'),
('keep tenant id in refund lookup','Refund lookup missing tenant filter','SQL lookup now binds tenant_id before invoice_id; the query test has the same invoice number in two tenants.','.java,.sql'),
('round tax after summing line amounts','Paisa difference on split invoice','Use BigDecimal through the accumulator; round at the invoice boundary. Reconciled the six failing invoice fixtures.','.java'),
('add idempotency check for adjustments','Retry posts a second credit','RestAssured suite sends the same idempotency key twice and checks one posting; the different-payload case returns 409.','.java'),
('move export reader to bounded batches','Month end export worker OOM','Heap dump showed retained invoice rows in ArrayList. Changed the reader to 500-row pages and ran the 420k-row snapshot with bounded heap.','.java'),
('fix: readiness while posting queue is paused','Paused worker still reports ready','Spring Boot readiness health group includes posting-worker state. Verified the deployment stops taking jobs until the worker starts.','.java,.yaml'),
('Bump runtime base to 21','Billing container fails timezone check','Updated Dockerfile with Nilesh; used the same tzdata in build and runtime images. CI container starts and /actuator/health returns UP.','Dockerfile,.yaml'),
('use index for invoice search by date','Search times out on large tenant','SQL EXPLAIN ANALYZE moved from a sequential scan to tenant/date index scan, 840ms to 46ms on the release snapshot.','.sql,.java'),
('fix: transaction rollback on posting failure','Adjustment saved without ledger entry','Spring transaction now includes the ledger enqueue row. Fault injection after insert leaves neither row committed.','.java'),
('test: adjustment expiry boundary','Expiry midnight regression','API checks run before and at expiry, with fixed clock and Asia/Kolkata date. Included missing auth and cross-tenant IDs.','.java'),
('stop retrying validation exceptions','Invalid posting loops in retry queue','Split permanent validation failures from transient transport exceptions. Queue depth returned to normal after deploy; checked one failed item was parked.','.java'),
('close resultset on failed export','Connection pool exhausts after cancelled download','Java stack samples showed export threads waiting for a connection. try-with-resources closes the cursor on cancellation and timeout.','.java'),
('normalise currency before key lookup','lowercase currency fails adjustment','Normalise the request code before matching. Kept the original value in validation error, added mixed-case controller tests.','.java'),
('fix: lock order for concurrent credit notes','Concurrent credits can deadlock','Acquire invoice row before balance row on both paths. Parallel integration run has 200 paired requests without deadlock.','.java,.sql'),
('healthcheck port in image','New image remains unhealthy','Adjusted Docker HEALTHCHECK to the management port following Nilesh review. Checked startup and shutdown with docker run.','Dockerfile'),
('test refund conflict response','Refund conflict response missing details','Added API checks for failure response contract and duplicate refund on a partially paid invoice. CI caught the missing conflict code before release.','.java,.json'),
('rename pendingAmount local','Adjustment calculator tidy up','Rename only, no behaviour change. Existing amount parameterised tests pass.','.java'),
('keep adjustment sequence on rollback','Gap after declined adjustment','Moved sequence allocation behind successful validation. Verified rollback and same-key replay in staging.','.java,.sql'),
('set lower fetch size for audit export','Audit export memory spike','JDBC driver was ignoring fetch size with autocommit. Explicit read transaction now streams rows. RSS stayed below the pod limit on replay.','.java'),
('fix: reject refund against void invoice','Void invoice refund accepted','Controller accepts request but service validates invoice status within the transaction. Added state transition regression checks.','.java'),
('test bank timeout then retry','Missing retry coverage for refund','Two-step API test uses a timeout response followed by success and asserts only one ledger posting. QA verified the seeded duplicate case fails.','.java'),
('remove unused adjustment mapper','Remove old adjustment conversion','Deleted obsolete mapper and mapping tests after callers moved to the new request shape.','.java'),
],
'P034': [
('fix date parsing for bank B','Feed rejected numeric settlement date','Accept Excel serial dates and ISO strings; explicit exception for dates outside the file month. Tests include leap day.','.py'),
('dedupe files by bank and checksum','Repeated upload adds settlement rows','Manifest key includes bank and checksum. Replayed both duplicate and corrected file variants; source count agrees after replacement.','.py,.sql'),
('repair missed settlement partitions','Backfill skips day after failed load','Airflow backfill selects uncommitted manifest rows instead of yesterday. Cleared the failed task and replayed three partitions with no duplicates.','.py'),
('cast refund id before join','Refund join drops leading zero ids','SQL model keeps bank IDs as text. Compared source control totals and the unmatched output before deploying.','.sql'),
('add source tests for settlement facts','Settlement fact grain checks','dbt fact model and source uniqueness tests, with corrections from Leena on the composite key. Successful CI build and source totals attached.','.sql,.yml'),
('fix: catch malformed trailer','Parser crashes on empty last line','Separate blank lines from trailer rows. Added malformed input fixtures and reran the daily ingestion task.','.py'),
('limit concurrent backfills','Backfill saturates settlement pool','Airflow pool and max_active_runs changed after a failed catch-up. Run history for the next backfill has no queued daily load.','.py,.yaml'),
('prune refund date scan','Dashboard scans full refund history','Snowflake query profile had a full table scan on cast(value_date). Changed to a bounded range on the date column; same totals, fewer scanned partitions.','.sql'),
('resize morning load warehouse','Morning load credits jump','Snowflake query history showed short queries waiting behind the wide merge. Split load and reporting warehouses, tested auto-suspend; deployed after the cost comparison.','.sql,.yaml'),
('make refund event key explicit','Refund model key review','Reviewed diagram now distinguishes refund event and payment keys. Leena corrected relationship cardinality; SQL reconciliation checks joined totals per tenant.','.sql'),
('fix missing timezone in filename date','UTC date sent to bank feed path','Python path builder uses bank timezone; the production runtime fault reproduced with a near-midnight fixture.','.py'),
('add retry delay to status sensor','Sensor hammers bank status API','Airflow retry delay and timeout set independently. Deployed DAG and checked a simulated outage followed by successful backfill.','.py'),
('test freshness for refund source','No stale-source failure on refunds','dbt source freshness and not-null tests with analytics lead review. Changed the source relation after CI identified the old database alias.','.yml,.sql'),
('exclude cancelled settlement from total','Cancelled rows counted twice','Split cancellation from replacement rows. Query plan and per-bank balance diff attached to ticket.','.sql'),
('handle empty zipped feed','Empty archive crashes ingest','Return a typed empty result for a valid zero-record archive; corrupt archives still fail. Production reprocessing completed.','.py'),
('fix warehouse resume after timeout','Reporting warehouse does not resume','Snowflake task resumed against the load role by mistake. Corrected warehouse binding and checked query history after deployment.','.sql'),
('retry failed bank C partition','Bank C run remains incomplete','Airflow run repaired from the last committed manifest. Reconciled row count and bank trailer amount before marking the partition complete.','.py,.sql'),
('settlement key null check','Null merchant ids in settlement model','Added SQL integrity check and a rejected-row table. Leena reviewed the model diagram and the source-to-fact reconciliation.','.sql'),
('fix: decimal overflow in bank parser','Large settlement amount rejected','Use decimal.Decimal with explicit scale; unit test covers the failing amount. Rerun wrote the missing bank partition.','.py'),
('trim unused reporting columns','Refund report scans unused fields','SQL projection prunes wide attributes before join. Snowflake query profile and control total comparison checked in staging then deployed.','.sql'),
],
'P038': [
('add quota for sandbox-a','Sandbox namespace needs quota','Added Kubernetes namespace quota using the supplied limits. Nilesh corrected the memory unit; dry-run and sandbox rollout passed.','.yaml'),
('validate team labels','Missing owner label in sandbox','Python checker and unit tests for owner/team labels. Reviewer asked to reject whitespace-only values before merging.','.py'),
('docs: kube context setup','New starter setup step missing','Wrote setup steps; buddy corrected context name and added the command to print current-context. Second run completed on the training laptop.','.md'),
('sandbox service restart notes','Record service check commands','Under Nilesh guidance ran systemctl status and journalctl on the staging helper host. Corrected unit name in shell check; recorded output in ticket.','.sh,.md'),
('run manifest check on PR','CI misses invalid resource requests','Added pipeline validation step with release engineer review. First run failed on kubeconform version; pinned the tool and passing run attached.','.yaml'),
('fix: missing label value','Blank label passes checker','Python script strips the label before checking. Unit test added after reviewer supplied the whitespace input.','.py'),
('quota for sandbox-b','Sandbox B quota rollout','Applied reviewed manifest in the supervised sandbox window. Checked ResourceQuota output and one rejected over-limit pod.','.yaml'),
('correct staging probe path','Training deployment readiness path wrong','Nilesh pointed out readiness and liveness were using different routes. Changed manifest and checked rollout status together.','.yaml'),
('check service user in setup','Setup check runs as root','Added shell check for the configured service user. Buddy corrected quoting and compared command output from staging.','.sh'),
('docs: log directory permissions','Permission step missing in setup','Draft used chmod 777; Nilesh changed it to the service group and checked access as that user. Updated the technical procedure.','.md'),
('add fixture for yaml null','Config checker fails on null document','Python unit test and guard for an empty YAML document, with reviewer correction on exception type.','.py'),
('test sandbox namespace limits','Quota check for sandbox template','Added reviewed Kubernetes limit range and verified the default request on a new test pod.','.yaml'),
('fix pipeline artifact path','Validation report not uploaded','With build engineer changed artifact path to match output directory. CI check now keeps the validation report.','.yaml'),
('return nonzero for missing owner','Checker returns success on invalid config','Python exit status test, corrected after buddy review; CI run fails on the supplied bad fixture.','.py'),
('add staging service check example','Starter runbook command example','Added reviewed status and journal output snippets; Nilesh verified the commands in the pairing session.','.md,.sh'),
],
'P039': [
('wait for invoice row not spinner','Invoice list test intermittently fails','Explicit wait targets the invoice row after search. 40 repeat runs passed, including the slow-response fixture.','.java'),
('add refund auth checks','Refund endpoint accepts missing scope','RestAssured suite now checks missing scope and cross-tenant invoice IDs. Scope defect raised before the release candidate went out.','.java'),
('seed invoices per worker','Parallel tests share invoice ids','Allocate a tenant fixture per worker. No collisions across 30 full parallel runs.','.java'),
('fix: stale element in refund modal','Refund modal test flakes','Re-query the confirmation button after the amount update. Repeat-run report attached for chrome and firefox.','.java'),
('test duplicate refund retry','Retry can post refund twice','RestAssured checks timeout then retry and ledger totals; the seeded service bug failed in CI before release.','.java'),
('fix tenant join in assertions','Totals check joins wrong tenant','SQL validation query now joins on tenant and invoice. Data engineer reviewed the query and source totals on the sample database.','.java,.sql'),
('upload test report on failure','Failed test jobs have no report','Added GitHub Actions always() report step with build engineer; failed-run artifacts now include the junit report.','.yml'),
('fixture api: reject negative totals','Fixture endpoint accepts invalid total','Fixture controller and tests under Deepak review; changed validation order after reviewer found null amount returned 500.','.java'),
('avoid cached element on tab switch','Tab switch invalidates invoice element','Page object now resolves within active panel. Tested 50 tab-switch repetitions without stale reference.','.java'),
('check refund contract on 409','Conflict response loses request id','API contract test checks request ID and error shape on conflict. CI run exposed response mapper regression in the release candidate.','.java,.json'),
('query totals by value date','Test totals use posting date','Reviewed SQL query uses bank value date, compared sum and count against supplied reconciliation sheet.','.sql,.java'),
('retry only the browser setup step','Rerun hides failed assertions','Changed pipeline retry stage with build engineer review. Assertion failures no longer rerun, setup failures retry once.','.yml'),
('fix download wait','CSV download occasionally empty','Selenium suite waits on download completion rather than fixed sleep. Repeat run includes delayed response and empty invoice list.','.java'),
('test revoked token response','Revoked token gets wrong error','RestAssured failure-path checks distinguish expired and revoked tokens, with assertions on response schema and audit ID.','.java'),
('clear worker fixture in finally','Failed test leaves invoice lock','Java fixture handler cleanup, reviewed by Deepak. Controller test forces validation failure and confirms the lock is released.','.java'),
('fix: invoice badge locator','Badge text changed in new UI','Selector uses data-testid instead of translated label. Full locale matrix and repeat-run reports passed.','.java'),
('refund rounding assertions','Rounding changes not caught by API suite','API checks compare BigDecimal totals and the ledger snapshot for partial refunds; caught the one-paisa regression in preprod.','.java'),
('handle missing bank id in fixture API','Fixture endpoint returns 500 for missing bank','Java fixture controller now returns 400. Reviewer corrected the null check and test covers missing and empty values.','.java'),
('remove sleep from invoice paging','Paging suite takes too long','Selenium expected condition watches active page and row key. 60 repeat runs passed on slow staging.','.java'),
('fix test report retention','Reports removed before QA signoff','Pipeline retention edited with build engineer guidance; checked report was available after the next nightly run.','.yml'),
('test webhook signature errors','Bad signature response contract','RestAssured suite covers absent and invalid signature. Pre-release CI caught raw exception content in response.','.java,.json'),
('compare open balance query','Open balance assertion misses credits','SQL query reviewed for credit-note join and reconciled against the supplied tenant totals.','.sql'),
],
'P040': [
('fix invoice download name','Invoice download has wrong extension','Keep the content-disposition filename. Tested slow response and aborted navigation; released with console patch.','.js,.tsx'),
('keep filters when paging','List paging drops bank filter','Filter state now lives above the paginated table. Component tests cover paging then changing bank.','.tsx,.ts'),
('narrow amount before formatting','Optional amount crashes row render','Guard missing amount before money formatting; removed unsafe assertion and added regression test.','.ts,.tsx'),
('cancel stale invoice requests','Old search result replaces new one','Abort previous fetch in effect cleanup. JavaScript test resolves requests in reverse order and the React screen retains current results.','.tsx,.js'),
('show retry for bank timeout','Timeout screen has no recovery action','React error panel and reviewed API checks for timeout, retry and missing auth. QA corrected the expected timeout error code.','.tsx,.ts'),
('fix credit note selection reset','Selection remains after tenant change','State reset follows tenant key; released with component tests for switching tenant and filter.','.tsx'),
('type refund status response','Refund status accepts unknown string','Discriminated union replaces string casts; exhaustive test handles pending and rejected variants.','.ts'),
('cache row action callbacks','Exception table rerenders on hover','React profiler showed all 180 rows rerendering. Stable callbacks cut unnecessary row commits; verified in released screen.','.tsx,.ts'),
('test empty refund response','Empty response breaks refund details','API error-state checks added with QA review, recorded 204 and malformed body responses in the component test run.','.ts,.json'),
('run typecheck before preview','Preview build misses type errors','Pipeline step added with release engineer guidance. Passing run linked after fixing workspace command.','.yml'),
('fix: filter debounce on unmount','Delayed search runs after navigation','Debounce cleanup cancels the pending promise callback; regression test moves route before timer fires.','.js,.tsx'),
('refund drawer focus return','Focus lost after closing drawer','Restore focus to trigger. Component tests include keyboard close and pending request.','.tsx,.css'),
('remove any from exception row','Unsafe cast hides missing bank field','Parser checks bank code and exposes nullable display value. Regression test covers missing bank object.','.ts,.tsx'),
('keep disabled action tooltip','Disabled action has no reason','React wrapper preserves tooltip for disabled actions. Released with component checks at narrow viewport.','.tsx,.css'),
('artifact name for preview build','Preview artifacts overwrite each other','With release engineer changed workflow artifact name to include PR ref; checked simultaneous runs retain separate bundles.','.yml'),
('fix: response after cancelled refund','Cancelled refund shows success toast','JavaScript response branch checks cancellation before success notification. Production async defect reproduced and regression test merged.','.ts,.tsx'),
('check retry after 429','Rate limit error state','API checks reviewed by QA cover Retry-After and an empty header. Expected delay corrected following review.','.ts,.json'),
('memoise exception table columns','Column actions rebuilt on selection','React profiler comparison attached: stable columns avoid rebuilding row cells when selection changes. Shipped in console release.','.tsx'),
('decode bank reference at boundary','Encoded bank ref displayed twice','TypeScript response adapter does one decode, regression tests preserve literal percent signs and malformed input.','.ts'),
('fix refund status polling teardown','Polling continues after drawer closes','React effect clears interval and aborts pending request; test advances timers after close and asserts no new call.','.tsx,.ts'),
('remove legacy invoice summary','Old summary component unused','Removed the old React summary after routes migrated. Existing screen tests pass.','.tsx,.css'),
('test retry button while offline','Offline retry leaves spinner running','Reviewed API checks for rejected network promise, offline state and recovery. QA confirmed the UI returns to retry state.','.ts,.tsx'),
],
'P042': [
('stop worker on cancelled context','Recon worker stays alive after cancel','Go worker selects on ctx.Done before waiting for next partition. Goroutine profile after replay returned to baseline.','.go'),
('return file errors to scheduler','Worker hides parse error','Go error wrapping retains file ID and cause. Failed partition is retried by scheduler instead of committed.','.go'),
('bound inflight partition jobs','Replay exhausts worker memory','Go semaphore bounds inflight partitions. Heap and goroutine profile checked during the 900-file staging replay.','.go'),
('close response body on retry','Recon worker leaks http connections','Go worker drains and closes body before retry. Connection count stayed bounded in staging failure injection.','.go'),
('test cancelled replay','Replay cancellation regression','Go tests exercise a cancelled context while the queue is empty and while a partition is running.','.go'),
('fix: duplicate settlement callback','Duplicate callback adds batch twice','Go handler uses batch key for idempotency. API fixture sends the callback twice and checks one committed batch.','.go'),
('cap retry backoff','Recon retry delay overflows','Go retry calculation clamps before multiplication. Table tests cover max duration and attempt boundary.','.go'),
('keep cancellation in parser path','Parser ignores worker shutdown','Pass context into Go parsing loop and release temporary buffer on cancellation. Replay profile checked after shutdown.','.go'),
('fix worker channel shutdown','Worker stuck when producer exits','Go producer owns channel close; consumer checks ok before processing. Repeated shutdown test and profile attached.','.go'),
('add replay window guard','Replay can cross bank cutoff','Go handler rejects a window beyond bank cutoff and tests the boundary with a fixed clock.','.go'),
('docs: backfill release checklist','Backfill release checklist update','Added queue-depth check and bank cutoff owner to the release checklist. Reviewed by the on-call engineer.','.md'),
('docs: replay rollback order','Replay rollback steps out of order','Updated the rollback procedure after the recovery exercise; reviewer asked to drain work before reverting the flag.','.md'),
('docs: load test entry criteria','Record load test entry conditions','Record agreed capacity test inputs and the owner of the bank fixture set. Discussed at the service design review.','.md'),
('docs: failure drill checklist','Recovery drill follow-up','Added the missing old-file replay check from the exercise notes. Team checked it in staging before signoff.','.md'),
('docs: on-call handover checklist','Handover actions need owners','Added explicit owners and links to the pending recovery tickets. Accepted at the team delivery review.','.md'),
('docs: partition isolation decision','Record partition isolation decision','Linked the accepted bank-level queue decision and production rollout checks from the design note.','.md'),
],
}

# Non-code workplace records. Text is written as requests, comments and accepted outcomes.
TICKETS = {
'P035': [
('Bulk exceptions empty state','Need an empty state for a bank with no exceptions, not the all-banks message.','Figma version 18, reconciliation workspace file: status and empty-state components updated. Tanvi handed over redlines; WEB release 2024.12 includes the new empty state.','PM'),
('Refund amount component','Amount cell truncates the sign at 100% zoom.','Tanvi updated the Figma amount component variants in version 27. Design QA accepted after screenshot comparison; WEB release 2025.04.','PM'),
('Exception drawer handoff','Implement drawer states for pending and completed cases.','Figma version 41 linked by Tanvi. Engineering used the status and amount components; release 2025.08 accepted after spacing corrections.','PM'),
('Bulk action confirm states','Confirm needs separate copy for mixed bank selection.','Tanvi maintained prototype version 54 and the status component, QA screenshots checked. WEB release 2025.12 accepted.','PM'),
('Table density in exception review','Long bank names wrap badly at 1280 width.','Figma version 68 and table component updates supplied by Tanvi. Design QA signed off against release 2026.04 screenshots.','PM'),
('Review flow final screens','Ship the revised exception review drawer.','Tanvi delivered Figma version 83, linked prototypes and component variants. WEB release 2026.08 accepted with final amount spacing fix.','PM'),
('Search empty state followup','Search with trailing spaces gives a confusing empty page.','Prototype version 89, Figma shared amount and status components checked at handoff. WEB release 2026.10 included the final screens.','PM'),
],
'P036': [
('Webhook 409 sample','Partner needs repeat-key failure cases in the acceptance collection.','Aman updated the API smoke collection: same key/same body, same key/different body, missing auth. CI run 1847 caught the 409 response without error code before release.','RECON'),
('Pilot opening balance check','Finance acceptance totals differ by one day for bank B.','SQL query reviewed by Sravya: changed posting_date to value_date and kept the tenant predicate. Reconciled count and sum to customer supplied totals. Aman reran it with the customer.','RECON'),
('Duplicate callback in partner test','Two callbacks arrive for the same settlement.','Aman added the repeated callback and timeout-then-retry paths to the maintained API suite. CI run 2094 exposed a second posting; verified the fix before pilot release.','RECON'),
('Agree pilot cutoff','Buyer wants same-day acceptance but bank file arrives next morning.','Aman agreed T+1 acceptance at 11am with the controller and integration lead. Product accepted the reporting label change; action list completed before pilot signoff.','RECON'),
('Missing scope acceptance check','Partner setup passes with wrong token scope.','API smoke suite updated by Aman for missing scope, expired token and cross-tenant ID. CI run 2318 blocked the release candidate on the missing-scope defect.','RECON'),
('Pilot invoice totals','Need agreed acceptance query for split merchant setup.','SQL joins reviewed by Sravya for tenant and merchant keys. Aman reconciled query output to the two source control totals and recorded customer acceptance.','RECON'),
('Close multi-bank pilot actions','Pilot needs replay recovery before acceptance.','Aman negotiated daily replay window with controller and integration lead. New acceptance schedule agreed, replay case passed, owners closed the action list.','RECON'),
('Signature error examples','Partner asks for failure contract examples.','Aman updated maintained API smoke checks for invalid signature and missing header. CI run 2670 found the untyped error response; fixed before partner release.','RECON'),
],
'P037': [
('Pune level 4 partition measurements','Check final partition quantities before running bill.','Sanket measured 184.6 square metres against the marked-up AutoCAD drawing. Vendor measurement sheet corrected for two door openings; consultant checked and signed the bill quantities.','PM'),
('Pune pantry drainage test','Complete ponding test before tile handover.','Sanket recorded 24-hour test and marked two seepage points on the site drawing. Vendor repaired joints and repeat test accepted by consultant.','PM'),
('Meeting room ceiling levels','Check ceiling setting-out before closure.','Site inspection by Sanket found one duct clashing with the bulkhead. Revised AutoCAD section issued to contractor; level check completed.','PM'),
('Office possession snag list','Walkthrough and closure of fit-out snags.','Sanket checked door closers, partition alignment, tile hollowness and as-built drawing set. 37 snags closed, 4 retained for the vendor visit. Consultant signed possession list.','PM'),
('As built drawing collection','Collect final civil drawings and measurement sheets.','Sanket checked the AutoCAD as-built against site measurements and returned the pantry drawing for revision. Final drawing set received from vendor.','PM'),
('Waterproofing rectification','Inspection after washroom leak complaint.','Sanket supervised tile removal and membrane repair at the threshold. Recorded site quantities and repeat ponding test before closing the vendor bill.','PM'),
],
'P041': [
('Forecast workbook tie-out','Complete monthly forecast checks before finance review.','Ritika built FCST_v7.xlsx with headcount, rate and FX assumptions linked to base/upside/downside scenarios. Formula check tab is clear; outputs tie to FI actuals. Reviewed by Meenal Shah, Finance Controller, accepted.','PM'),
('FI parked document clearing','Two cost centre documents remain parked after close.','Ritika traced failed FI cost-centre validity on the documents, corrected the posting dates with AP and reconciled the reposted entries to the ledger extract. Controller checked the reconciliation.','PM'),
('Invoice extract for budget bridge','Need SQL extract for the cost bridge.','Ritika SQL query reviewed by Sravya: tenant predicate and reversal-document exclusion corrected. Count and sum match supplied FI control totals. Output used in the budget bridge.','PM'),
('Q4 scenario workbook','Update forecast for hiring and infra options.','Ritika independently rebuilt FCST_v12.xlsx with separate headcount drivers and three scenarios. Check tab reconciles opening cash and P&L to the finance report. Meenal accepted after checking assumption links.','PM'),
('FI accrual mismatch','Accrual reversals not matching the month-end report.','Ritika traced the FI reversal period on six documents and reconciled the corrected postings to the ledger. AP confirmed all document references; controller accepted the close report.','PM'),
('Agree cost owner assumptions','Infra and finance have different forecast headcount bases.','Ritika agreed the start-date basis with infra lead and HR; decision recorded as signed offers only, vacancy upside kept separate. Both owners approved, workbook assumptions and report updated.','PM'),
('SQL cost centre mapping check','Compare cost extract with FI totals.','Sravya reviewed Ritika SQL and corrected the effective-date join. Reconciled the result against supplied cost centre totals; unmatched rows are listed for AP.','PM'),
('Rolling forecast signoff','Prepare the next rolling forecast.','FCST_v19.xlsx built by Ritika includes scenario switches, circularity check and actuals reconciliation. All formula checks passed and finance report tie-out accepted by Meenal.','PM'),
('FI duplicate reference query','Two expense postings share vendor reference.','Ritika checked SAP FI document history, identified the reversed original and reconciled net expense to the close ledger. No duplicate open payable remains.','PM'),
('Budget owner decision','Sales wants full travel budget restored for Q4.','Ritika agreed an event-based travel cap with sales director and finance controller. Signed decision and updated monthly phasing accepted by both; owners completed the revised request schedule.','PM'),
],
'P042': [
('Backfill queue isolation decision','Choose isolation boundary for bank file backfills.','Vivek proposed bank-level queues after comparing per-tenant memory and queue count. Team accepted capacity limit of 600 files/hour and tested the failure case with one bank unavailable. Production rollout passed queue and latency checks.','RECON'),
('Replay dependency with billing','Billing lock change blocks recon replay release.','Vivek agreed separate rollout windows with billing owner. Feature flag stays off until lock metrics pass. Owners completed both windows and release check was green.','RECON'),
('Retro: remove cross-bank test dependency','One bank fixture blocks all release candidates.','Vivek coordinated separate fixtures and owners. Tracked actions through two sprints; the recon board shows both fixture tasks done and no shared-data blocker at the next release.','RECON'),
('Reconciliation release split','Large replay feature exceeds release window.','Vivek guided the team through flag-first versus full release, recorded risk and owner for each path. Flag-first accepted; two phased releases completed with rollback checks.','RECON'),
('Bank cutoff capacity decision','Retry surge can extend work past bank cutoff.','Vivek authored capacity and failure notes for the replay limiter. Team accepted 80 concurrent jobs after load test; production validation kept work inside cutoff under the replay surge.','RECON'),
('Retro action: queue age owner','Queue age alert has no handover owner.','Vivek coordinated action owners and updated the release board. Both follow-up tickets closed in the next sprint; the handover check was completed on the next release.','RECON'),
('Agree recovery drill window','Data load conflicts with recon recovery exercise.','Vivek secured a shifted drill window with data and billing leads. Agreed evidence checklist and owners; drill completed and actions have named due dates.','RECON'),
('Partition rollout readiness','Close risks before bank partition change.','Vivek guided the technical decision on partial rollback and recorded capacity assumptions. Service owners completed load and failure tests, phased rollout passed production validation.','RECON'),
],
}

REVIEWS = {
'P033': [('The update can succeed then enqueue can fail. Can both inserts share the transaction?', 'Moved enqueue insert into the same transaction, rollback integration check added.'), ('This join is missing tenant_id. Same invoice id exists in another tenant.', 'Added tenant key to join and the two-tenant fixture.'), ('Closing the stream here will skip the failure path. Please use try-with-resources.', 'Resultset now closes in both success and error paths.'), ('BigDecimal from double will carry the binary error. Parse the decimal string.', 'Changed constructor and added 0.1/0.2 regression case.')],
'P034': [('Would this overwrite the earlier day when the file arrives late?', 'Partition now uses the bank value date; late-file fixture added.'), ('We need tenant in the key as well. Please check count before and after that join.', 'Composite key corrected; source and joined counts now agree.'), ('Empty archive should not be the same as a corrupt zip.', 'Split empty and invalid archive handling, tests updated.')],
'P038': [('Is this namespace meant to have the same default CPU request?', 'Nilesh confirmed the value and asked for units in the example; updated.'), ('The script accepts spaces for owner, should we strip it first?', 'Buddy confirmed; trim added with a whitespace fixture.')],
'P039': [('This fixture is shared by four workers. The delete in finally can remove another test data.', 'Created invoice per worker and moved cleanup to the worker fixture.'), ('A fixed sleep will still fail on slow CI. Can we wait on the actual row?', 'Changed to explicit wait on row ID; repeat run passed.'), ('We assert 409 but not that the balance stayed same. That would miss a second posting.', 'Added balance and posting-count assertions; seeded duplicate now fails.'), ('Catching Exception here makes a failed assertion pass the test.', 'Removed catch, kept cleanup in finally. Assertion failure visible in CI.')],
'P040': [('The response can arrive after tenant changes. Please abort the previous request.', 'Added AbortController in effect cleanup, reverse-order response test passes.'), ('This as Bank hides the missing bank field. Could we narrow before formatting?', 'Added optional-field guard and a missing-bank regression case.'), ('key=index reuses the wrong row when filters reorder this list.', 'Changed to exception ID and added reorder test.'), ('Timer stays alive when drawer closes, so this still polls in background.', 'Cleared timer on effect cleanup; unmount test checks no more requests.')],
'P042': [('If the file is committed before the ledger ack, what do we replay after a crash?', 'Moved commit marker after durable ack, added crash-between-steps regression test.'), ('This buffer grows for the whole bank file. Bound it before increasing the worker count.', 'Introduced bounded batches and attached the load-test memory graph.'), ('What stops one bank replay using every worker? Please include a noisy-neighbour test.', 'Per-bank limit added and the isolated-bank failure test passed.'), ('Rollback needs to drain the old queue before disabling the consumer.', 'Release steps reordered and checked in staging recovery exercise.'), ('The timeout cancels the HTTP call but does it stop the parsing goroutine?', 'Parser now receives context; shutdown test confirms goroutine count returns.'), ('The partial batch must stay retryable on that error. A success marker loses it.', 'Success marker is only written after full batch ack; error-path test added.')],
}
