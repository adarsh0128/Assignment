from django.conf import settings
from django.db import models


class ApprovalAction(models.Model):
    class Action(models.TextChoices):
        APPROVE = "approve", "Approve"
        REJECT = "reject", "Reject"
        FLAG = "flag", "Flag"
        REOPEN = "reopen", "Reopen"
        LOCK = "lock", "Lock"

    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="approval_actions"
    )
    normalized_record = models.ForeignKey(
        "normalization.NormalizedRecord", on_delete=models.PROTECT, related_name="approval_actions"
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approval_actions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "created_at"], name="approval_org_created_idx"),
            models.Index(fields=["normalized_record", "created_at"], name="approval_record_created_idx"),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk and ApprovalAction.objects.filter(pk=self.pk).exists():
            raise ValueError("Approval actions are immutable after creation")
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="audit_logs"
    )
    normalized_record = models.ForeignKey(
        "normalization.NormalizedRecord", on_delete=models.PROTECT, related_name="audit_logs"
    )
    field_name = models.CharField(max_length=80)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="audit_logs"
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["normalized_record", "created_at"], name="audit_record_created_idx"),
            models.Index(fields=["organization", "created_at"], name="audit_org_created_idx"),
        ]
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("Audit logs are append-only")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit logs cannot be deleted")
