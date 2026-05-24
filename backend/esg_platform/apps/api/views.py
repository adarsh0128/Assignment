from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from esg_platform.apps.api.permissions import HasOrganization
from esg_platform.apps.ingestion.models import IngestionRun
from esg_platform.apps.normalization.models import NormalizedRecord


class TenantQuerysetMixin:
    organization_field = "organization"

    def get_queryset(self):
        queryset = super().get_queryset()
        lookup = {f"{self.organization_field}_id": self.request.user.organization_id}
        return queryset.filter(**lookup)


class DashboardView(APIView):
    permission_classes = [HasOrganization]

    def get(self, request):
        org_id = request.user.organization_id
        week_start = timezone.now() - timezone.timedelta(days=7)
        record_counts = NormalizedRecord.objects.filter(organization_id=org_id).aggregate(
            pending_reviews=Count("id", filter=Q(status__in=["pending", "flagged"])),
            flagged_rows=Count("id", filter=Q(is_suspicious=True)),
            approved_this_week=Count(
                "id", filter=Q(status="approved", updated_at__gte=week_start)
            ),
        )
        recent_runs = list(
            IngestionRun.objects.filter(organization_id=org_id)
            .select_related("data_source")
            .order_by("-created_at")[:8]
            .values(
                "id",
                "source_type",
                "original_filename",
                "status",
                "total_rows",
                "invalid_rows",
                "suspicious_rows",
                "created_at",
            )
        )
        return Response(
            {
                "total_runs": IngestionRun.objects.filter(organization_id=org_id).count(),
                **record_counts,
                "recent_runs": recent_runs,
            }
        )
