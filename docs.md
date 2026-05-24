# ESG Data Platform — Architecture & Domain Model

## Overview

This platform ingests ESG-related operational data from multiple enterprise systems, normalizes it into a unified emissions-ready format, and provides a structured analyst review workflow before records become audit-locked.

The platform is purpose-built to handle the realities of enterprise sustainability data: inconsistent formats, fragmented source systems, missing values, and the non-negotiable requirement for defensible audit trails under frameworks like GHG Protocol, CDP, and ISO 14064.

### Design Pillars

| Pillar                      | Description                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------- |
| **Traceability**            | Every record links back to its origin: raw row → ingestion run → source system     |
| **Auditability**            | All changes are immutably logged with actor, timestamp, before/after values        |
| **Source Preservation**     | Raw data is never modified or overwritten                                          |
| **Normalization Pipeline**  | Units, categories, and scopes are resolved during a controlled transformation step |
| **Analyst Review Workflow** | Human review gates record approval before data enters reporting                    |

The architecture deliberately prioritizes **explainability over complexity**. Every design decision has a traceable rationale.

---

# Core Design Principles

## 1. Preserve Raw Data

Enterprise ESG data is inherently messy. SAP exports, utility CSVs, and travel reports arrive with:

- Inconsistent units (gallons vs. liters, kWh vs. MWh, miles vs. km)
- Missing or ambiguous values (blank cells, null quantities)
- Non-standard or system-specific headers (e.g., `ANLZA`, `PRCTR`, `KOSTL`)
- Records requiring contextual interpretation (e.g., cost-center-to-facility mapping)

**Raw source data is never overwritten.** Normalized records are generated as separate, derived entities. This mirrors battle-tested ETL and data warehouse patterns — a staging layer exists precisely to absorb source imperfections without contaminating downstream reporting.

Benefits of this separation:

- Source truth is always recoverable
- Normalization bugs can be corrected by reprocessing without data loss
- Analysts can inspect what actually arrived vs. what the system interpreted
- Auditors get a defensible, unmodified source record

---

## 2. Multi-Tenant Isolation

The platform supports multiple independent organizations (tenants) sharing the same infrastructure.

Every major entity carries an `organization_id` foreign key, ensuring:

- Queries are always scoped to a single tenant
- Cross-tenant data leakage is prevented at the data model level
- The platform scales horizontally by adding tenants, not deployments

**Prototype approach:** Shared database with row-level tenant isolation via `organization_id` predicates on all queries.

**Production-grade alternatives:**

| Strategy                      | Trade-offs                                                |
| ----------------------------- | --------------------------------------------------------- |
| Row-level isolation (current) | Simple to operate; requires disciplined query enforcement |
| Schema-per-tenant             | Better isolation; slightly more complex migrations        |
| Database-per-tenant           | Strongest isolation; highest operational overhead         |

---

## 3. Immutable Auditability

ESG data is audit-sensitive. Regulatory frameworks, third-party verifiers, and internal compliance teams require proof that:

- What was reported matches what was ingested
- Any changes were made intentionally, by an identified actor, at a known time
- No records were silently modified after approval

**Once an analyst approves a record, it becomes locked.** Any subsequent edit requires:

1. An explicit unlock action (with justification)
2. An `AuditLog` entry capturing:
   - The actor (who made the change)
   - The timestamp
   - The previous value
   - The new value

This creates a fully defensible audit history that can withstand external scrutiny.

---

# Entity Relationship Map

```
Organization ──────────────────────────────────────────────────┐
     │                                                          │
     ├──► User (role: admin | analyst | viewer)                │
     │                                                          │
     ├──► DataSource (SAP | Utility | Travel | Manual)         │
     │         │                                               │
     │         └──► IngestionRun ──► RawRecord                 │
     │                                    │                    │
     │                                    ▼                    │
     ├──────────────────────────► NormalizedRecord ◄──── EmissionFactor
     │                                    │
     │                           ┌────────┼────────────┐
     │                           ▼        ▼            ▼
     │                      AuditLog  ApprovalAction  (locked)
     │
     ├──► Facility
     │         ▲
     └──► PlantMapping (SAP plant code → Facility)
```

