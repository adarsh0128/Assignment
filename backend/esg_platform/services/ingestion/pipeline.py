import hashlib
import json

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from esg_platform.apps.ingestion.models import IngestionRun, RawRecord
from esg_platform.services.ingestion.parse_csv import parse_csv
from esg_platform.services.ingestion.validate_schema import validate_row
from esg_platform.services.normalization.normalizers import build_record


def _row_hash(row: dict[str, str]) -> str:
    encoded = json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def process_upload(organization, user, data_source, uploaded_file) -> IngestionRun:
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    run = IngestionRun.objects.create(
        organization=organization,
        data_source=data_source,
        uploaded_by=user,
        source_type=data_source.source_type,
        original_filename=uploaded_file.name,
        stored_file=ContentFile(file_bytes, name=uploaded_file.name),
        status=IngestionRun.Status.PROCESSING,
    )
    rows = parse_csv(uploaded_file)
    total = len(rows)
    valid = invalid = suspicious = 0
    errors = []
    with transaction.atomic():
        for index, row in enumerate(rows, start=2):
            row_errors = validate_row(data_source.source_type, row)
            raw = RawRecord.objects.create(
                ingestion_run=run,
                organization=organization,
                row_number=index,
                payload=row,
                validation_errors=row_errors,
                content_hash=_row_hash(row),
            )
            if row_errors:
                invalid += 1
                errors.append({"row_number": index, "errors": row_errors})
                continue
            try:
                normalized = build_record(raw)
                normalized.save()
                valid += 1
                if normalized.is_suspicious:
                    suspicious += 1
            except Exception as exc:
                invalid += 1
                errors.append({"row_number": index, "errors": [str(exc)]})
        run.total_rows = total
        run.valid_rows = valid
        run.invalid_rows = invalid
        run.suspicious_rows = suspicious
        run.error_summary = errors[:100]
        run.status = (
            IngestionRun.Status.COMPLETED
            if invalid == 0
            else IngestionRun.Status.COMPLETED_WITH_ERRORS
        )
        run.completed_at = timezone.now()
        run.save(update_fields=[
            "total_rows",
            "valid_rows",
            "invalid_rows",
            "suspicious_rows",
            "error_summary",
            "status",
            "completed_at",
        ])
    return run
