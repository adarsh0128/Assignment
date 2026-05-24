from esg_platform.apps.core.models import Facility, PlantMapping


def resolve_plant(organization, plant_code: str) -> Facility | None:
    cleaned = (plant_code or "").strip()
    if not cleaned or cleaned.upper() == "N/A":
        return None
    mapping = (
        PlantMapping.objects.select_related("facility")
        .filter(organization=organization, plant_code=cleaned)
        .first()
    )
    return mapping.facility if mapping else None


def resolve_facility_by_name(organization, name: str) -> Facility | None:
    if not name:
        return None
    return Facility.objects.filter(organization=organization, name__iexact=name.strip()).first()
