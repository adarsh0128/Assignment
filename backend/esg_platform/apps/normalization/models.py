from decimal import Decimal

from django.db import models
from django.db.models import Q


class EmissionFactor(models.Model):
    class Scope(models.TextChoices):
        SCOPE_1 = "scope_1", "Scope 1"
        SCOPE_2_MARKET = "scope_2_market", "Scope 2 market-based"
        SCOPE_2_LOCATION = "scope_2_location", "Scope 2 location-based"
        SCOPE_3_CAT_6 = "scope_3_cat_6", "Scope 3 Category 6"

    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="emission_factors"
    )
    scope = models.CharField(max_length=30, choices=Scope.choices)
    category = models.CharField(max_length=80)
    factor_value = models.DecimalField(max_digits=14, decimal_places=6)
    factor_unit = models.CharField(max_length=40)
    source = models.CharField(max_length=255)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "scope", "category", "effective_from"],
                name="factor_org_scope_category_date_uniq",
            )
        ]
        indexes = [models.Index(fields=["organization", "scope", "category"], name="factor_lookup_idx")]


class NormalizedRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        FLAGGED = "flagged", "Flagged"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        LOCKED = "locked", "Locked"

    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="normalized_records"
    )
    raw_record = models.OneToOneField(
        "ingestion.RawRecord", on_delete=models.PROTECT, related_name="normalized_record"
    )
    ingestion_run = models.ForeignKey(
        "ingestion.IngestionRun", on_delete=models.PROTECT, related_name="normalized_records"
    )
    data_source = models.ForeignKey(
        "ingestion.DataSource", on_delete=models.PROTECT, related_name="normalized_records"
    )
    facility = models.ForeignKey(
        "core.Facility", on_delete=models.SET_NULL, related_name="normalized_records", null=True, blank=True
    )
    emission_factor = models.ForeignKey(
        EmissionFactor, on_delete=models.PROTECT, related_name="normalized_records", null=True, blank=True
    )
    source_type = models.CharField(max_length=20)
    category = models.CharField(max_length=80)
    scope = models.CharField(max_length=30)
    activity_date = models.DateField()
    canonical_quantity = models.DecimalField(max_digits=16, decimal_places=4)
    canonical_unit = models.CharField(max_length=20)
    co2e_kg = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))
    source_reference = models.CharField(max_length=255, blank=True)
    normalized_payload = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_suspicious = models.BooleanField(default=False)
    suspicion_reasons = models.JSONField(default=list, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status", "source_type"], name="norm_org_status_source_idx"),
            models.Index(
                fields=["is_suspicious"],
                name="norm_suspicious_true_idx",
                condition=Q(is_suspicious=True),
            ),
            models.Index(fields=["organization", "activity_date"], name="norm_org_activity_idx"),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk:
            current = NormalizedRecord.objects.get(pk=self.pk)
            if current.status == self.Status.LOCKED:
                raise ValueError("Locked normalized records are immutable")
        super().save(*args, **kwargs)
