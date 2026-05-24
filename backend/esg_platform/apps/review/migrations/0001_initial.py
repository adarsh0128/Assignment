import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_initial"),
        ("normalization", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="ApprovalAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("approve", "Approve"), ("reject", "Reject"), ("flag", "Flag"), ("reopen", "Reopen"), ("lock", "Lock")], max_length=20)),
                ("reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="approval_actions", to=settings.AUTH_USER_MODEL)),
                ("normalized_record", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="approval_actions", to="normalization.normalizedrecord")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="approval_actions", to="core.organization")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("field_name", models.CharField(max_length=80)),
                ("old_value", models.JSONField(blank=True, null=True)),
                ("new_value", models.JSONField(blank=True, null=True)),
                ("reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="audit_logs", to=settings.AUTH_USER_MODEL)),
                ("normalized_record", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="audit_logs", to="normalization.normalizedrecord")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="audit_logs", to="core.organization")),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.AddIndex(model_name="approvalaction", index=models.Index(fields=["organization", "created_at"], name="approval_org_created_idx")),
        migrations.AddIndex(model_name="approvalaction", index=models.Index(fields=["normalized_record", "created_at"], name="approval_record_created_idx")),
        migrations.AddIndex(model_name="auditlog", index=models.Index(fields=["normalized_record", "created_at"], name="audit_record_created_idx")),
        migrations.AddIndex(model_name="auditlog", index=models.Index(fields=["organization", "created_at"], name="audit_org_created_idx")),
    ]
