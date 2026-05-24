from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

from esg_platform.apps.ingestion.models import DataSource, RawRecord
from esg_platform.apps.normalization.models import EmissionFactor, NormalizedRecord
from esg_platform.services.ingestion.detect_anomalies import (
    AIRPORT_COUNTRIES,
    detect_billing_overlap,
    detect_common,
    detect_duplicate_invoice,
    detect_plant_usage_spike,
    detect_travel_anomalies,
    detect_usage_spike,
)
from esg_platform.services.normalization.plant_resolver import (
    resolve_facility_by_name,
    resolve_plant,
)
from esg_platform.services.normalization.scope_mapper import scope_for_source
from esg_platform.services.normalization.unit_converter import (
    distance_to_km,
    electricity_to_kwh,
    fuel_to_liters,
    parse_date,
    parse_decimal,
)

AIRPORT_COORDS = {
    "ATL": (33.6407, -84.4277),
    "BOS": (42.3656, -71.0096),
    "CDG": (49.0097, 2.5479),
    "DEL": (28.5562, 77.1000),
    "DEN": (39.8561, -104.6737),
    "DFW": (32.8998, -97.0403),
    "DXB": (25.2532, 55.3657),
    "FRA": (50.0379, 8.5622),
    "JFK": (40.6413, -73.7781),
    "LAX": (33.9416, -118.4085),
    "LHR": (51.4700, -0.4543),
    "NRT": (35.7720, 140.3929),
    "ORD": (41.9742, -87.9073),
    "SFO": (37.6213, -122.3790),
    "SIN": (1.3644, 103.9915),
}


def estimate_flight_km(departure: str, arrival: str) -> Decimal:
    if departure not in AIRPORT_COORDS or arrival not in AIRPORT_COORDS:
        return Decimal("0")
    lat1, lon1 = AIRPORT_COORDS[departure]
    lat2, lon2 = AIRPORT_COORDS[arrival]
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return Decimal(str(round(6371 * 2 * asin(sqrt(a)), 2)))


def find_factor(organization, scope: str, category: str) -> EmissionFactor | None:
    return (
        EmissionFactor.objects.filter(
            organization=organization, scope=scope, category=category
        )
        .order_by("-effective_from")
        .first()
    )


def build_record(raw_record: RawRecord) -> NormalizedRecord:
    source_type = raw_record.ingestion_run.source_type
    if source_type == DataSource.SourceType.SAP:
        return normalize_sap(raw_record)
    if source_type == DataSource.SourceType.UTILITY:
        return normalize_utility(raw_record)
    if source_type == DataSource.SourceType.TRAVEL:
        return normalize_travel(raw_record)
    raise ValueError(f"unsupported source type: {source_type}")


def normalize_sap(raw_record: RawRecord) -> NormalizedRecord:
    row = raw_record.payload
    organization = raw_record.organization
    quantity = parse_decimal(row["quantity"])
    invoice_date = parse_date(row["invoice_date"])
    amount = parse_decimal(row["amount_local"])
    unit_error = None
    try:
        canonical_quantity = fuel_to_liters(quantity, row["uom"])
    except ValueError as exc:
        canonical_quantity = Decimal("0")
        unit_error = str(exc)
    reasons = detect_common(quantity, unit_error)
    if detect_duplicate_invoice(organization, row["vendor_id"], invoice_date, amount):
        reasons.append("duplicate invoice")
    if detect_plant_usage_spike(
        organization, row.get("plant_code", "").strip(), canonical_quantity, invoice_date
    ):
        reasons.append("usage spike greater than 300 percent over trailing plant average")
    facility = resolve_plant(organization, row.get("plant_code", ""))
    if not facility:
        reasons.append("missing or unresolved plant code")
    category = "stationary_combustion"
    scope = scope_for_source(DataSource.SourceType.SAP, category)
    factor = find_factor(organization, scope, category)
    co2e = canonical_quantity * factor.factor_value if factor else Decimal("0")
    return NormalizedRecord(
        organization=organization,
        raw_record=raw_record,
        ingestion_run=raw_record.ingestion_run,
        data_source=raw_record.ingestion_run.data_source,
        facility=facility,
        emission_factor=factor,
        source_type=DataSource.SourceType.SAP,
        category=category,
        scope=scope,
        activity_date=invoice_date,
        canonical_quantity=canonical_quantity,
        canonical_unit="L",
        co2e_kg=co2e,
        source_reference=f"{row['vendor_id']}:{row['invoice_date']}:{row['amount_local']}",
        normalized_payload={
            "vendor_id": row["vendor_id"],
            "invoice_date": str(invoice_date),
            "amount_local": str(amount),
            "fuel_type": row["fuel_type"],
            "plant_code": row.get("plant_code", ""),
        },
        is_suspicious=bool(reasons),
        suspicion_reasons=reasons,
        status="flagged" if reasons else "pending",
    )


