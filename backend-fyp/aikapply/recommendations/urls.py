from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, UniversityViewSet, RecommendationViewSet

router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')
router.register(r'universities', UniversityViewSet, basename='university')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
]