---

# Entity Reference

---

## Organization

Represents a company or business unit using the platform.

### Fields

| Field        | Type     | Notes                            |
| ------------ | -------- | -------------------------------- |
| `id`         | UUID     | Primary key                      |
| `name`       | string   | Display name of the organization |
| `created_at` | datetime | Account creation timestamp       |

### Design Notes

- Top-level tenant entity; referenced by all other entities via `organization_id`
- Supports future per-tenant configuration (e.g., custom emission factors, regional settings)
- In a production system, would link to billing, subscription tier, and SSO configuration

---

## User

Application users who interact with the platform.

### Fields

| Field             | Type              | Notes                                      |
| ----------------- | ----------------- | ------------------------------------------ |
| `id`              | UUID              | Primary key                                |
| `organization_id` | FK → Organization | Tenant scoping                             |
| `email`           | string            | Unique within the platform; used for login |
| `role`            | enum              | Determines permissions (see below)         |
| `created_at`      | datetime          | Account creation timestamp                 |

### Roles

| Role      | Permissions                                            |
| --------- | ------------------------------------------------------ |
| `admin`   | Manage users, configure data sources, view all records |
| `analyst` | Review, approve, reject, and flag normalized records   |
| `viewer`  | Read-only access to approved records and reports       |

### Design Notes

- `actor_id` in `AuditLog` and `analyst_id` in `ApprovalAction` reference this entity
- Future RBAC expansion: per-facility permissions, per-scope visibility, delegation chains
- Production systems would integrate with SSO/SAML for enterprise identity providers

---

## DataSource

Represents a configured integration point or ingestion channel.

### Examples

| Source Type     | Description                               |
| --------------- | ----------------------------------------- |
| `sap_fuel`      | Diesel/fuel consumption exports from SAP  |
| `utility_csv`   | Energy usage files from utility providers |
| `concur_travel` | Business travel reports from Concur       |
| `manual_upload` | Ad hoc CSV uploads from internal teams    |

### Fields

| Field             | Type              | Notes                                                                   |
| ----------------- | ----------------- | ----------------------------------------------------------------------- |
| `id`              | UUID              | Primary key                                                             |
| `organization_id` | FK → Organization | Tenant scoping                                                          |
| `source_type`     | enum              | Determines normalization pipeline to apply                              |
| `display_name`    | string            | Human-readable label (e.g., "UK Electricity — National Grid")           |
| `config_json`     | JSON              | Source-specific configuration (column mappings, unit assumptions, etc.) |
| `created_at`      | datetime          | Source registration timestamp                                           |

### Design Notes

- `config_json` stores source-specific parsing configuration:
  - Column name mappings for non-standard headers
  - Default unit assumptions when unit column is absent
  - Facility/cost center resolution overrides
- One `DataSource` can produce many `IngestionRun` records over time
- Future: webhook endpoints for automated ingestion triggers

---

## IngestionRun

Represents a single file upload or import event from a data source.

### Fields

| Field             | Type              | Notes                                        |
| ----------------- | ----------------- | -------------------------------------------- |
| `id`              | UUID              | Primary key                                  |
| `organization_id` | FK → Organization | Tenant scoping                               |
| `data_source_id`  | FK → DataSource   | Which source produced this run               |
| `uploaded_by`     | FK → User         | Who triggered the upload                     |
| `status`          | enum              | Current processing state                     |
| `file_name`       | string            | Original filename for reference              |
| `total_rows`      | integer           | Total rows parsed from source file           |
| `failed_rows`     | integer           | Rows that failed validation or normalization |
| `created_at`      | datetime          | Upload timestamp                             |

### Status Lifecycle

