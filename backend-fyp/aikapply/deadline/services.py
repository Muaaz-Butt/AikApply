"""
deadline_tracker/services.py
────────────────────────────
Parses an uploaded Excel file and upserts University records.

Expected Excel columns (case-insensitive, order doesn't matter):

  | university_id | name          | deadline   | program   | city    | website | notes |
  |---------------|---------------|------------|-----------|---------|---------|-------|
  | u1            | FAST NUCES    | 2025-11-15 | BS CS     | Lahore  | ...     | ...   |

Only `name` and `deadline` are required.
If `university_id` is missing, one is auto-generated as  u<row_number>.

Accepted deadline formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, MM/DD/YYYY.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

import openpyxl

from .models import ExcelUpload, University


# ── column aliases ────────────────────────────────────────────────────────────

COLUMN_ALIASES: dict[str, list[str]] = {
    "university_id": ["university_id", "id", "uni_id", "code"],
    "name": ["name", "university", "university_name", "institution"],
    "deadline": ["deadline", "date", "application_deadline", "last_date", "due_date"],
    "program": ["program", "programme", "degree", "course"],
    "city": ["city", "location", "campus"],
    "website": ["website", "url", "link", "web"],
    "notes": ["notes", "note", "remarks", "comments"],
}


def _normalize_header(raw: str) -> str:
    return re.sub(r"[^a-z0-9]", "_", raw.strip().lower())


def _resolve_columns(headers: list[str]) -> dict[str, int]:
    """Map canonical field names → column index."""
    normalized = {_normalize_header(h): i for i, h in enumerate(headers)}
    result: dict[str, int] = {}
    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                result[field] = normalized[alias]
                break
    return result


DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d %b %Y",
    "%d %B %Y",
]


def _parse_date(raw: Any) -> date | None:
    if isinstance(raw, (date, datetime)):
        return raw.date() if isinstance(raw, datetime) else raw
    if raw is None:
        return None
    raw_str = str(raw).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw_str, fmt).date()
        except ValueError:
            continue
    return None


def _cell_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


# ── main parser ───────────────────────────────────────────────────────────────

class ExcelParseResult:
    def __init__(self):
        self.imported: int = 0
        self.skipped: int = 0
        self.errors: list[str] = []
        self.universities: list[University] = []


def parse_and_import(file_path: str, upload_record: ExcelUpload | None = None) -> ExcelParseResult:
    """
    Read `file_path` (.xlsx), upsert University rows, return a result summary.

    Pass an `ExcelUpload` instance to have it updated with counts/errors.
    """
    result = ExcelParseResult()

    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
    except Exception as exc:
        result.errors.append(f"Cannot open workbook: {exc}")
        _finalize_upload(upload_record, result)
        return result

    ws = wb.active  # always use the first sheet

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        result.errors.append("Workbook is empty.")
        _finalize_upload(upload_record, result)
        return result

    # first non-empty row = headers
    header_row = rows[0]
    headers = [_cell_str(h) for h in header_row]
    col_map = _resolve_columns(headers)

    if "name" not in col_map:
        result.errors.append("Could not find a 'name' / 'university_name' column.")
        _finalize_upload(upload_record, result)
        return result

    if "deadline" not in col_map:
        result.errors.append("Could not find a 'deadline' / 'date' column.")
        _finalize_upload(upload_record, result)
        return result

    auto_id_counter = 1

    for row_idx, row in enumerate(rows[1:], start=2):  # data starts at row 2
        # skip fully blank rows
        if all(cell is None or _cell_str(cell) == "" for cell in row):
            continue

        def get(field: str) -> Any:
            idx = col_map.get(field)
            return row[idx] if idx is not None and idx < len(row) else None

        name = _cell_str(get("name"))
        if not name:
            result.skipped += 1
            result.errors.append(f"Row {row_idx}: missing name — skipped.")
            continue

        deadline = _parse_date(get("deadline"))
        if deadline is None:
            result.skipped += 1
            result.errors.append(
                f"Row {row_idx} ({name}): could not parse deadline '{get('deadline')}' — skipped."
            )
            continue

        # university_id: use column value or auto-generate
        raw_uid = _cell_str(get("university_id"))
        uid = raw_uid if raw_uid else f"u{auto_id_counter}"
        auto_id_counter += 1

        uni, created = University.objects.update_or_create(
            university_id=uid,
            defaults={
                "name": name,
                "deadline": deadline,
                "program": _cell_str(get("program")),
                "city": _cell_str(get("city")),
                "website": _cell_str(get("website")),
                "notes": _cell_str(get("notes")),
            },
        )
        result.imported += 1
        result.universities.append(uni)

    _finalize_upload(upload_record, result)
    return result


def _finalize_upload(upload_record: ExcelUpload | None, result: ExcelParseResult):
    if upload_record is None:
        return
    upload_record.rows_imported = result.imported
    upload_record.rows_skipped = result.skipped
    upload_record.errors = "\n".join(result.errors)
    upload_record.success = result.imported > 0
    upload_record.save()