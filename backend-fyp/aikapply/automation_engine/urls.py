# from django.urls import path
# from .views import submit_application

# urlpatterns = [
#     path("submit/", submit_application),
# ]
from django.urls import path
from .views import SubmitApplicationView

urlpatterns = [
    path("submit/", SubmitApplicationView.as_view(), name="submit-application"),
 
]