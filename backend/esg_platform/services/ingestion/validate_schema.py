from esg_platform.apps.ingestion.models import DataSource

REQUIRED_FIELDS = {
    DataSource.SourceType.SAP: {
        "material_code",
        "plant_code",
        "fuel_type",
        "quantity",
        "uom",
        "invoice_date",
        "vendor_name",
        "vendor_id",
        "currency",
        "amount_local",
        "procurement_category",
        "cost_center",
        "gl_account",
    },
    DataSource.SourceType.UTILITY: {
        "meter_id",
        "facility_name",
        "billing_period_start",
        "billing_period_end",
        "kwh_consumed",
        "mwh_consumed",
        "tariff_type",
        "peak_kwh",
        "offpeak_kwh",
        "demand_kw",
        "demand_charge_usd",
        "account_number",
        "supplier_name",
    },
    DataSource.SourceType.TRAVEL: {
        "expense_report_id",
        "traveler_name",
        "travel_date",
        "travel_type",
        "departure_airport",
        "arrival_airport",
        "airline",
        "cabin_class",
        "hotel_name",
        "hotel_city",
        "hotel_nights",
        "hotel_chain",
        "ground_transport_type",
        "ground_distance_km",
        "ground_distance_mi",
        "expense_amount",
        "expense_currency",
        "booking_tool",
    },
}


def validate_headers(source_type: str, row: dict[str, str]) -> list[str]:
    missing = REQUIRED_FIELDS[source_type] - set(row.keys())
    return [f"missing column: {field}" for field in sorted(missing)]


def validate_row(source_type: str, row: dict[str, str]) -> list[str]:
    errors = validate_headers(source_type, row)
    if errors:
        return errors
    if source_type == DataSource.SourceType.SAP:
        for field in ["quantity", "invoice_date", "vendor_id", "amount_local"]:
            if not row.get(field):
                errors.append(f"{field} is required")
    if source_type == DataSource.SourceType.UTILITY:
        if not row.get("meter_id"):
            errors.append("meter_id is required")
        if not row.get("kwh_consumed") and not row.get("mwh_consumed"):
            errors.append("kwh_consumed or mwh_consumed is required")
    if source_type == DataSource.SourceType.TRAVEL:
        if not row.get("expense_report_id"):
            errors.append("expense_report_id is required")
        if not row.get("travel_date"):
            errors.append("travel_date is required")
    return errors
