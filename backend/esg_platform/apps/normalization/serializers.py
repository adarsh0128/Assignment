from rest_framework import serializers

from esg_platform.apps.normalization.models import EmissionFactor, NormalizedRecord


class EmissionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactor
        fields = [
            "id",
            "scope",
            "category",
            "factor_value",
            "factor_unit",
            "source",
            "effective_from",
            "effective_to",
        ]


class NormalizedRecordSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.name", read_only=True)
    raw_payload = serializers.JSONField(source="raw_record.payload", read_only=True)

    class Meta:
        model = NormalizedRecord
        fields = [
            "id",
            "raw_record",
            "ingestion_run",
            "data_source",
            "facility",
            "facility_name",
            "source_type",
            "category",
            "scope",
            "activity_date",
            "canonical_quantity",
            "canonical_unit",
            "co2e_kg",
            "source_reference",
            "normalized_payload",
            "status",
            "is_suspicious",
            "suspicion_reasons",
            "raw_payload",
            "locked_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
