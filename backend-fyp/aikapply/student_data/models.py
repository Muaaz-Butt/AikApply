from django.db import models
from accounts.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Personal Info
    student_name = models.CharField(max_length=255)
    student_cnic = models.CharField(max_length=20)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    email = models.EmailField()
    nationality = models.CharField(max_length=100)
    religion = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    domicile = models.CharField(max_length=100)
    hafiz_quran = models.BooleanField(default=False)
    hostel = models.BooleanField(default=False)
    matric_obtained = models.IntegerField(null=True, blank=True)
    matric_total = models.IntegerField(null=True, blank=True)
    matric_roll = models.CharField(max_length=50, null=True, blank=True)
    board = models.CharField(max_length=100, null=True, blank=True)

    inter_part_one = models.IntegerField(null=True, blank=True)
    inter_total = models.IntegerField(null=True, blank=True)
    inter_roll = models.CharField(max_length=50, null=True, blank=True)

    preference1 = models.CharField(max_length=100, null=True, blank=True)
    preference2 = models.CharField(max_length=100, null=True, blank=True)
    preference3 = models.CharField(max_length=100, null=True, blank=True)
    # Family Info
    father_income = models.IntegerField()
    father_name = models.CharField(max_length=255)
    father_cnic = models.CharField(max_length=20)
    father_phone = models.CharField(max_length=20)
    mother_name = models.CharField(max_length=255)
    guardian_name = models.CharField(max_length=255)
    guardian_mobile = models.CharField(max_length=20)
    guardian_cnic = models.CharField(max_length=20)
    photo = models.FileField(upload_to="photos/", null=True, blank=True)
    matric_degree = models.FileField(upload_to="documents/matric/", null=True, blank=True)
    inter_degree = models.FileField(upload_to="documents/inter/", null=True, blank=True)
    domicile_upload = models.FileField(upload_to="documents/domicile/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student_name
