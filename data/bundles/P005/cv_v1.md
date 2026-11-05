# Sneha Iyer
Bengaluru | sneha.iyer.dev@gmail.com | github.com/sneha-iyer-dev

## Summary
Backend engineer, 4 years. Services in Go and Java for payments and reconciliation. Prefer boring, well-tested code.

## Skills
**Languages:** Go, Java, Python (scripts), SQL
**Backend:** gRPC, REST, Kafka, PostgreSQL, Redis, Docker
**Cloud/Tools:** AWS (SQS, S3), Helm, GitHub Actions, Prometheus/Grafana, Git

## Experience

**Kestrel Cloud Pvt Ltd** - SDE-II (Apr 2025 - present), SDE-I (Sep 2023 - Mar 2025)
Reconciliation Engineering, Bengaluru
- Work on recon-engine (matching engine) and ledger-api, both Go services
- Rewrote the settlement matcher worker pool; fixed goroutine leak that made workers restart every ~6 hours
- Added bulk posting endpoint to ledger-api (idempotency keys, batched pgx inserts), 8x throughput
- On-call for recon services, 1 week in 6
- Part of the go-live of the EU region (Berlin) for recon - wrote the go/no-go checklist and the data residency config switches
- Go-to-market support: built the tenant sandbox seeding script used by Sales Engineering demos

**Razorpay, Bengaluru** - SDE-I (Jul 2022 - Aug 2023)
- Worked on payment links backend in Java / Spring Boot
- Added webhook retry with dead letter queue
- Wrote unit and integration tests, raised coverage of module from 58% to 81%

## Education
B.Tech, Computer Science and Engineering, PES University, Bengaluru - 2022 (CGPA 8.7)

## Other
- Contributed small fixes to open source Go projects (docs, one bug fix in a CSV parsing library)
- Go Bangalore meetup attendee
