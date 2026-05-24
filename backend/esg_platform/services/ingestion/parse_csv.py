import csv
from io import TextIOWrapper


def parse_csv(uploaded_file) -> list[dict[str, str]]:
    uploaded_file.seek(0)
    wrapper = TextIOWrapper(uploaded_file.file, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(wrapper)
    return [{key: (value or "").strip() for key, value in row.items()} for row in reader]
