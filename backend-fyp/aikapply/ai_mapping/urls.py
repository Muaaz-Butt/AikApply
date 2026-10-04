# from django.urls import path
# from django.views.decorators.csrf import csrf_exempt
# from .views import GenerateAutomationView

# urlpatterns = [
#     # Wrapping the view in csrf_exempt bypasses the token check
#     path('generate-mapping/', csrf_exempt(GenerateAutomationView.as_view()), name='generate-mapping'),
# ]
"""
mapping/urls.py

New endpoint added:
  GET /mapping/get/<app_id>/  →  returns the saved mapping JSON from disk
  (React can use this to show a preview or pass mapping_file to automation)
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import GenerateAutomationView

urlpatterns = [
    # Generate (or regenerate) mapping for a given URL
    path(
        "generate-mapping/",
        csrf_exempt(GenerateAutomationView.as_view()),
        name="generate-mapping",
    ),

    # # Retrieve previously saved mapping by app_id
    # path(
    #     "get-mapping/<int:app_id>/",
    #     csrf_exempt(RetrieveMappingView.as_view()),
    #     name="get-mapping",
    # ),
]

# from django.urls import path
# from .views import GenerateAutomationView

# urlpatterns = [
#     # Endpoint to trigger the AI mapping logic
#     path('generate-mapping/', GenerateAutomationView.as_view(), name='generate_mapping'),
# ]