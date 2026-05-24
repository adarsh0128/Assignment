# Architecture Decisions

## SAP CSV Instead of OData

The SAP integration uses flat-file CSV because enterprise sustainability teams often receive scheduled extracts from SAP ECC or S/4HANA via jobs owned by ERP administrators. CSV also lets the prototype simulate real export quirks: localized numbers, mixed units, blank plant codes, and duplicate invoice lines.

Tradeoff accepted: CSV lacks typed contracts, delta semantics, and source-system authorization controls that OData can provide. Production could add OData when SAP ownership, security approvals, and change-data requirements are mature. The prototype intentionally excludes OData because the assignment focuses on file ingestion, row validation, and audit review.

## Ingestion Pipeline

The pipeline is split into parsing, schema validation, normalization, anomaly detection, and review-state creation. Services own business logic so views stay HTTP-focused and serializers stay I/O-focused.

Tradeoff accepted: the initial pipeline runs synchronously after upload to keep deployment small. Production would push runs to Celery or a managed queue and stream progress events.

## Row-Level Failure Handling

Invalid rows are stored as `RawRecord` entries with validation errors, while valid rows continue through normalization. This prevents a few bad rows from blocking a utility bill batch or SAP export.

Tradeoff accepted: analysts must review both batch-level and row-level health. Production would add richer remediation screens and resubmission workflows.

## Tenant Filtering

Tenant isolation is applied in querysets and service entry points using the authenticated user's organization. This keeps enforcement close to data access rather than scattered across individual view methods.

Tradeoff accepted: the prototype does not include PostgreSQL row-level security. Production multi-tenant deployments should add RLS and separate operational observability by tenant.

## Ambiguities Resolved

Travel "arrival before departure" requires time fields, but the required CSV listed only `travel_date`. The prototype accepts optional `departure_time` and `arrival_time` columns in travel CSVs and treats missing times as non-failing.

Scope 2 market-based vs location-based is noted in emission factors. Utility normalization defaults to location-based when no supplier-specific factor is selected.
