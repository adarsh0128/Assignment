# Source Format Notes

## SAP Fuel and Procurement CSV

Researched format: Common SAP procurement and materials extracts built from MM/FI fields such as material, plant, vendor, invoice date, currency, amount, cost center, and GL account.

Simplified: The prototype uses one flat CSV instead of joining purchase orders, goods receipts, invoices, material masters, and vendor masters. It also maps plant codes through a local `PlantMapping` table rather than reading SAP customizing tables.

Production risks: Localized number formats, duplicate invoice lines, plant-code changes, vendor master inconsistencies, unit-of-measure conversions by material, and reconciliation against finance posting status.

## Utility Electricity CSV

Researched format: Commercial utility billing exports with meters, billing periods, kWh/MWh, tariff, peak/off-peak consumption, demand kW, demand charges, account numbers, and suppliers.

Simplified: The prototype models one meter per row and one billing charge summary. Real bills can contain taxes, riders, interval data, meter multipliers, multiple service points, renewable energy certificates, and amended bills.

Production risks: Billing-period overlaps, credits and rebills, tariff changes, estimated reads, missing meter mappings to facilities, and market-based vs location-based factor selection.

## Corporate Travel Export

Researched format: Concur/Navan-style expense and booking exports with expense report IDs, traveler names, travel type, airports, airline, cabin, hotel fields, ground transport distances, currency, and booking tool.

Simplified: The prototype accepts optional departure and arrival times for anomaly checks, uses a small airport lookup, and estimates flight distance with Haversine. Production exports often separate itinerary segments, expense lines, approvals, and receipts.

Production risks: Multi-leg flights, codeshares, rail operators, hotel chain normalization, missing booking distances, personal travel mixed with business trips, privacy rules for traveler data, and retroactive expense corrections.
