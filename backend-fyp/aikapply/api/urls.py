from django.urls import path
from .views import parse_form, map_fields, submit_application, ChatbotAPIView

urlpatterns = [
    path("parse/", parse_form),
    path("map/", map_fields),
    path("submit/", submit_application),
    path("chat/", ChatbotAPIView.as_view(), name="chat"),
]
