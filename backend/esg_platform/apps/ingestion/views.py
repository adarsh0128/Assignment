from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from esg_platform.apps.api.permissions import HasOrganization, IsAnalystOrAdmin
from esg_platform.apps.api.views import TenantQuerysetMixin
from esg_platform.apps.ingestion.models import DataSource, IngestionRun, RawRecord
from esg_platform.apps.ingestion.serializers import (
    DataSourceSerializer,
    IngestionRunSerializer,
    RawRecordSerializer,
    UploadSerializer,
)
from esg_platform.services.ingestion.pipeline import process_upload


class DataSourceListView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = DataSourceSerializer
    queryset = DataSource.objects.filter(is_active=True)


class IngestionRunListView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = IngestionRunSerializer
    queryset = IngestionRun.objects.select_related("data_source")

    def get_queryset(self):
        queryset = super().get_queryset()
        source_type = self.request.query_params.get("source_type")
        status_filter = self.request.query_params.get("status")
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class IngestionRunDetailView(TenantQuerysetMixin, RetrieveAPIView):
    permission_classes = [HasOrganization]
    serializer_class = IngestionRunSerializer
    queryset = IngestionRun.objects.select_related("data_source")


class RawRecordListView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = RawRecordSerializer
    queryset = RawRecord.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(ingestion_run_id=self.kwargs["run_id"])


class UploadView(APIView):
    permission_classes = [HasOrganization, IsAnalystOrAdmin]

    def post(self, request):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_source = get_object_or_404(
            DataSource,
            id=serializer.validated_data["data_source"],
            organization_id=request.user.organization_id,
            is_active=True,
        )
        run = process_upload(
            organization=request.user.organization,
            user=request.user,
            data_source=data_source,
            uploaded_file=serializer.validated_data["file"],
        )
        return Response(IngestionRunSerializer(run).data, status=status.HTTP_201_CREATED)
