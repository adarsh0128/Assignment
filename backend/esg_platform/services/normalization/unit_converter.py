from datetime import datetime
from decimal import Decimal, InvalidOperation

LITERS_PER_UNIT = {
    "L": Decimal("1"),
    "GAL": Decimal("3.78541"),
    "M3": Decimal("1000"),
    "KG": Decimal("1.176"),
    "LB": Decimal("0.533"),
}


def parse_decimal(value: str) -> Decimal:
    text = (value or "").strip()
    if not text:
        raise ValueError("missing decimal value")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal value: {value}") from exc


def parse_date(value: str):
    for fmt in ("%d.%m.%Y", "%Y%m%d", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid date: {value}")


def fuel_to_liters(quantity: Decimal, uom: str) -> Decimal:
    normalized = (uom or "").strip().upper()
    if normalized not in LITERS_PER_UNIT:
        raise ValueError(f"unresolvable unit of measure: {uom}")
    return quantity * LITERS_PER_UNIT[normalized]


def electricity_to_kwh(kwh: str, mwh: str) -> Decimal:
    if kwh:
        return parse_decimal(kwh)
    if mwh:
        return parse_decimal(mwh) * Decimal("1000")
    raise ValueError("missing electricity consumption")


def distance_to_km(km: str, miles: str) -> Decimal:
    if km:
        return parse_decimal(km)
    if miles:
        return parse_decimal(miles) * Decimal("1.609344")
    return Decimal("0")
