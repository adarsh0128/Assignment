from django.db import transaction
from django.utils import timezone

from esg_platform.apps.normalization.models import NormalizedRecord
from esg_platform.apps.review.models import ApprovalAction
from esg_platform.services.review.audit_writer import write_audit_log

TRANSITIONS = {
    ("pending", "flag"): "flagged",
    ("pending", "approve"): "approved",
    ("flagged", "approve"): "approved",
    ("flagged", "reject"): "rejected",
    ("approved", "lock"): "locked",
    ("rejected", "reopen"): "pending",
}


def apply_review_action(record: NormalizedRecord, actor, action: str, reason: str = "") -> NormalizedRecord:
    key = (record.status, action)
    if key not in TRANSITIONS:
        raise ValueError(f"transition {record.status} -> {action} is not allowed")
    new_status = TRANSITIONS[key]
    with transaction.atomic():
        ApprovalAction.objects.create(
            organization=record.organization,
            normalized_record=record,
            action=action,
            reason=reason,
            created_by=actor,
        )
        old_status = record.status
        record.status = new_status
        if new_status == "locked":
            record.locked_at = timezone.now()
        record.save(update_fields=["status", "locked_at", "updated_at"])
        write_audit_log(
            record=record,
            actor=actor,
            field_name="status",
            old_value=old_status,
            new_value=new_status,
            reason=reason,
        )
    return record
