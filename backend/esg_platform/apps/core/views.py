from rest_framework.generics import ListAPIView

from esg_platform.apps.api.permissions import HasOrganization
from esg_platform.apps.api.views import TenantQuerysetMixin
from esg_platform.apps.core.models import Facility, PlantMapping
from esg_platform.apps.core.serializers import FacilitySerializer, PlantMappingSerializer


class FacilityListView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = FacilitySerializer
    queryset = Facility.objects.all()


class PlantMappingListView(TenantQuerysetMixin, ListAPIView):
    permission_classes = [HasOrganization]
    serializer_class = PlantMappingSerializer
    queryset = PlantMapping.objects.select_related("facility")
