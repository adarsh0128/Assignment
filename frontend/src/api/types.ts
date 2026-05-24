export type SourceType = "sap" | "utility" | "travel";
export type RecordStatus = "pending" | "flagged" | "approved" | "rejected" | "locked";

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DataSource {
  id: number;
  name: string;
  source_type: SourceType;
  is_active: boolean;
}

export interface IngestionRun {
  id: number;
  data_source: number;
  data_source_name: string;
  source_type: SourceType;
  original_filename: string;
  status: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  suspicious_rows: number;
  error_summary: Array<{ row_number: number; errors: string[] }>;
  created_at: string;
  completed_at: string | null;
}

export interface NormalizedRecord {
  id: number;
  raw_record: number;
  ingestion_run: number;
  data_source: number;
  facility_name: string | null;
  source_type: SourceType;
  category: string;
  scope: string;
  activity_date: string;
  canonical_quantity: string;
  canonical_unit: string;
  co2e_kg: string;
  source_reference: string;
  normalized_payload: Record<string, unknown>;
  raw_payload: Record<string, unknown>;
  status: RecordStatus;
  is_suspicious: boolean;
  suspicion_reasons: string[];
  locked_at: string | null;
}

export interface AuditLog {
  id: number;
  normalized_record: number;
  field_name: string;
  old_value: unknown;
  new_value: unknown;
  actor_username: string;
  reason: string;
  created_at: string;
}

export interface Dashboard {
  total_runs: number;
  pending_reviews: number;
  flagged_rows: number;
  approved_this_week: number;
  recent_runs: IngestionRun[];
}
