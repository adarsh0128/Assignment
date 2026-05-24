from django.urls import path

from esg_platform.apps.ingestion.views import (
    DataSourceListView,
    IngestionRunDetailView,
    IngestionRunListView,
    RawRecordListView,
    UploadView,
)

urlpatterns = [
    path("data-sources/", DataSourceListView.as_view(), name="data-source-list"),
    path("uploads/", UploadView.as_view(), name="upload"),
    path("runs/", IngestionRunListView.as_view(), name="run-list"),
    path("runs/<int:pk>/", IngestionRunDetailView.as_view(), name="run-detail"),
    path("runs/<int:run_id>/raw-records/", RawRecordListView.as_view(), name="raw-record-list"),
]
