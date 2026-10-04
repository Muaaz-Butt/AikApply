from django.db import models
from accounts.models import User
from student_data.models import StudentProfile  # your student model

class University(models.Model):
    name = models.CharField(max_length=255)
    application_url = models.URLField()

    def __str__(self):
        return self.name

class FieldMapping(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    portal_field_name = models.CharField(max_length=255)
    student_field_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.portal_field_name} -> {self.student_field_name}"
