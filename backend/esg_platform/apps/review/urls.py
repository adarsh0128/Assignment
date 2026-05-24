from django.urls import path

from esg_platform.apps.review.views import (
    AuditTimelineView,
    BulkApproveView,
    DashboardEndpoint,
    ReviewActionView,
)

urlpatterns = [
    path("dashboard/", DashboardEndpoint.as_view(), name="dashboard"),
    path("review/<int:record_id>/action/", ReviewActionView.as_view(), name="review-action"),
    path("review/bulk-approve/", BulkApproveView.as_view(), name="bulk-approve"),
    path("audit/<int:record_id>/", AuditTimelineView.as_view(), name="audit-timeline"),
]