def normalize_utility(raw_record: RawRecord) -> NormalizedRecord:
    row = raw_record.payload
    organization = raw_record.organization
    start_date = parse_date(row["billing_period_start"])
    end_date = parse_date(row["billing_period_end"])
    quantity = electricity_to_kwh(row.get("kwh_consumed", ""), row.get("mwh_consumed", ""))
    reasons = detect_common(quantity)
    meter_id = row["meter_id"]
    if detect_usage_spike(organization, meter_id, quantity, end_date):
        reasons.append("usage spike greater than 300 percent over trailing average")
    if detect_billing_overlap(organization, meter_id, start_date, end_date):
        reasons.append("billing period overlap")
    demand_charge = parse_decimal(row.get("demand_charge_usd") or "0")
    if demand_charge < 0:
        reasons.append("negative demand charge credit row")
    if not row.get("tariff_type"):
        reasons.append("missing tariff type")
    category = "purchased_electricity"
    scope = scope_for_source(DataSource.SourceType.UTILITY, category)
    factor = find_factor(organization, scope, category)
    co2e = quantity * factor.factor_value if factor else Decimal("0")
    return NormalizedRecord(
        organization=organization,
        raw_record=raw_record,
        ingestion_run=raw_record.ingestion_run,
        data_source=raw_record.ingestion_run.data_source,
        facility=resolve_facility_by_name(organization, row.get("facility_name", "")),
        emission_factor=factor,
        source_type=DataSource.SourceType.UTILITY,
        category=category,
        scope=scope,
        activity_date=end_date,
        canonical_quantity=quantity,
        canonical_unit="kWh",
        co2e_kg=co2e,
        source_reference=meter_id,
        normalized_payload={
            "meter_id": meter_id,
            "billing_period_start": str(start_date),
            "billing_period_end": str(end_date),
            "supplier_name": row.get("supplier_name", ""),
        },
        is_suspicious=bool(reasons),
        suspicion_reasons=reasons,
        status="flagged" if reasons else "pending",
    )


def normalize_travel(raw_record: RawRecord) -> NormalizedRecord:
    row = raw_record.payload
    organization = raw_record.organization
    travel_type = row["travel_type"].strip().lower()
    category = {"air": "flight", "hotel": "hotel", "ground": "ground", "rail": "rail", "taxi": "ground"}.get(
        travel_type, "business_travel"
    )
    activity_date = parse_date(row["travel_date"])
    reasons = detect_travel_anomalies(row)
    dep = (row.get("departure_airport") or "").upper()
    arr = (row.get("arrival_airport") or "").upper()
    if category == "flight":
        quantity = estimate_flight_km(dep, arr)
    elif category == "hotel":
        quantity = parse_decimal(row.get("hotel_nights") or "0")
    else:
        quantity = distance_to_km(row.get("ground_distance_km", ""), row.get("ground_distance_mi", ""))
    if quantity < 0:
        reasons.append("negative activity quantity")
    scope = scope_for_source(DataSource.SourceType.TRAVEL, category)
    factor = find_factor(organization, scope, category)
    co2e = quantity * factor.factor_value if factor else Decimal("0")
    domesticity = "unknown"
    if dep in AIRPORT_COUNTRIES and arr in AIRPORT_COUNTRIES:
        domesticity = "domestic" if AIRPORT_COUNTRIES[dep] == AIRPORT_COUNTRIES[arr] else "international"
    return NormalizedRecord(
        organization=organization,
        raw_record=raw_record,
        ingestion_run=raw_record.ingestion_run,
        data_source=raw_record.ingestion_run.data_source,
        source_type=DataSource.SourceType.TRAVEL,
        category=category,
        scope=scope,
        activity_date=activity_date,
        canonical_quantity=quantity,
        canonical_unit="night" if category == "hotel" else "km",
        co2e_kg=co2e,
        source_reference=row["expense_report_id"],
        normalized_payload={
            "expense_report_id": row["expense_report_id"],
            "traveler_name": row.get("traveler_name", ""),
            "cabin_class": row.get("cabin_class") or "economy",
            "departure_airport": dep,
            "arrival_airport": arr,
            "domesticity": domesticity,
            "booking_tool": row.get("booking_tool", ""),
        },
        is_suspicious=bool(reasons),
        suspicion_reasons=reasons,
        status="flagged" if reasons else "pending",
    )
