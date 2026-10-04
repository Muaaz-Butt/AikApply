"""
automation_pipline/urls.py

URL routing for the automation pipeline.
"""

from django.urls import path
from .views import ApplyPipelineView

app_name = 'automation_pipline'

urlpatterns = [
    path("apply/", ApplyPipelineView.as_view(), name="apply-pipeline"),
]