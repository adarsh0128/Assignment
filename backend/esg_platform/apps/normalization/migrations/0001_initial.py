import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("core", "0001_initial"),
        ("ingestion", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="EmissionFactor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope", models.CharField(choices=[("scope_1", "Scope 1"), ("scope_2_market", "Scope 2 market-based"), ("scope_2_location", "Scope 2 location-based"), ("scope_3_cat_6", "Scope 3 Category 6")], max_length=30)),
                ("category", models.CharField(max_length=80)),
                ("factor_value", models.DecimalField(decimal_places=6, max_digits=14)),
                ("factor_unit", models.CharField(max_length=40)),
                ("source", models.CharField(max_length=255)),
                ("effective_from", models.DateField()),
                ("effective_to", models.DateField(blank=True, null=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="emission_factors", to="core.organization")),
            ],
        ),
        migrations.CreateModel(
            name="NormalizedRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_type", models.CharField(max_length=20)),
                ("category", models.CharField(max_length=80)),
                ("scope", models.CharField(max_length=30)),
                ("activity_date", models.DateField()),
                ("canonical_quantity", models.DecimalField(decimal_places=4, max_digits=16)),
                ("canonical_unit", models.CharField(max_length=20)),
                ("co2e_kg", models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ("source_reference", models.CharField(blank=True, max_length=255)),
                ("normalized_payload", models.JSONField(default=dict)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("flagged", "Flagged"), ("approved", "Approved"), ("rejected", "Rejected"), ("locked", "Locked")], default="pending", max_length=20)),
                ("is_suspicious", models.BooleanField(default=False)),
                ("suspicion_reasons", models.JSONField(blank=True, default=list)),
                ("locked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("data_source", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="normalized_records", to="ingestion.datasource")),
                ("emission_factor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="normalized_records", to="normalization.emissionfactor")),
                ("facility", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="normalized_records", to="core.facility")),
                ("ingestion_run", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="normalized_records", to="ingestion.ingestionrun")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="normalized_records", to="core.organization")),
                ("raw_record", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="normalized_record", to="ingestion.rawrecord")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="emissionfactor", index=models.Index(fields=["organization", "scope", "category"], name="factor_lookup_idx")),
        migrations.AddIndex(model_name="normalizedrecord", index=models.Index(fields=["organization", "status", "source_type"], name="norm_org_status_source_idx")),
        migrations.AddIndex(model_name="normalizedrecord", index=models.Index(condition=Q(is_suspicious=True), fields=["is_suspicious"], name="norm_suspicious_true_idx")),
        migrations.AddIndex(model_name="normalizedrecord", index=models.Index(fields=["organization", "activity_date"], name="norm_org_activity_idx")),
        migrations.AddConstraint(model_name="emissionfactor", constraint=models.UniqueConstraint(fields=("organization", "scope", "category", "effective_from"), name="factor_org_scope_category_date_uniq")),
    ]
