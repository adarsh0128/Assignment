from rest_framework.generics import ListAPIView, RetrieveAPIView

from esg_platform.apps.api.permissions import HasOrganization
from esg_platform.apps.api.views import TenantQuerysetMixin
from esg_platform.apps.normalization.models import EmissionFactor, NormalizedRecord
from esg_platform.apps.normalization.serializers import (
    EmissionFactorSerializer,
    NormalizedRecordSerializer,
)


class NormalizedRecordListView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = NormalizedRecordSerializer
    queryset = NormalizedRecord.objects.select_related(
        "facility", "raw_record", "ingestion_run", "data_source"
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in ["status", "source_type"]:
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        suspicious = self.request.query_params.get("is_suspicious")
        if suspicious in {"true", "false"}:
            queryset = queryset.filter(is_suspicious=suspicious == "true")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            queryset = queryset.filter(activity_date__gte=start)
        if end:
            queryset = queryset.filter(activity_date__lte=end)
        return queryset


class NormalizedRecordDetailView(TenantQuerysetMixin, RetrieveAPIView):
    permission_classes = [HasOrganization]
    serializer_class = NormalizedRecordSerializer
    queryset = NormalizedRecord.objects.select_related(
        "facility", "raw_record", "ingestion_run", "data_source", "emission_factor"
    )


class EmissionFactorListView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = EmissionFactorSerializer
    queryset = EmissionFactor.objects.all()
