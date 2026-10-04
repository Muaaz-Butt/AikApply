# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from .models import University, FieldMapping
# # from student_data.models import StudentProfile
# from .utils import build_application_steps


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from rest_framework.authentication import SessionAuthentication
# from student_data.models import StudentProfile
# from student_data.serializers import StudentProfileSerializer
# from .services import AIService


# class CsrfExemptSessionAuthentication(SessionAuthentication):
#     def enforce_csrf(self, request):
#         return  # Do nothing, bypassing the check

# class GenerateAutomationView(APIView):
#     # Order matters: check who they are, then if they are allowed
#     authentication_classes = [CsrfExemptSessionAuthentication] 
#     permission_classes = [permissions.IsAuthenticated]
   
#     def post(self, request):
#         target_url = request.data.get("url")
#         if not target_url:
#             return Response({"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST)

#         # 2. Get data for logged in user
#         try:
#             # request.user is available because of IsAuthenticated permission
#             profile = StudentProfile.objects.get(user=request.user)
#         except StudentProfile.DoesNotExist:
#             return Response({
#                 "error": "profile_missing",
#                 "message": "Please complete your application form before using auto-apply."
#             }, status=status.HTTP_404_NOT_FOUND)

#         student_data = StudentProfileSerializer(profile).data
        
#         # 3. Call AI Service
#         ai_service = AIService()
#         try:
#             # Note: Ensure your AIService.get_automation_instructions 
#             # accepts target_url, student_data, and app_id
#             mapping_result = ai_service.get_automation_instructions(
#                 target_url=target_url,
#                 student_data=student_data,
#                 app_id=profile.id
#             )
            
#             # Using .dict() because mapping_result is a Pydantic object from LangChain
#             return Response(mapping_result.dict(), status=status.HTTP_200_OK)
            
#         except Exception as e:
#             # Catching AI or Connection errors
#             return Response({
#                 "error": "ai_mapping_failed",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
mapping/views.py

Drop-in replacement. Key changes vs original:
  - After getting the AI mapping, we NOW save it to media/mappings/<app_id>_mapping.json
    so the automation task can load it by file path.
  - The response now includes "mapping_file" (relative path) and "application_id"
    so the React frontend can pass mapping_file straight to the submit_application
    endpoint without any extra step.
  - application_id is stable (same student + url = same id) via AIService.make_app_id().
  - All existing authentication and permission logic is kept exactly as-is.
"""

import json
import os
from pathlib import Path

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication

from student_data.models import StudentProfile
from student_data.serializers import StudentProfileSerializer
from .services import AIService


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Bypass CSRF for API calls from React


class GenerateAutomationView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        target_url = request.data.get("url")
        if not target_url:
            return Response(
                {"error": "URL is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Get logged-in student's profile
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    "error": "profile_missing",
                    "message": "Please complete your application form before using auto-apply.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        student_data = StudentProfileSerializer(profile).data

        # 2. Compute stable application_id
        ai_service = AIService()
        app_id = AIService.make_app_id(profile.id, target_url)

        # 3. Call AI Service to get the mapping
        try:
            mapping_result = ai_service.get_automation_instructions(
                target_url=target_url,
                student_data=student_data,
                app_id=app_id,
            )
        except Exception as e:
            return Response(
                {"error": "ai_mapping_failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 4. Convert Pydantic model → plain dict
        mapping_dict = mapping_result.dict()

        # Ensure application_id and url are top-level (schema may nest them)
        mapping_dict["application_id"] = app_id
        mapping_dict["url"] = target_url

        # 5. Save mapping JSON to media/mappings/<app_id>_mapping.json
        mappings_dir = Path(settings.MEDIA_ROOT) / "mappings"
        mappings_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{app_id}_mapping.json"
        file_path = mappings_dir / file_name
        with open(file_path, "w") as f:
            json.dump(mapping_dict, f, indent=2)

        # Relative path that the automation view expects
        relative_mapping_path = str(Path("mappings") / file_name)

        # 6. Return mapping + file path to the React frontend
        return Response(
            {
                **mapping_dict,
                # React should store this and send it to /automation/submit/
                "mapping_file": relative_mapping_path,
            },
            status=status.HTTP_200_OK,
        )