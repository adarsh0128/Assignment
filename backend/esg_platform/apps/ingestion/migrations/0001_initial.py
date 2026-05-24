import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="DataSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("source_type", models.CharField(choices=[("sap", "SAP fuel and procurement"), ("utility", "Utility electricity"), ("travel", "Corporate travel")], max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_sources", to="core.organization")),
            ],
        ),
        migrations.CreateModel(
            name="IngestionRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_type", models.CharField(choices=[("sap", "SAP fuel and procurement"), ("utility", "Utility electricity"), ("travel", "Corporate travel")], max_length=20)),
                ("original_filename", models.CharField(max_length=255)),
                ("stored_file", models.FileField(upload_to="uploads/%Y/%m/%d/")),
                ("status", models.CharField(choices=[("received", "Received"), ("processing", "Processing"), ("completed", "Completed"), ("completed_with_errors", "Completed with errors"), ("failed", "Failed")], default="received", max_length=30)),
                ("total_rows", models.PositiveIntegerField(default=0)),
                ("valid_rows", models.PositiveIntegerField(default=0)),
                ("invalid_rows", models.PositiveIntegerField(default=0)),
                ("suspicious_rows", models.PositiveIntegerField(default=0)),
                ("error_summary", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("data_source", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ingestion_runs", to="ingestion.datasource")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ingestion_runs", to="core.organization")),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ingestion_runs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RawRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("row_number", models.PositiveIntegerField()),
                ("payload", models.JSONField()),
                ("validation_errors", models.JSONField(blank=True, default=list)),
                ("content_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("ingestion_run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="raw_records", to="ingestion.ingestionrun")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="raw_records", to="core.organization")),
            ],
            options={"ordering": ["row_number"]},
        ),
        migrations.AddIndex(model_name="datasource", index=models.Index(fields=["organization", "source_type"], name="datasource_org_type_idx")),
        migrations.AddIndex(model_name="ingestionrun", index=models.Index(fields=["organization", "-created_at"], name="run_org_created_idx")),
        migrations.AddIndex(model_name="ingestionrun", index=models.Index(fields=["organization", "status"], name="run_org_status_idx")),
        migrations.AddIndex(model_name="rawrecord", index=models.Index(fields=["ingestion_run", "row_number"], name="raw_run_row_idx")),
        migrations.AddIndex(model_name="rawrecord", index=models.Index(fields=["organization", "created_at"], name="raw_org_created_idx")),
        migrations.AddConstraint(model_name="datasource", constraint=models.UniqueConstraint(fields=("organization", "source_type", "name"), name="datasource_org_type_name_uniq")),
        migrations.AddConstraint(model_name="rawrecord", constraint=models.UniqueConstraint(fields=("ingestion_run", "row_number"), name="raw_run_row_uniq")),
    ]
