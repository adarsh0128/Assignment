from django.urls import path

from esg_platform.apps.core.views import FacilityListView, PlantMappingListView

urlpatterns = [
    path("facilities/", FacilityListView.as_view(), name="facility-list"),
    path("plant-mappings/", PlantMappingListView.as_view(), name="plant-mapping-list"),
]
