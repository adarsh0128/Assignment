from django.apps import AppConfig


class IngestionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "esg_platform.apps.ingestion"
    label = "ingestion"
