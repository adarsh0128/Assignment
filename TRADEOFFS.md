# Tradeoffs

## 1. Asynchronous Ingestion Workers

What it is: A queue-backed pipeline using worker processes for parsing, normalization, anomaly detection, and progress events.

Why excluded: The prototype needs to be easy to run on Render with a small operational footprint. Synchronous processing keeps the architecture understandable while still preserving row-level failures and auditability.

Production version: Celery or a managed queue, idempotent ingestion tasks, progress events, retry policies, poison-row handling, and worker autoscaling.

## 2. Object Storage Abstraction

What it is: S3-compatible storage for uploaded CSVs with encryption, lifecycle policies, checksum validation, and legal retention rules.

Why excluded: The assignment explicitly scopes file storage to the local filesystem. Django `FileField` captures the storage boundary without adding an unused abstraction.

Production version: S3 or equivalent object storage, tenant-prefixed keys, KMS encryption, malware scanning, immutable retention, and signed access URLs.

## 3. Database-Level Audit Triggers

What it is: PostgreSQL triggers and restricted DB roles enforcing immutability independent of Django application code.

Why excluded: The prototype demonstrates behavior through model guards and service workflow code without requiring custom SQL or privileged database setup.

Production version: PostgreSQL triggers for `RawRecord`, `AuditLog`, `ApprovalAction`, and locked `NormalizedRecord` rows, plus append-only audit export to a tamper-evident archive.