```
uploaded → processing → completed
                     ↘ partial_failure
                     ↘ failed
```

| Status            | Meaning                                            |
| ----------------- | -------------------------------------------------- |
| `uploaded`        | File received; processing not yet started          |
| `processing`      | Normalization pipeline running                     |
| `completed`       | All rows processed successfully                    |
| `partial_failure` | Some rows failed; successful rows still normalized |
| `failed`          | Fatal error; no rows normalized                    |

### Design Notes

- `failed_rows > 0` with `status = partial_failure` signals rows that need manual review
- Provides operational visibility: which uploads are stuck, which failed silently
- Enables partial reprocessing: failed rows can be corrected and re-ingested without re-uploading successful rows
- Future: async status polling via Celery tasks with webhook callbacks on completion

---

## RawRecord

Stores the untouched, verbatim content of each source row.

### Fields

| Field               | Type              | Notes                                              |
| ------------------- | ----------------- | -------------------------------------------------- |
| `id`                | UUID              | Primary key                                        |
| `ingestion_run_id`  | FK → IngestionRun | Links to the upload event                          |
| `source_row_number` | integer           | Original row position in the source file           |
| `raw_payload`       | JSON              | Complete, unmodified source row as key-value pairs |
| `validation_errors` | JSON              | List of detected issues during initial parsing     |
| `created_at`        | datetime          | Record creation timestamp                          |

### Example `raw_payload`

```json
{
  "WERKS": "1042",
  "MENGE": "450",
  "MEINS": "GAL",
  "BUDAT": "2024-03-15",
  "KOSTL": "MAINT-EU-07"
}
```

### Example `validation_errors`

```json
[
  {
    "field": "MEINS",
    "issue": "Unit 'GAL' requires conversion to canonical unit 'L'"
  },
  {
    "field": "KOSTL",
    "issue": "Cost center 'MAINT-EU-07' not found in PlantMapping"
  }
]
```

### Design Notes

- `raw_payload` is immutable — never modified after creation
- `source_row_number` allows precise source tracing: "Row 147 of invoice_march_2024.csv"
- `validation_errors` are non-blocking by default; the normalization pipeline records issues but continues
- Enables reprocessing: if a normalization bug is discovered, the pipeline can replay against existing `RawRecord` rows without re-upload

---

## NormalizedRecord

The canonical, ESG-ready representation of a single activity record.

### Fields

| Field                | Type                | Notes                                                                        |
| -------------------- | ------------------- | ---------------------------------------------------------------------------- |
| `id`                 | UUID                | Primary key                                                                  |
| `organization_id`    | FK → Organization   | Tenant scoping; enables direct org-level queries                             |
| `raw_record_id`      | FK → RawRecord      | Source traceability link                                                     |
| `category`           | enum                | High-level activity category                                                 |
| `scope`              | enum                | GHG Protocol scope assignment                                                |
| `activity_type`      | string              | Specific activity descriptor (e.g., "diesel combustion", "grid electricity") |
| `quantity`           | decimal             | Activity quantity in normalized units                                        |
| `normalized_unit`    | string              | Canonical unit (e.g., "L", "kWh", "km")                                      |
| `normalized_value`   | decimal             | Quantity after unit conversion                                               |
| `emission_factor_id` | FK → EmissionFactor | Factor used to compute CO₂e                                                  |
| `co2e`               | decimal             | Computed CO₂ equivalent emissions (tCO₂e)                                    |
| `status`             | enum                | Analyst workflow state                                                       |
| `suspicious`         | boolean             | Flagged by anomaly detection rules                                           |
| `locked`             | boolean             | True once approved; prevents silent edits                                    |
| `created_at`         | datetime            | Record creation timestamp                                                    |

### Category Values

| Category       | Examples                                |
| -------------- | --------------------------------------- |
| `fuel`         | Diesel, petrol, natural gas consumption |
| `electricity`  | Grid electricity, renewable purchases   |
| `travel`       | Flights, rail, vehicle mileage          |
| `waste`        | Landfill, recycling, incineration       |
| `refrigerants` | HFC leakage, cooling system losses      |

