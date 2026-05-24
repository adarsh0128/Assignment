from datetime import datetime
from decimal import Decimal

from esg_platform.apps.ingestion.models import DataSource
from esg_platform.apps.normalization.models import NormalizedRecord

AIRPORT_COUNTRIES = {
    "ATL": "US",
    "BOS": "US",
    "CDG": "FR",
    "DEL": "IN",
    "DEN": "US",
    "DFW": "US",
    "DXB": "AE",
    "FRA": "DE",
    "JFK": "US",
    "LAX": "US",
    "LHR": "GB",
    "NRT": "JP",
    "ORD": "US",
    "SFO": "US",
    "SIN": "SG",
}


def detect_common(quantity: Decimal, unit_error: str | None = None) -> list[str]:
    reasons = []
    if quantity < 0:
        reasons.append("negative activity quantity")
    if unit_error:
        reasons.append(unit_error)
    return reasons


def detect_duplicate_invoice(organization, vendor_id: str, invoice_date, amount_local: Decimal) -> bool:
    return NormalizedRecord.objects.filter(
        organization=organization,
        source_type=DataSource.SourceType.SAP,
        normalized_payload__vendor_id=vendor_id,
        normalized_payload__invoice_date=str(invoice_date),
        normalized_payload__amount_local=str(amount_local),
    ).exists()


def detect_usage_spike(organization, meter_id: str, quantity: Decimal, activity_date) -> bool:
    prior = (
        NormalizedRecord.objects.filter(
            organization=organization,
            source_type=DataSource.SourceType.UTILITY,
            normalized_payload__meter_id=meter_id,
            activity_date__lt=activity_date,
        )
        .order_by("-activity_date")[:3]
        .values_list("canonical_quantity", flat=True)
    )
    values = list(prior)
    if len(values) < 3:
        return False
    average = sum(values, Decimal("0")) / Decimal(len(values))
    return average > 0 and quantity > average * Decimal("4")


def detect_plant_usage_spike(organization, plant_code: str, quantity: Decimal, activity_date) -> bool:
    if not plant_code:
        return False
    prior = (
        NormalizedRecord.objects.filter(
            organization=organization,
            source_type=DataSource.SourceType.SAP,
            normalized_payload__plant_code=plant_code,
            activity_date__lt=activity_date,
        )
        .exclude(canonical_quantity__lt=0)
        .order_by("-activity_date")[:3]
        .values_list("canonical_quantity", flat=True)
    )
    values = list(prior)
    if len(values) < 3:
        return False
    average = sum(values, Decimal("0")) / Decimal(len(values))
    return average > 0 and quantity > average * Decimal("4")


def detect_billing_overlap(organization, meter_id: str, start_date, end_date) -> bool:
    return NormalizedRecord.objects.filter(
        organization=organization,
        source_type=DataSource.SourceType.UTILITY,
        normalized_payload__meter_id=meter_id,
        normalized_payload__billing_period_start__lte=str(end_date),
        normalized_payload__billing_period_end__gte=str(start_date),
    ).exists()


def detect_travel_anomalies(row: dict[str, str]) -> list[str]:
    reasons = []
    dep = (row.get("departure_airport") or "").upper()
    arr = (row.get("arrival_airport") or "").upper()
    if dep and dep not in AIRPORT_COUNTRIES:
        reasons.append(f"unrecognized airport code: {dep}")
    if arr and arr not in AIRPORT_COUNTRIES:
        reasons.append(f"unrecognized airport code: {arr}")
    departure_time = row.get("departure_time")
    arrival_time = row.get("arrival_time")
    if departure_time and arrival_time:
        dep_time = datetime.strptime(departure_time, "%H:%M").time()
        arr_time = datetime.strptime(arrival_time, "%H:%M").time()
        if arr_time < dep_time:
            reasons.append("impossible travel timestamp: arrival before departure")
    return reasons
