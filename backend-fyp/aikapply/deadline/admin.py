from django.contrib import admin
from .models import University, ExcelUpload


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = [
        "university_id", "name", "deadline", "program",
        "city", "days_remaining_display", "priority",
    ]
    list_filter = ["city"]
    search_fields = ["name", "university_id", "program", "city"]
    ordering = ["deadline"]
    readonly_fields = ["created_at", "updated_at"]

    def days_remaining_display(self, obj):
        d = obj.days_remaining
        if d < 0:
            return f"Expired ({abs(d)}d ago)"
        return f"{d} days"
    days_remaining_display.short_description = "Days Remaining"


@admin.register(ExcelUpload)
class ExcelUploadAdmin(admin.ModelAdmin):
    list_display = [
        "original_filename", "uploaded_at",
        "rows_imported", "rows_skipped", "success",
    ]
    readonly_fields = [
        "original_filename", "uploaded_at",
        "rows_imported", "rows_skipped", "errors", "success",
    ]
    ordering = ["-uploaded_at"]