### Scope Values

| Scope     | Definition                                        | Examples                             |
| --------- | ------------------------------------------------- | ------------------------------------ |
| `scope_1` | Direct emissions (owned/controlled sources)       | Fuel combustion, company vehicles    |
| `scope_2` | Purchased energy (location-based or market-based) | Grid electricity, district heating   |
| `scope_3` | Indirect value chain emissions                    | Business travel, supply chain, waste |

### Status Lifecycle

```
pending → flagged → approved → (locked)
       ↘           ↘ rejected
```

| Status     | Meaning                                                    |
| ---------- | ---------------------------------------------------------- |
| `pending`  | Awaiting analyst review                                    |
| `flagged`  | Anomaly detected; requires analyst investigation           |
| `approved` | Analyst confirmed; eligible for locking                    |
| `rejected` | Excluded from reporting; reason captured in ApprovalAction |

### Design Notes

- `organization_id` is denormalized here (also reachable via `raw_record_id → IngestionRun → organization_id`) for query efficiency
- `locked = true` is set post-approval; subsequent edits require an audit trail entry
- `suspicious = true` does not block processing; it routes the record to the analyst queue
- `co2e` is always stored in tonnes CO₂ equivalent (tCO₂e) regardless of source unit

---

## EmissionFactor

Reference table of emissions conversion factors used to calculate CO₂ equivalent.

### Fields

| Field              | Type    | Notes                                                     |
| ------------------ | ------- | --------------------------------------------------------- |
| `id`               | UUID    | Primary key                                               |
| `factor_name`      | string  | Human-readable name (e.g., "DEFRA 2023 — Diesel, UK")     |
| `category`         | string  | Activity category this factor applies to                  |
| `unit`             | string  | Unit the factor applies to (e.g., "L", "kWh")             |
| `co2e_factor`      | decimal | kgCO₂e per unit of activity                               |
| `source_reference` | string  | Citation (e.g., "DEFRA 2023 GHG Conversion Factors v1.2") |

### Example Records

| factor_name                 | category    | unit | co2e_factor | source_reference |
| --------------------------- | ----------- | ---- | ----------- | ---------------- |
| Diesel — UK 2023            | fuel        | L    | 2.6789      | DEFRA 2023       |
| Grid Electricity — UK 2023  | electricity | kWh  | 0.2307      | DEFRA 2023       |
| Short-haul Flight — Economy | travel      | km   | 0.1551      | DEFRA 2023       |

### Design Notes

- Decoupled from `NormalizedRecord` to allow factor updates without rewriting activity records
- `source_reference` ensures factors are traceable to published, verifiable datasets
- Future: factor versioning (time-bound validity ranges), regionalization (country/grid-specific factors), market-based vs. location-based electricity factors

---

## AuditLog

Immutable, append-only record of every significant action taken on a `NormalizedRecord`.

### Fields

| Field                  | Type                  | Notes                      |
| ---------------------- | --------------------- | -------------------------- |
| `id`                   | UUID                  | Primary key                |
| `normalized_record_id` | FK → NormalizedRecord | Record being tracked       |
| `actor_id`             | FK → User             | Who performed the action   |
| `action_type`          | enum                  | Type of change (see below) |
| `previous_value`       | JSON                  | State before the action    |
| `new_value`            | JSON                  | State after the action     |
| `created_at`           | datetime              | When the action occurred   |

### Action Types

| Action     | When it fires                                  |
| ---------- | ---------------------------------------------- |
| `created`  | NormalizedRecord first generated from raw data |
| `edited`   | Any field on the record is modified            |
| `approved` | Analyst marks the record as approved           |
| `rejected` | Analyst marks the record as rejected           |
| `locked`   | Record transitions to immutable state          |

