from decimal import Decimal

from django.core.management.base import BaseCommand

from esg_platform.apps.core.models import Facility, Organization, PlantMapping, User
from esg_platform.apps.ingestion.models import DataSource
from esg_platform.apps.normalization.models import EmissionFactor


class Command(BaseCommand):
    help = "Seed a demo tenant with analyst user, sources, facilities, mappings, and factors."

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            slug="acme-industrial",
            defaults={"name": "Acme Industrial Manufacturing"},
        )
        user, created = User.objects.get_or_create(
            username="analyst",
            defaults={
                "email": "analyst@acmeindustrial.com",
                "organization": org,
                "role": User.Role.ANALYST,
                "is_staff": True,
            },
        )
        if created:
            user.set_password("ChangeMe123!")
            user.save()
        elif user.organization_id != org.id:
            user.organization = org
            user.role = User.Role.ANALYST
            user.save(update_fields=["organization", "role"])

        facilities = {
            "DE01": ("Berlin Assembly", "DE", "Berlin"),
            "US07": ("Dallas Distribution", "US", "Dallas"),
            "IN03": ("Pune Components", "IN", "Pune"),
            "BR02": ("Curitiba Logistics", "BR", "Curitiba"),
            "GB05": ("Manchester Service Center", "GB", "Manchester"),
        }
        for plant_code, (name, country, city) in facilities.items():
            facility, _ = Facility.objects.get_or_create(
                organization=org,
                name=name,
                city=city,
                defaults={"country": country, "external_id": plant_code},
            )
            PlantMapping.objects.get_or_create(
                organization=org,
                plant_code=plant_code,
                defaults={"facility": facility},
            )

        for name, source_type in [
            ("SAP fuel and procurement export", DataSource.SourceType.SAP),
            ("Utility electricity bills", DataSource.SourceType.UTILITY),
            ("Corporate travel expense export", DataSource.SourceType.TRAVEL),
        ]:
            DataSource.objects.get_or_create(
                organization=org,
                name=name,
                source_type=source_type,
            )

        factors = [
            ("scope_1", "stationary_combustion", Decimal("2.680000"), "kgCO2e/L"),
            ("scope_2_location", "purchased_electricity", Decimal("0.420000"), "kgCO2e/kWh"),
            ("scope_3_cat_6", "flight", Decimal("0.158000"), "kgCO2e/km"),
            ("scope_3_cat_6", "hotel", Decimal("18.500000"), "kgCO2e/night"),
            ("scope_3_cat_6", "ground", Decimal("0.192000"), "kgCO2e/km"),
            ("scope_3_cat_6", "rail", Decimal("0.041000"), "kgCO2e/km"),
        ]
        for scope, category, value, unit in factors:
            EmissionFactor.objects.get_or_create(
                organization=org,
                scope=scope,
                category=category,
                effective_from="2026-01-01",
                defaults={
                    "factor_value": value,
                    "factor_unit": unit,
                    "source": "GHG Protocol-aligned demo factor library",
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded demo tenant. Login: analyst / ChangeMe123!"))
