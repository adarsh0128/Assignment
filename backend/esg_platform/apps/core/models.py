from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        ANALYST = "analyst", "Analyst"
        AUDITOR = "auditor", "Auditor"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ANALYST)

    class Meta:
        indexes = [models.Index(fields=["organization", "role"], name="user_org_role_idx")]


class Facility(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="facilities"
    )
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=2)
    city = models.CharField(max_length=120)
    external_id = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name", "city"], name="facility_org_name_city_uniq"
            )
        ]
        indexes = [models.Index(fields=["organization", "name"], name="facility_org_name_idx")]

    def __str__(self) -> str:
        return f"{self.name} ({self.city})"


class PlantMapping(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="plant_mappings"
    )
    plant_code = models.CharField(max_length=30)
    facility = models.ForeignKey(
        Facility, on_delete=models.PROTECT, related_name="plant_mappings"
    )
    source_system = models.CharField(max_length=40, default="SAP")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "plant_code"], name="plant_mapping_org_code_uniq"
            )
        ]
        indexes = [models.Index(fields=["organization", "plant_code"], name="plant_org_code_idx")]

    def __str__(self) -> str:
        return f"{self.plant_code} -> {self.facility_id}"
