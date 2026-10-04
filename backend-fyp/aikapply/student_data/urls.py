
from django.urls import path
from .views import StudentProfileSubmitAPIView, StudentProfileUpdateAPIView

urlpatterns = [

    path('profile/', StudentProfileSubmitAPIView.as_view(), name='student-profile-api'),
        path('profile/edit/', StudentProfileUpdateAPIView.as_view(), name='edit-profile'),
]