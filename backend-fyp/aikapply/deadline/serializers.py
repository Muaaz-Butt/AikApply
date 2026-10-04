"""
deadline_tracker/serializers.py
"""
from rest_framework import serializers
from .models import University, ExcelUpload


class UniversitySerializer(serializers.ModelSerializer):
    days_remaining = serializers.IntegerField(read_only=True)
    priority = serializers.CharField(read_only=True)
    status_color = serializers.CharField(read_only=True)
    is_past = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = [
            "id",
            "university_id",
            "name",
            "deadline",
            "program",
            "city",
            "website",
            "notes",
            "days_remaining",
            "priority",
            "status_color",
            "is_past",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_is_past(self, obj) -> bool:
        return obj.days_remaining < 0


class ExcelUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelUpload
        fields = [
            "id",
            "original_filename",
            "uploaded_at",
            "rows_imported",
            "rows_skipped",
            "errors",
            "success",
        ]
        read_only_fields = fields


class DeadlineSummarySerializer(serializers.Serializer):
    """
    Aggregated stats returned by GET /api/deadlines/summary/
    """
    total = serializers.IntegerField()
    critical = serializers.IntegerField()
    high = serializers.IntegerField()
    medium = serializers.IntegerField()
    low = serializers.IntegerField()
    expired = serializers.IntegerField()
    next_deadline = UniversitySerializer(allow_null=True)
    universities = UniversitySerializer(many=True)