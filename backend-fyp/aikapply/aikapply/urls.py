"""
URL configuration for aikapply project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')), 
    path('student/', include('student_data.urls')),
    path('ai_mapping/', include('ai_mapping.urls')),
    # path("api/", include("api.urls")),
    path("automation_engine/", include("automation_engine.urls")),
    path("api/", include("recommendations.urls")),
    path("api_tools/", include("api.urls")),
    path('api/automation-pipeline/', include('automation_pipline.urls')),
     path("api/deadlines/", include("deadline.urls")),
    # Local demo university portals for testing auto-apply (see dummy_university/views.py)
    path("demo-portals/", include("dummy_university.urls")),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