### Example AuditLog Entry

```json
{
  "action_type": "edited",
  "actor_id": "user-uuid-analyst-1",
  "previous_value": { "quantity": 450, "normalized_unit": "L", "co2e": 1205.5 },
  "new_value": { "quantity": 1704, "normalized_unit": "L", "co2e": 4561.7 },
  "created_at": "2024-03-20T14:33:00Z"
}
```

### Design Notes

- Records are never deleted or modified — append-only by design
- `previous_value` and `new_value` store field-level diffs as JSON for flexibility
- Enables complete reconstruction of a record's history at any point in time
- Required for regulatory defensibility: auditors can see exactly what changed, when, and by whom

---

## ApprovalAction

Tracks explicit analyst decisions in the review workflow.

### Fields

| Field                  | Type                  | Notes                                      |
| ---------------------- | --------------------- | ------------------------------------------ |
| `id`                   | UUID                  | Primary key                                |
| `normalized_record_id` | FK → NormalizedRecord | Record being reviewed                      |
| `analyst_id`           | FK → User             | Analyst making the decision                |
| `decision`             | enum                  | Outcome of the review                      |
| `comment`              | text                  | Analyst's free-text justification or notes |
| `created_at`           | datetime              | Decision timestamp                         |

### Decisions

| Decision  | Meaning                                                     |
| --------- | ----------------------------------------------------------- |
| `approve` | Record is valid; include in reporting                       |
| `reject`  | Record is invalid or duplicate; exclude from reporting      |
| `flag`    | Record needs further investigation; return to pending queue |

### Design Notes

- Intentionally separate from `AuditLog` to cleanly distinguish **business workflow decisions** from **system change events**
- `comment` field provides human context essential for audit narratives ("Rejected: duplicate entry, already captured in SAP run 2024-Q1-003")
- A record can have multiple `ApprovalAction` rows if it is flagged, revised, and re-reviewed

---

## Facility

Represents a physical location or operational site.

### Fields

| Field             | Type              | Notes                                                        |
| ----------------- | ----------------- | ------------------------------------------------------------ |
| `id`              | UUID              | Primary key                                                  |
| `organization_id` | FK → Organization | Tenant scoping                                               |
| `facility_name`   | string            | Human-readable name (e.g., "Manchester Distribution Centre") |
| `country`         | string            | ISO 3166-1 alpha-2 country code                              |
| `facility_code`   | string            | Internal identifier for cross-system reference               |

### Design Notes

- Utility and fuel records map to facilities to enable site-level emissions reporting
- `country` supports region-specific emission factor selection in future enhancements
- `facility_code` serves as a stable internal reference that can be matched across source systems
- Future: geo-coordinates, regional grid assignments, facility-level emission targets

---

## PlantMapping

SAP-specific lookup table resolving cryptic plant codes to known Facility records.

### Fields

| Field             | Type              | Notes                                                            |
| ----------------- | ----------------- | ---------------------------------------------------------------- |
| `id`              | UUID              | Primary key                                                      |
| `organization_id` | FK → Organization | Tenant scoping                                                   |
| `sap_plant_code`  | string            | Raw plant identifier as it appears in SAP exports (e.g., "1042") |
| `facility_id`     | FK → Facility     | Resolved platform facility                                       |

### Design Notes

- SAP exports frequently use numeric or cryptic plant codes with no human-readable label in the file
- Without this mapping, normalization cannot assign records to the correct facility
- Analogous patterns apply to other systems: Concur department codes, Oracle cost centers, etc.
- In production, this would be generalized into a `SourceCodeMapping` table with a `source_type` discriminator

---

# Data Flow: End-to-End Lifecycle

