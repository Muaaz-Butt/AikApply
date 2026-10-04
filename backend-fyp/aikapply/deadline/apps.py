"""
deadline_tracker/apps.py

Seeds the DB from Excel on EVERY Django startup (runserver, gunicorn, etc.)
if the University table is empty.

Excel file search order:
  1. settings.DEADLINE_EXCEL_PATH   (explicit override)
  2. <BASE_DIR>/data/universities_deadlines.xlsx
  3. <BASE_DIR>/universities_deadlines.xlsx   ← easiest: just drop it here
  4. next to this file's parent directory
"""

import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DeadlineTrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "deadline"
    verbose_name = "Deadline Tracker"

    def ready(self):
        """
        Called once when Django finishes loading.
        We defer the actual DB query using a thread so it runs
        AFTER the ORM is fully ready (avoids AppRegistryNotReady errors).
        """
        import threading
        t = threading.Thread(target=_try_seed, daemon=True)
        t.start()


def _find_excel() -> str | None:
    """Return the first existing Excel path from the candidate list."""
    from django.conf import settings

    base_dir = getattr(settings, "BASE_DIR", None)
    candidates = []

    explicit = getattr(settings, "DEADLINE_EXCEL_PATH", None)
    if explicit:
        candidates.append(str(explicit))

    if base_dir:
        candidates.append(os.path.join(str(base_dir), "data", "universities_deadlines.xlsx"))
        candidates.append(os.path.join(str(base_dir), "universities_deadlines.xlsx"))

    # parent of this file = deadline_tracker/, so .. = project root
    candidates.append(
        os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "universities_deadlines.xlsx")
        )
    )

    for p in candidates:
        if p and os.path.isfile(p):
            logger.info(f"[deadline_tracker] Found Excel at: {p}")
            return p

    logger.warning(
        "[deadline_tracker] No Excel file found. Searched:\n"
        + "\n".join(f"  {p}" for p in candidates)
        + "\nDrop universities_deadlines.xlsx in your project root "
        "or set DEADLINE_EXCEL_PATH in settings.py."
    )
    return None


def _try_seed():
    """
    Import Excel into DB if the University table is empty.
    Runs in a background thread so it never blocks server startup.
    """
    import time
    time.sleep(1)  # tiny delay — let Django finish loading fully

    try:
        import django
        django.setup()
    except RuntimeError:
        pass  # already set up, fine

    try:
        from .models import University
        from .services import parse_and_import

        if University.objects.exists():
            logger.info("[deadline_tracker] DB already populated — skipping seed.")
            return

        excel_path = _find_excel()
        if excel_path is None:
            return

        logger.info(f"[deadline_tracker] Seeding from: {excel_path}")
        result = parse_and_import(excel_path)

        if result.imported:
            logger.info(
                f"[deadline_tracker] ✓ Seeded {result.imported} universities "
                f"({result.skipped} rows skipped)."
            )
        else:
            logger.error(
                f"[deadline_tracker] Seed ran but imported 0 rows. "
                f"Errors: {result.errors}"
            )

        for err in result.errors:
            logger.warning(f"[deadline_tracker] {err}")

    except Exception as exc:
        logger.error(f"[deadline_tracker] Seed failed: {exc}", exc_info=True)