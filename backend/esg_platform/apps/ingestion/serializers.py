from rest_framework import serializers

from esg_platform.apps.ingestion.models import DataSource, IngestionRun, RawRecord


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ["id", "name", "source_type", "is_active", "created_at"]


class IngestionRunSerializer(serializers.ModelSerializer):
    data_source_name = serializers.CharField(source="data_source.name", read_only=True)

    class Meta:
        model = IngestionRun
        fields = [
            "id",
            "data_source",
            "data_source_name",
            "source_type",
            "original_filename",
            "status",
            "total_rows",
            "valid_rows",
            "invalid_rows",
            "suspicious_rows",
            "error_summary",
            "created_at",
            "completed_at",
        ]
        read_only_fields = [
            "source_type",
            "original_filename",
            "status",
            "total_rows",
            "valid_rows",
            "invalid_rows",
            "suspicious_rows",
            "error_summary",
            "created_at",
            "completed_at",
        ]


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = ["id", "row_number", "payload", "validation_errors", "content_hash", "created_at"]


class UploadSerializer(serializers.Serializer):
    data_source = serializers.IntegerField()
    file = serializers.FileField()