```
[Source System]
      │
      │  CSV / export file
      ▼
[Upload Event]
  IngestionRun created (status: uploaded)
      │
      ▼
[Parsing Layer]
  For each row → RawRecord created (raw_payload = verbatim row)
  Validation errors stored in validation_errors[]
      │
      ▼
[Normalization Pipeline]
  Unit conversion (GAL → L, MWh → kWh, miles → km)
  Scope assignment (Scope 1 / 2 / 3)
  Category classification
  PlantMapping resolution (SAP plant code → Facility)
  EmissionFactor lookup
  CO₂e calculation
  Anomaly detection (suspicious = true/false)
      │
      ▼
[NormalizedRecord created]
  status: pending  (or flagged if suspicious)
      │
      ▼
[Analyst Review Queue]
  Analyst views flagged / pending records
  May edit values (AuditLog entry written)
  Makes decision: approve / reject / flag
  ApprovalAction created
      │
      ▼
[Locking]
  Approved records → locked = true
  Immutable from this point forward
      │
      ▼
[Reporting Layer]
  Query approved, locked NormalizedRecords
  Aggregate by scope / category / facility / period
  Export for GHG reporting, CDP submission, etc.
```

---

# Source Traceability Strategy

Every normalized record maintains a complete, unbroken lineage chain:

```
NormalizedRecord
  └── raw_record_id → RawRecord
        └── ingestion_run_id → IngestionRun
              └── data_source_id → DataSource
                    └── organization_id → Organization
```

This chain answers every audit question:

| Audit Question                      | Answered By                 |
| ----------------------------------- | --------------------------- |
| What was the original source value? | `RawRecord.raw_payload`     |
| Which file did this come from?      | `IngestionRun.file_name`    |
| When was it uploaded?               | `IngestionRun.created_at`   |
| Who uploaded it?                    | `IngestionRun.uploaded_by`  |
| What system generated the file?     | `DataSource.source_type`    |
| What changed after normalization?   | `AuditLog` entries          |
| Who approved the final record?      | `ApprovalAction.analyst_id` |

---

# Unit Normalization Strategy

Different source systems report activity data in different units. The normalization pipeline resolves all values to canonical units before storage.

### Normalization Steps

1. **Detect source unit** — read from raw row; fall back to `DataSource.config_json` defaults if absent
2. **Validate compatibility** — confirm the detected unit maps to the expected canonical unit family
3. **Convert** — apply conversion factor to produce canonical quantity
4. **Store** — write both `normalized_value` (converted) and preserve original in `RawRecord.raw_payload`

### Canonical Unit Mapping

| Activity Category | Canonical Unit       | Common Source Units             |
| ----------------- | -------------------- | ------------------------------- |
| Fuel consumption  | Litres (L)           | Gallons (US/UK), kg, cubic feet |
| Electricity usage | Kilowatt-hours (kWh) | MWh, GWh, Joules                |
| Business travel   | Kilometres (km)      | Miles, nautical miles           |
| Refrigerants      | Kilograms (kg)       | lbs, oz                         |
| Waste             | Tonnes (t)           | kg, lbs, short tons             |

### Validation Errors (Non-Blocking)

If a unit cannot be resolved, the row is still stored as a `RawRecord` with a `validation_error` entry. The `NormalizedRecord` is created with `suspicious = true`, routing it to the analyst queue for manual resolution.

---

# Anomaly Detection Rules

The platform applies a rule-based anomaly detection pass during normalization. Records triggering any rule have `suspicious = true` set and are routed to the analyst review queue.

### Current Rules

| Rule              | Description                                                                |
| ----------------- | -------------------------------------------------------------------------- |
| Negative quantity | Activity quantity is zero or negative (e.g., −200 litres of diesel)        |
| Implausible spike | Quantity exceeds N× the rolling average for that facility/activity type    |
| Duplicate invoice | Same invoice/reference number appears in multiple records                  |
| Impossible route  | Flight or travel record between origin/destination with no plausible route |
| Missing unit      | Source row has a quantity but no unit; canonical unit cannot be inferred   |
| Unmapped facility | SAP plant code has no entry in `PlantMapping`                              |

### Design Decision: Rules-Based Only

