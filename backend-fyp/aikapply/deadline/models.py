from django.db import models
from django.utils import timezone
from datetime import date


class University(models.Model):
    """
    A university entry imported from the Excel file.
    Each row in the Excel becomes one University record.
    """

    university_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Short unique ID, e.g. 'u1'. Auto-generated if blank.",
    )
    name = models.CharField(max_length=255)
    deadline = models.DateField(help_text="Admission application deadline")
    program = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Degree / program name (optional)",
    )
    city = models.CharField(max_length=100, blank=True, default="")
    website = models.URLField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline"]
        verbose_name = "University"
        verbose_name_plural = "Universities"

    def __str__(self):
        return f"{self.name} ({self.deadline})"

    # ── computed helpers ──────────────────────────────────────────────────────

    @property
    def days_remaining(self) -> int:
        """Positive = days left, 0 = today, negative = past deadline."""
        delta = self.deadline - date.today()
        return delta.days

    @property
    def priority(self) -> str:
        d = self.days_remaining
        if d < 0:
            return "expired"
        if d <= 14:
            return "critical"
        if d <= 30:
            return "high"
        if d <= 60:
            return "medium"
        return "low"

    @property
    def priority_order(self) -> int:
        """Numeric weight so we can sort by priority."""
        return {"expired": 5, "critical": 1, "high": 2, "medium": 3, "low": 4}.get(
            self.priority, 99
        )

    @property
    def status_color(self) -> str:
        return {
            "expired": "gray",
            "critical": "red",
            "high": "orange",
            "medium": "yellow",
            "low": "green",
        }.get(self.priority, "gray")


class ExcelUpload(models.Model):
    """
    Tracks every Excel file that has been uploaded / imported.
    Useful for auditing and re-imports.
    """

    file = models.FileField(upload_to="deadline_uploads/")
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    rows_imported = models.PositiveIntegerField(default=0)
    rows_skipped = models.PositiveIntegerField(default=0)
    errors = models.TextField(blank=True, default="")
    success = models.BooleanField(default=False)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_filename} @ {self.uploaded_at:%Y-%m-%d %H:%M}"