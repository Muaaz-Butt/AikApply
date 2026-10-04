from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    """Model to store user profile data for recommendations"""
    
    # Basic Information
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Location Information
    current_city = models.CharField(max_length=100, help_text="Current city of residence")
    current_province = models.CharField(max_length=100, help_text="Current province")
    can_move_to_other_cities = models.BooleanField(default=False, help_text="Can the user move to other cities?")
    preferred_cities = models.JSONField(default=list, blank=True, help_text="List of preferred cities if can move")
    
    # Academic Information
    interests = models.JSONField(default=list, help_text="List of academic interests/subjects")
    preferred_field_of_study = models.CharField(max_length=200, blank=True, help_text="Preferred field of study")
    academic_level = models.CharField(
        max_length=50,
        choices=[
            ('high_school', 'High School'),
            ('intermediate', 'Intermediate/FSC'),
            ('bachelor', 'Bachelor'),
            ('master', 'Master'),
            ('phd', 'PhD'),
        ],
        default='intermediate'
    )
    intermediate_percentage = models.FloatField(blank=True, null=True, help_text="Percentage in Intermediate/FSC exams")
    
    # Financial Information
    fee_affordability = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low (Under 50,000 PKR per semester)'),
            ('medium', 'Medium (50,000 - 150,000 PKR per semester)'),
            ('high', 'High (150,000 - 300,000 PKR per semester)'),
            ('very_high', 'Very High (Above 300,000 PKR per semester)'),
        ],
        help_text="Fee affordability range"
    )
    scholarship_required = models.BooleanField(default=False, help_text="Does the user need scholarship?")
    
    # Additional Preferences
    university_type = models.CharField(
        max_length=50,
        choices=[
            ('public', 'Public University'),
            ('private', 'Private University'),
            ('both', 'Both'),
        ],
        default='both'
    )
    campus_facilities = models.JSONField(
        default=list,
        blank=True,
        help_text="Preferred campus facilities (e.g., library, labs, sports, hostel)"
    )
    language_preference = models.CharField(
        max_length=50,
        choices=[
            ('urdu', 'Urdu'),
            ('english', 'English'),
            ('both', 'Both'),
        ],
        default='both'
    )
    
    # Additional Notes
    additional_requirements = models.TextField(blank=True, help_text="Any additional requirements or preferences")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    
    class Meta:
        ordering = ['-created_at']


class University(models.Model):
    """Model to store university information"""
    
    name = models.CharField(max_length=200, unique=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    university_type = models.CharField(
        max_length=50,
        choices=[
            ('public', 'Public University'),
            ('private', 'Private University'),
        ]
    )
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    fee_range = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low (Under 50,000 PKR per semester)'),
            ('medium', 'Medium (50,000 - 150,000 PKR per semester)'),
            ('high', 'High (150,000 - 300,000 PKR per semester)'),
            ('very_high', 'Very High (Above 300,000 PKR per semester)'),
        ],
        blank=True
    )
    programs_offered = models.JSONField(default=list, blank=True, help_text="List of programs/fields offered")
    achievements = models.TextField(blank=True, help_text="Notable achievements and rankings")
    facilities = models.JSONField(default=list, blank=True, help_text="Available facilities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    class Meta:
        ordering = ['name']


class Recommendation(models.Model):
    """Model to store recommendations generated for users"""
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recommendations')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='recommendations', null=True, blank=True)
    university_name = models.CharField(max_length=200, help_text="University name if not in database")
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    
    # Recommendation Details
    recommendation_reason = models.TextField(help_text="Why this university is recommended")
    match_score = models.FloatField(default=0.0, help_text="Match score (0-100)")
    achievements = models.TextField(blank=True, help_text="University achievements and highlights")
    fee_information = models.TextField(blank=True, help_text="Fee structure information")
    programs_available = models.JSONField(default=list, blank=True, help_text="Relevant programs available")
    
    # AI Generated Content
    ai_analysis = models.TextField(blank=True, help_text="Detailed AI analysis")
    pros = models.JSONField(default=list, blank=True, help_text="Pros of this university")
    cons = models.JSONField(default=list, blank=True, help_text="Cons of this university")
    
    # Ranking
    rank = models.IntegerField(default=0, help_text="Ranking in the recommendation list")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recommendation for {self.user_profile.name} - {self.university_name}"
    
    class Meta:
        ordering = ['rank', '-match_score']

