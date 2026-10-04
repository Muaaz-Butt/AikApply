"""
Management command: import_now

Immediately imports the Excel file into the database.
Run this once to fix an empty DB:

    python manage.py import_now
    python manage.py import_now --path /full/path/to/file.xlsx
    python manage.py import_now --clear   # wipe first, then import
"""

import os
from django.core.management.base import BaseCommand, CommandError
from deadline_tracker.models import University
from deadline_tracker.services import parse_and_import


SEARCH_PATHS = [
    "universities_deadlines.xlsx",
    "data/universities_deadlines.xlsx",
]


class Command(BaseCommand):
    help = "Immediately import university deadlines from Excel into the DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path", "-p",
            type=str,
            default=None,
            help="Explicit path to .xlsx file (optional — auto-detected if omitted)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing University records before importing",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        # ── find the file ──────────────────────────────────────────────────────
        path = options["path"]

        if path is None:
            base = getattr(settings, "BASE_DIR", os.getcwd())
            candidates = [os.path.join(str(base), p) for p in SEARCH_PATHS]
            # also check explicit setting
            explicit = getattr(settings, "DEADLINE_EXCEL_PATH", None)
            if explicit:
                candidates.insert(0, str(explicit))

            path = next((p for p in candidates if os.path.isfile(p)), None)

        if path is None or not os.path.isfile(path):
            self.stdout.write(self.style.ERROR(
                "\nCould not find universities_deadlines.xlsx.\n"
                "Either:\n"
                "  1. Copy it to your project root (same folder as manage.py)\n"
                "  2. Pass it explicitly:  python manage.py import_now --path /full/path/to/file.xlsx\n"
                "  3. Set DEADLINE_EXCEL_PATH = '/path/to/file.xlsx'  in settings.py\n"
            ))
            return

        self.stdout.write(f"Using file: {path}")

        # ── optionally clear ───────────────────────────────────────────────────
        if options["clear"]:
            deleted, _ = University.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing records."))

        existing = University.objects.count()
        if existing > 0 and not options["clear"]:
            self.stdout.write(
                self.style.WARNING(f"DB already has {existing} universities. "
                                   "Use --clear to replace them, or this will upsert.")
            )

        # ── import ─────────────────────────────────────────────────────────────
        result = parse_and_import(path)

        self.stdout.write(self.style.SUCCESS(f"  ✓ Imported : {result.imported} universities"))
        if result.skipped:
            self.stdout.write(self.style.WARNING(f"  ⚠ Skipped  : {result.skipped} rows"))
        for err in result.errors:
            self.stdout.write(self.style.ERROR(f"  ✗ {err}"))

        # ── show what's now in DB ──────────────────────────────────────────────
        self.stdout.write("\nCurrent DB contents:")
        for u in University.objects.all().order_by("deadline"):
            self.stdout.write(
                f"  [{u.university_id}] {u.name:<20} deadline={u.deadline}  "
                f"days_left={u.days_remaining}  priority={u.priority}"
            )

        self.stdout.write(self.style.SUCCESS("\nDone. Now test: GET /api/deadlines/summary/"))