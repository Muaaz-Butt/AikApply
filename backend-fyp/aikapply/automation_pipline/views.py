"""
automation_pipline/views.py

Unified pipeline view.

POST /automation-pipeline/apply/
Body: { "url": "https://university-portal.com/apply" }

Steps (all in one request):
  1. Authenticate the logged-in student
  2. Fetch their StudentProfile
  3. Call AIService to generate the field mapping
  4. Save the mapping JSON to media/mappings/<profile_id>_mapping.json  (url excluded — portal-agnostic)
  5. Feed mapping_dict (with url injected at runtime) into AutomationService
  6. Return the automation result + mapping metadata
"""

import json
import traceback
from pathlib import Path

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from student_data.models import StudentProfile
from student_data.serializers import StudentProfileSerializer

# ✅ FIXED: Use relative imports from the same app
from .services import AIService, AutomationService


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Skip CSRF enforcement so React/mobile clients can POST without a cookie."""
    def enforce_csrf(self, request):
        return


@method_decorator(csrf_exempt, name='dispatch')
class ApplyPipelineView(APIView):
    """
    Single endpoint that:
      - generates the AI mapping for the logged-in student
      - immediately runs the browser automation
      - returns the final automation result
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        # ------------------------------------------------------------------ #
        # 0. INPUT VALIDATION                                                 #
        # ------------------------------------------------------------------ #
        target_url = request.data.get("url")
        if not target_url:
            return Response(
                {"status": "failed", "message": "url is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print("\n================ APPLY PIPELINE ================")
        print("USER   :", request.user)
        print("URL    :", target_url)

        # ------------------------------------------------------------------ #
        # 1. LOAD STUDENT PROFILE                                             #
        # ------------------------------------------------------------------ #
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": "profile_missing",
                    "message": (
                        "Please complete your application form "
                        "before using auto-apply."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        student_data = StudentProfileSerializer(profile).data
        print("PROFILE:", profile.id)

        # ------------------------------------------------------------------ #
        # 2. GENERATE AI MAPPING                                              #
        # app_id is student-scoped only so the same mapping file              #
        # works for every portal this student applies to                      #
        # ------------------------------------------------------------------ #
        try:
            ai_service = AIService()
            app_id = str(profile.id)

            print("APP ID :", app_id)
            print("Calling AIService.get_automation_instructions ...")

            mapping_result = ai_service.get_automation_instructions(
                target_url=target_url,
                student_data=student_data,
                app_id=app_id,
            )
        except Exception as e:
            print("❌ AI MAPPING FAILED")
            traceback.print_exc()
            return Response(
                {
                    "status": "failed",
                    "error": "ai_mapping_failed",
                    "message": "Failed to generate field mapping.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ------------------------------------------------------------------ #
        # 3. NORMALISE MAPPING → plain dict                                   #
        # Support both Pydantic models (.dict()) and plain dicts              #
        # ------------------------------------------------------------------ #
        mapping_dict = (
            mapping_result.dict()
            if hasattr(mapping_result, "dict")
            else mapping_result
        )

        # url is injected at runtime from the request — not hardcoded in file
        # so the same student mapping works for any portal
        mapping_dict["url"] = target_url
        mapping_dict["application_id"] = app_id

        print("MAPPING KEYS:", list(mapping_dict.keys()))

        # ------------------------------------------------------------------ #
        # 4. PERSIST MAPPING FILE                                             #
        # Named by profile_id only — portal-agnostic                         #
        # url is excluded from the saved file and injected fresh each call    #
        # ------------------------------------------------------------------ #
        try:
            mappings_dir = Path(settings.MEDIA_ROOT) / "mappings"
            mappings_dir.mkdir(parents=True, exist_ok=True)

            file_name = f"{profile.id}_mapping.json"
            file_path = mappings_dir / file_name

            # Exclude url so file stays reusable across portals
            mapping_to_save = {k: v for k, v in mapping_dict.items() if k != "url"}

            with open(file_path, "w") as f:
                json.dump(mapping_to_save, f, indent=2)

            relative_mapping_path = str(Path("mappings") / file_name)
            print("MAPPING SAVED →", file_path)

        except Exception as e:
            # Non-fatal: automation can still run from in-memory mapping_dict
            print("⚠️  Could not save mapping file:", e)
            relative_mapping_path = None

        # ------------------------------------------------------------------ #
        # 5. RUN AUTOMATION                                                   #
        # mapping_dict already has url injected — automation gets everything  #
        # ------------------------------------------------------------------ #
        try:
            print("\n🚀 STARTING AUTOMATION ENGINE...")
            automation_service = AutomationService()
            result = automation_service.run(mapping_dict)

        except Exception as e:
            print("💥 AUTOMATION CRASHED")
            traceback.print_exc()
            return Response(
                {
                    "status": "failed",
                    "error": "automation_crashed",
                    "message": "Automation engine threw an unexpected error.",
                    "details": str(e),
                    "traceback": traceback.format_exc(),
                    "mapping_file": relative_mapping_path,
                    "application_id": app_id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        print("\n🔥 AUTOMATION RESULT:")
        print(json.dumps(result, indent=2, default=str))

        # ------------------------------------------------------------------ #
        # 6. RETURN RESULT                                                    #
        # ------------------------------------------------------------------ #
        if result.get("status") == "failed":
            print("❌ AUTOMATION REPORTED FAILURE")
            result["mapping_file"] = relative_mapping_path
            result["application_id"] = app_id
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        print("✅ PIPELINE COMPLETE")
        return Response(
            {
                **result,
                "mapping_file": relative_mapping_path,
                "application_id": app_id,
            },
            status=status.HTTP_200_OK,
        )