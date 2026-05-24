from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from esg_platform.apps.api.permissions import HasOrganization, IsAnalystOrAdmin
from esg_platform.apps.api.views import DashboardView, TenantQuerysetMixin
from esg_platform.apps.normalization.models import NormalizedRecord
from esg_platform.apps.review.models import AuditLog
from esg_platform.apps.review.serializers import (
    AuditLogSerializer,
    BulkApproveSerializer,
    ReviewActionSerializer,
)
from esg_platform.services.review.approval_workflow import apply_review_action


class DashboardEndpoint(DashboardView):
    pass


class ReviewActionView(APIView):
    permission_classes = [HasOrganization, IsAnalystOrAdmin]

    def post(self, request, record_id: int):
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = get_object_or_404(
            NormalizedRecord,
            id=record_id, organization_id=request.user.organization_id
        )
        try:
            updated = apply_review_action(
                record=record,
                actor=request.user,
                action=serializer.validated_data["action"],
                reason=serializer.validated_data.get("reason", ""),
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response({"id": updated.id, "status": updated.status})


class BulkApproveView(APIView):
    permission_classes = [HasOrganization, IsAnalystOrAdmin]

    def post(self, request):
        serializer = BulkApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        records = NormalizedRecord.objects.filter(
            id__in=serializer.validated_data["record_ids"],
            organization_id=request.user.organization_id,
            status__in=["pending", "flagged"],
        )
        updated_ids = []
        for record in records:
            updated = apply_review_action(
                record=record,
                actor=request.user,
                action="approve",
                reason=serializer.validated_data.get("reason", "Bulk approve"),
            )
            updated_ids.append(updated.id)
        return Response({"updated_ids": updated_ids}, status=status.HTTP_200_OK)


class AuditTimelineView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related("actor", "normalized_record")

    def get_queryset(self):
        return super().get_queryset().filter(normalized_record_id=self.kwargs["record_id"])
