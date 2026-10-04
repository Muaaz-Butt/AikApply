"""
automation_pipline/apps.py

Django app configuration.
"""

from django.apps import AppConfig


class AutomationPiplineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "automation_pipline"  # ✅ Your actual app name
    verbose_name = "Automation Pipeline"