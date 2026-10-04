"""
deadline_tracker/urls.py

Include in your project's urls.py:
    path("api/deadlines/", include("deadline_tracker.urls")),
"""

from django.urls import path
from . import views

urlpatterns = [
    # Health / status — call this first from React to detect empty DB
    path("db-status/",  views.DBStatusView.as_view(),       name="deadline-db-status"),

    # Aggregated summary (main endpoint for the dashboard)
    path("summary/",    views.DeadlineSummaryView.as_view(), name="deadline-summary"),

    # List all (with ?priority= and ?search= filters)
    path("",            views.UniversityListView.as_view(),  name="university-list"),

    # Upload an Excel file
    path("upload/",     views.ExcelUploadView.as_view(),     name="deadline-upload"),

    # Upload history
    path("uploads/",    views.UploadHistoryView.as_view(),   name="upload-history"),

    # Wipe everything
    path("clear/",      views.ClearAllView.as_view(),        name="deadline-clear"),

    # Single university — keep last (catch-all slug)
    path("<str:university_id>/", views.UniversityDetailView.as_view(), name="university-detail"),
]