from django.conf import settings
from django.db import models


class DataSource(models.Model):
    class SourceType(models.TextChoices):
        SAP = "sap", "SAP fuel and procurement"
        UTILITY = "utility", "Utility electricity"
        TRAVEL = "travel", "Corporate travel"

    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="data_sources"
    )
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "source_type", "name"], name="datasource_org_type_name_uniq"
            )
        ]
        indexes = [models.Index(fields=["organization", "source_type"], name="datasource_org_type_idx")]

    def __str__(self) -> str:
        return self.name


class IngestionRun(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        COMPLETED_WITH_ERRORS = "completed_with_errors", "Completed with errors"
        FAILED = "failed", "Failed"

    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="ingestion_runs"
    )
    data_source = models.ForeignKey(
        DataSource, on_delete=models.PROTECT, related_name="ingestion_runs"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ingestion_runs"
    )
    source_type = models.CharField(max_length=20, choices=DataSource.SourceType.choices)
    original_filename = models.CharField(max_length=255)
    stored_file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.RECEIVED)
    total_rows = models.PositiveIntegerField(default=0)
    valid_rows = models.PositiveIntegerField(default=0)
    invalid_rows = models.PositiveIntegerField(default=0)
    suspicious_rows = models.PositiveIntegerField(default=0)
    error_summary = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "-created_at"], name="run_org_created_idx"),
            models.Index(fields=["organization", "status"], name="run_org_status_idx"),
        ]
        ordering = ["-created_at"]


class RawRecord(models.Model):
    ingestion_run = models.ForeignKey(
        IngestionRun, on_delete=models.CASCADE, related_name="raw_records"
    )
    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="raw_records"
    )
    row_number = models.PositiveIntegerField()
    payload = models.JSONField()
    validation_errors = models.JSONField(default=list, blank=True)
    content_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingestion_run", "row_number"], name="raw_run_row_uniq"
            )
        ]
        indexes = [
            models.Index(fields=["ingestion_run", "row_number"], name="raw_run_row_idx"),
            models.Index(fields=["organization", "created_at"], name="raw_org_created_idx"),
        ]
        ordering = ["row_number"]

    def save(self, *args, **kwargs):
        if self.pk and RawRecord.objects.filter(pk=self.pk).exists():
            raise ValueError("Raw records are immutable after creation")
        super().save(*args, **kwargs)
