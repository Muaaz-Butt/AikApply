from django.urls import path
from .views import LoginAPIView, LogoutAPIView,signup_test,signup,ChangePasswordAPIView,MeAPIView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('signuptest/', signup_test, name='signup'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('me/', MeAPIView.as_view(), name='me'),

]
