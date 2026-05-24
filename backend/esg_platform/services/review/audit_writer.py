from esg_platform.apps.review.models import AuditLog


def write_audit_log(record, actor, field_name: str, old_value, new_value, reason: str = ""):
    return AuditLog.objects.create(
        organization=record.organization,
        normalized_record=record,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        actor=actor,
        reason=reason,
    )