The prototype intentionally avoids ML-based anomaly detection for two reasons:

1. **Explainability** — Rules produce a clear, human-readable rationale for each flag. Analysts can understand and trust the flagging logic.
2. **Scope** — Statistical models require sufficient historical data and significantly more development effort.

Future enhancement: configurable rule thresholds per organization, per facility, or per activity type.

---

# Analyst Review Workflow

### Record Lifecycle

```
         ┌─────────────────────────────┐
         │                             │
pending ──┼──(anomaly detected)──► flagged
         │                             │
         │◄────────────────────────────┘
         │         (re-queued)
         │
         ├──(analyst approves)──► approved ──► locked
         │
         └──(analyst rejects)──► rejected
```

### Workflow Rules

- Only `analyst` and `admin` role users can make approval decisions
- Approval or rejection always creates an `ApprovalAction` entry
- All edits made during review create `AuditLog` entries
- Once `locked = true`, the record cannot be silently edited
- Locked records require an explicit unlock action (itself audit-logged) to modify

### Analyst Queue Priorities

1. `flagged` records (highest priority — anomaly detected)
2. `pending` records older than N days (configurable SLA)
3. New `pending` records (FIFO)

---

# Scope Classification Logic

Scope assignment follows the GHG Protocol Corporate Standard.

### Classification Rules

| Scope   | Conditions                                            | Examples                                        |
| ------- | ----------------------------------------------------- | ----------------------------------------------- |
| Scope 1 | `category = fuel` AND source is owned/operated        | Diesel in company vehicles, on-site gas boilers |
| Scope 2 | `category = electricity` AND purchased from grid      | Utility bills, site electricity meters          |
| Scope 3 | `category = travel` OR indirect supply chain activity | Flights, rail, hired vehicles                   |

Scope is assigned by the normalization pipeline based on `source_type` and `activity_type`. Analysts can override during review (with AuditLog entry).

---

# Simplifications (Prototype Scope)

This is a prototype built under time and scope constraints. The following are intentionally excluded:

| Excluded Feature                  | Reason                                               |
| --------------------------------- | ---------------------------------------------------- |
| Real SAP API integration          | Requires SAP system access and certified connectors  |
| OCR utility bill extraction       | Complex ML pipeline; out of scope                    |
| Async distributed pipeline        | Celery/Kafka requires significant infrastructure     |
| Regional emission factor datasets | Requires licensed factor databases (DEFRA, EPA, IEA) |
| ML anomaly detection              | Requires historical data and model development       |
| Full RBAC matrix                  | Per-facility, per-scope permissions deferred         |
| SSO/SAML authentication           | Enterprise identity integration deferred             |
| Emissions factor versioning       | Time-bound factor validity deferred                  |

---

# Future Production Roadmap

### Near-Term (Next Quarter)

- **Async ingestion pipeline** — Celery workers for non-blocking file processing; webhook callbacks on completion
- **Configurable anomaly rules** — Organization-level rule thresholds via admin UI
- **Facility-level reporting dashboards** — Aggregated emissions by site, scope, and time period

### Medium-Term

- **dbt transformation layer** — Declarative, version-controlled normalization logic replacing imperative pipeline code
- **OCR utility bill extraction** — Automated extraction from PDF invoices using document AI
- **Emissions factor versioning** — Time-bound validity ranges; automatic factor selection by reporting period

### Long-Term

- **Kafka event pipeline** — Real-time ingestion from connected enterprise systems
- **Warehouse integrations** — Snowflake/BigQuery export for analytics-grade reporting
- **SSO/SAML support** — Enterprise identity provider integration (Okta, Azure AD)
- **Market-based Scope 2 accounting** — EAC/REGO certificate matching for market-based emissions
- **Scope 3 category expansion** — Supply chain, purchased goods, end-of-life treatment
- **API-first ingestion** — REST webhooks for direct integration with SAP, Concur, Oracle
