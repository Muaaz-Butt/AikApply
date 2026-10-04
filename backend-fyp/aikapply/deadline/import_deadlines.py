"""
Management command: import_deadlines

Usage:
    python manage.py import_deadlines path/to/universities.xlsx
    python manage.py import_deadlines path/to/universities.xlsx --clear
"""

import os
from django.core.management.base import BaseCommand, CommandError
from deadline_tracker.models import University
from deadline_tracker.services import parse_and_import


class Command(BaseCommand):
    help = "Import university deadlines from an Excel (.xlsx) file"

    def add_arguments(self, parser):
        parser.add_argument("xlsx_path", type=str, help="Path to the .xlsx file")
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing universities before importing",
        )

    def handle(self, *args, **options):
        path = options["xlsx_path"]

        if not os.path.exists(path):
            raise CommandError(f"File not found: {path}")

        if not path.lower().endswith((".xlsx", ".xlsm")):
            raise CommandError("Only .xlsx / .xlsm files are supported.")

        if options["clear"]:
            count, _ = University.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing records."))

        self.stdout.write(f"Importing from: {path}")
        result = parse_and_import(path)

        self.stdout.write(
            self.style.SUCCESS(f"  Imported : {result.imported} universities")
        )
        if result.skipped:
            self.stdout.write(
                self.style.WARNING(f"  Skipped  : {result.skipped} rows")
            )
        for err in result.errors:
            self.stdout.write(self.style.ERROR(f"  ⚠ {err}"))

        self.stdout.write(self.style.SUCCESS("Done."))