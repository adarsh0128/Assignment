# Data Model

This prototype models an enterprise ESG ingestion workflow where every operational record is owned by an `Organization`. The schema favors source traceability, row-level failure handling, and analyst auditability over broad analytics dimensional modeling.

## Tables

### Organization
Tenant root for all data. It exists because sustainability platforms are commonly deployed either for a single enterprise or as a multi-tenant service. The accepted tradeoff is that tenant deletion cascades most prototype data; production would usually archive or legally retain records instead.

### User
Extends Django `AbstractUser` with `organization` and `role`. This keeps authentication compatible with Django and JWT while making tenant and role available on every request. `organization` uses `PROTECT` so users cannot be orphaned by accidental tenant deletion.

### DataSource
Registers SAP, utility, or travel sources per organization. It gives ingestion runs a stable configuration boundary instead of treating every file as ad hoc. The source enum is intentionally narrow because the assignment locks three source types; production would add source versioning and owner metadata.

### IngestionRun
Represents one uploaded file. It tracks status and row counts so analysts can distinguish batch health from row-level failures. `data_source` and `uploaded_by` use `PROTECT` to preserve accountability.

### RawRecord
Stores the immutable parsed CSV row in JSON with row number, validation errors, and content hash. It is immutable so downstream transformations can always be traced back to exactly what was received. The tradeoff is larger storage; production would move raw files to object storage and keep this row ledger in PostgreSQL.

### NormalizedRecord
Stores canonical ESG activity: source type, scope, category, canonical quantity/unit, emission estimate, suspicion flags, and review status. Every row has a `OneToOneField` to `RawRecord` to enforce source traceability. Source-specific details remain in `normalized_payload` because SAP fuel, utility billing, and travel differ materially.

### AuditLog
Append-only history of field changes and workflow transitions. It has no soft delete because audit records should not disappear or be overwritten. The ORM blocks updates and deletes; production would also enforce this with database triggers and restricted DB roles.

### ApprovalAction
Immutable analyst decisions per normalized record. It is separated from `AuditLog` because workflow intent is a business event, while audit entries are field-level evidence. Approval actions use `PROTECT` on the record and actor.

### EmissionFactor
Stores scope, category, factor value, unit, source, and effective dates. It supports Scope 1 fuel, Scope 2 electricity, and Scope 3 Category 6 business travel. The prototype keeps factors tenant-scoped; production might also support globally managed factor libraries.

### Facility
Physical location used for plant-code resolution and utility association. It is scoped by organization and uses country/city metadata sufficient for this prototype.

### PlantMapping
Maps SAP plant codes to facilities. It exists because SAP exports often use plant codes that are meaningful only inside ERP configuration. `facility` uses `PROTECT` so mappings cannot silently point to deleted locations.

## Multi-Tenancy

Tenant isolation is enforced at queryset level through API base mixins and service filters that always constrain by `request.user.organization`. Records also carry `organization_id` directly on query-heavy tables so common list queries do not rely on deep joins. This prototype excludes cross-tenant admin views.

## Immutability

`RawRecord`, `AuditLog`, and `ApprovalAction` reject updates through model `save()`. `AuditLog.delete()` raises. `NormalizedRecord` rejects any update once its persisted status is `locked`. This is intentionally implemented in Django for prototype portability; production would add PostgreSQL triggers, row-level permissions, and tamper-evident log export.

## Normalization

SAP quantities normalize to liters, utility electricity normalizes to kWh, and travel normalizes to km by subcategory where distance matters. Scope mapping is explicit: combustion fuel is Scope 1, electricity is Scope 2, and business travel is Scope 3 Category 6.

## Indexes

`IngestionRun(org, created_at)` supports the dashboard and runs page, which list recent uploads per tenant.

`RawRecord(ingestion_run, row_number)` supports deterministic run-detail row review and enforces run-local row uniqueness.

`NormalizedRecord(org, status, source_type)` supports the review queue filters used by analysts.

`AuditLog(record_id, created_at)` supports chronological audit timelines for record detail and audit pages.

`NormalizedRecord(is_suspicious)` partial index where true supports the flagged-review workflow without indexing the common false value.

Additional pragmatic indexes on facility, factor, and organization/date fields support lookup-heavy services.

## Deliberate Simplifications

The prototype does not implement S3, asynchronous workers, or database triggers. It also keeps source-specific normalized attributes in JSON rather than fully modeling every source-specific column. These choices keep the prototype deployable and reviewable while preserving the main architecture contracts.
