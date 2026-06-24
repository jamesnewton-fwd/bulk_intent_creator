import csv
from pathlib import Path
from typing import Union

from .exceptions import CSVValidationError
from .models import IntentCheck

REQUIRED_COLUMNS = {
    "name",
    "check_type",
    "from_location_type",
    "from_location_value",
    "to_location_type",
    "to_location_value",
}

OPTIONAL_COLUMNS = {
    "note",
    "enabled",
    "priority",
    "perf_monitoring_enabled",
    "tags",
    "return_path",
    "mode",
    "flow_types",
    "forwarding_types",
    "noise_types",
    "header_fields_with_defaults",
    "from_logical_network",
    "to_logical_network",
    "from_ipv4_dst",
    "to_ipv4_dst",
    "bypass_devices",
}

ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


def parse_csv(filepath: Union[str, Path]) -> list[IntentCheck]:
    checks: list[IntentCheck] = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise CSVValidationError(0, "CSV file is empty or has no header row")

        actual_columns = {c.strip() for c in reader.fieldnames}

        missing = REQUIRED_COLUMNS - actual_columns
        if missing:
            raise CSVValidationError(
                0, f"Missing required column(s): {', '.join(sorted(missing))}"
            )

        unknown = actual_columns - ALL_COLUMNS
        if unknown:
            raise CSVValidationError(
                0, f"Unrecognised column(s): {', '.join(sorted(unknown))}"
            )

        for row_num, row in enumerate(reader, start=2):
            checks.append(_row_to_check(row, row_num))

    return checks


# --- helpers ---

def _require(row: dict, col: str, row_num: int) -> str:
    value = row.get(col, "").strip()
    if not value:
        raise CSVValidationError(row_num, f"Missing value for required column '{col}'")
    return value


def _split_list(row: dict, col: str) -> list[str]:
    """Return a stripped, non-empty list from a comma-separated CSV cell."""
    raw = row.get(col, "").strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_bool(row: dict, col: str, default: bool, row_num: int) -> bool:
    raw = row.get(col, "").strip().lower()
    if not raw:
        return default
    if raw in ("true", "yes", "1"):
        return True
    if raw in ("false", "no", "0"):
        return False
    raise CSVValidationError(row_num, f"Column '{col}' must be true/false, got '{raw}'")


def _row_to_check(row: dict, row_num: int) -> IntentCheck:
    return IntentCheck(
        name=_require(row, "name", row_num),
        check_type=_require(row, "check_type", row_num),
        from_location_type=_require(row, "from_location_type", row_num),
        from_location_value=_require(row, "from_location_value", row_num),
        to_location_type=_require(row, "to_location_type", row_num),
        to_location_value=_require(row, "to_location_value", row_num),
        note=row.get("note", "").strip() or None,
        enabled=_parse_bool(row, "enabled", True, row_num),
        priority=row.get("priority", "").strip() or "NOT_SET",
        perf_monitoring_enabled=_parse_bool(row, "perf_monitoring_enabled", False, row_num),
        tags=_split_list(row, "tags"),
        return_path=row.get("return_path", "").strip() or "ANY",
        mode=row.get("mode", "").strip() or "PERMIT_ALL",
        flow_types=_split_list(row, "flow_types"),
        forwarding_types=_split_list(row, "forwarding_types"),
        noise_types=_split_list(row, "noise_types"),
        header_fields_with_defaults=_split_list(row, "header_fields_with_defaults"),
        from_logical_network=row.get("from_logical_network", "").strip() or None,
        to_logical_network=row.get("to_logical_network", "").strip() or None,
        from_ipv4_dst=_split_list(row, "from_ipv4_dst"),
        to_ipv4_dst=_split_list(row, "to_ipv4_dst"),
        bypass_devices=_split_list(row, "bypass_devices"),
    )
