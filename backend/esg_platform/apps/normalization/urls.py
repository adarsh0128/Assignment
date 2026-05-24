from django.urls import path

from esg_platform.apps.normalization.views import (
    EmissionFactorListView,
    NormalizedRecordDetailView,
    NormalizedRecordListView,
)

urlpatterns = [
    path("normalized-records/", NormalizedRecordListView.as_view(), name="normalized-record-list"),
    path("normalized-records/<int:pk>/", NormalizedRecordDetailView.as_view(), name="normalized-record-detail"),
    path("emission-factors/", EmissionFactorListView.as_view(), name="emission-factor-list"),
]
