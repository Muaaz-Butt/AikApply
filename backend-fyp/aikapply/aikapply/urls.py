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
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.http import FileResponse, Http404
from django.views.static import serve as serve_file


def frontend_app(request):
    """Serve the built React app's index.html; React Router handles the page."""
    index = settings.FRONTEND_DIST / "index.html"
    if not index.is_file():
        raise Http404("Frontend build not found")
    return FileResponse(open(index, "rb"), content_type="text/html")


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

if not settings.DEBUG:
    # static() only works in DEBUG; serve uploads (photos, screenshots) in production too
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve_file, {"document_root": settings.MEDIA_ROOT}),
    ]

# Every other path is a React page (/, /login, /dashboard, ...) when the built app is present
if settings.FRONTEND_DIST.is_dir():
    urlpatterns += [
        re_path(
            r"^(?!admin/|auth/|student/|ai_mapping/|automation_engine/|api/|api_tools/|demo-portals/|media/|static/).*$",
            frontend_app,
        ),
    ]
