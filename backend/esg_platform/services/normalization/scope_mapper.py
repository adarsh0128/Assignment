from esg_platform.apps.ingestion.models import DataSource
from esg_platform.apps.normalization.models import EmissionFactor


def scope_for_source(source_type: str, category: str) -> str:
    if source_type == DataSource.SourceType.SAP:
        return EmissionFactor.Scope.SCOPE_1
    if source_type == DataSource.SourceType.UTILITY:
        return EmissionFactor.Scope.SCOPE_2_LOCATION
    if source_type == DataSource.SourceType.TRAVEL:
        return EmissionFactor.Scope.SCOPE_3_CAT_6
    raise ValueError(f"unsupported source type: {source_type}")
