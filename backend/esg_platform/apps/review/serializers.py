from rest_framework import serializers

from esg_platform.apps.review.models import ApprovalAction, AuditLog


class ApprovalActionSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = ApprovalAction
        fields = [
            "id",
            "normalized_record",
            "action",
            "reason",
            "created_by",
            "created_by_username",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_by_username", "created_at"]


class ReviewActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject", "flag", "reopen", "lock"])
    reason = serializers.CharField(required=False, allow_blank=True)


class BulkApproveSerializer(serializers.Serializer):
    record_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    reason = serializers.CharField(required=False, allow_blank=True)


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "normalized_record",
            "field_name",
            "old_value",
            "new_value",
            "actor",
            "actor_username",
            "reason",
            "created_at",
        ]
        read_only_fields = fields
