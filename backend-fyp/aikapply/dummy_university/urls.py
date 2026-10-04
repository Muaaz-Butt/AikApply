from django.urls import path

from . import views

urlpatterns = [
    path("submissions/", views.submissions, name="demo-portal-submissions"),
    path("<slug:slug>/", views.portal, name="demo-portal"),
    path("<slug:slug>/submit/", views.submit, name="demo-portal-submit"),
]
