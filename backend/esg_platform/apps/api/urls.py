from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from esg_platform.apps.api.views import HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include("esg_platform.apps.core.urls")),
    path("", include("esg_platform.apps.ingestion.urls")),
    path("", include("esg_platform.apps.normalization.urls")),
    path("", include("esg_platform.apps.review.urls")),
]
