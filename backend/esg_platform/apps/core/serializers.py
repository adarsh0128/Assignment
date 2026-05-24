from rest_framework import serializers

from esg_platform.apps.core.models import Facility, Organization, PlantMapping, User


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "organization"]


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ["id", "name", "country", "city", "external_id", "created_at"]


class PlantMappingSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.name", read_only=True)

    class Meta:
        model = PlantMapping
        fields = ["id", "plant_code", "facility", "facility_name", "source_system", "created_at"]
