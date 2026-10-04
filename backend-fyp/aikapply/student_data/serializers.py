
from rest_framework import serializers
from .models import StudentProfile

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile

        fields = "__all__"
        read_only_fields = ("user", "created_at")