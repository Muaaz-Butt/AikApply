from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
# import threading
# from .tasks import run_application

# # 1. Your Custom Authentication Class
# class CsrfExemptSessionAuthentication(SessionAuthentication):
#     def enforce_csrf(self, request):
#         return  # Bypass CSRF

# @api_view(["POST"])
# # 2. Use these specific decorators for function-based views
# @authentication_classes([CsrfExemptSessionAuthentication])
# @permission_classes([permissions.IsAuthenticated])
# def submit_application(request):
#     mapping_file = request.data.get("mapping_file")

#     if not mapping_file:
#         return Response({"error": "No mapping data provided"}, status=400)

#     # Start the Selenium/Automation task in a background thread
#     threading.Thread(
#         target=run_application,
#         args=(mapping_file,)
#     ).start()

#     return Response({
#         "status": "processing",
#         "message": "Automation has started in the background",
#         "mapping_file": mapping_file
#     })

# import json
# import traceback
# from pathlib import Path

# from django.conf import settings
# from rest_framework import permissions, status
# from rest_framework.authentication import SessionAuthentication
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .service import AutomationService

# # ----------------------------------------------------------------
# # CSRF Bypass for API Testing
# # ----------------------------------------------------------------
# class CsrfExemptSessionAuthentication(SessionAuthentication):
#     """
#     Bypasses CSRF validation so you can test POST requests in Postman 
#     using Session Authentication.
#     """
#     def enforce_csrf(self, request):
#         return

# # ----------------------------------------------------------------
# # Automation View
# # ----------------------------------------------------------------
# class SubmitApplicationView(APIView):
#     """
#     Receives a mapping (via file path or raw JSON) and executes 
#     the Selenium automation engine.
#     """
#     authentication_classes = [CsrfExemptSessionAuthentication]
#     # permission_classes = [permissions.IsAuthenticated]
#     permission_classes = [permissions.AllowAny]
#     def post(self, request):
#         mapping_file_path = request.data.get("mapping_file")
#         raw_mapping_data = request.data.get("mapping_data")
#         uni_id = request.data.get("university_id")

#         try:
#             # --------------------------------------------------
#             # 1. HANDLE university_id (🔥 NEW LOGIC)
#             # --------------------------------------------------
#             if uni_id:
#                 mapping_map = {
#                    "u1": "mappings/844445_mapping.json",
#                     "u2": "mappings/368519_mapping.json",
#                     "u3": "mappings/844445_mapping.json",
#                     "u4": "mappings/368519_mapping.json",
#                     # 👉 add more universities here
#                 }


#                 selected_mapping = mapping_map.get(uni_id)

#                 if not selected_mapping:
#                     return Response(
#                         {"status": "failed", "message": "Invalid university_id"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 full_path = Path(settings.MEDIA_ROOT) / selected_mapping

#                 if not full_path.exists():
#                     return Response(
#                         {
#                             "status": "failed",
#                             "message": f"Mapping file not found: {full_path}"
#                         },
#                         status=status.HTTP_404_NOT_FOUND
#                     )

#                 with open(full_path, "r") as f:
#                     mapping_data = json.load(f)

#             # --------------------------------------------------
#             # 2. HANDLE RAW JSON (fallback)
#             # --------------------------------------------------
#             elif raw_mapping_data:
#                 mapping_data = raw_mapping_data

#             # --------------------------------------------------
#             # 3. HANDLE FILE PATH (fallback)
#             # --------------------------------------------------
#             if mapping_file_path:
#                 full_path = Path(settings.MEDIA_ROOT) / mapping_file_path.lstrip('/')

#                 if not full_path.exists():
#                     return Response(
#                         {
#                             "status": "failed",
#                             "message": f"Mapping file not found at: {full_path}"
#                         },
#                         status=status.HTTP_404_NOT_FOUND
#                     )

#                 with open(full_path, "r") as f:
#                     mapping_data = json.load(f)

#             # --------------------------------------------------
#             # 4. NO INPUT PROVIDED
#                         # --------------------------------------------------
#             if not mapping_file_path and not raw_mapping_data:
#                 return Response(
#                     {
#                         "status": "failed",
#                         "message": "Provide 'mapping_file' or 'mapping_data'"
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#     )

#             # --------------------------------------------------
#             # 5. RUN AUTOMATION
#             # --------------------------------------------------
#             print(f"🚀 Starting Automation for App ID: {mapping_data.get('application_id')}")

#             service = AutomationService()
#             result = service.run(mapping_data)

#             # --------------------------------------------------
#             # 6. RETURN RESPONSE
#             # --------------------------------------------------
#             if result.get("status") == "failed":
#                 return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

#             return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             traceback.print_exc()


#             return Response(
#                 {
#                     "status": "failed",
#                     "message": "A critical error occurred",
#                     "details": str(e)
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
import json
import traceback
from pathlib import Path

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from .service import AutomationService


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class SubmitApplicationView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mapping_file_path = request.data.get("mapping_file")
        raw_mapping_data = request.data.get("mapping_data")
        uni_id = request.data.get("university_id")

        mapping_data = None

        try:
            # --------------------------------------------------
            # DEBUG: Incoming request
            # --------------------------------------------------
            print("\n================ NEW REQUEST ================")
            print("UNIVERSITY ID:", uni_id)
            print("MAPPING FILE:", mapping_file_path)
            print("RAW DATA:", bool(raw_mapping_data))

            # --------------------------------------------------
            # 1. UNIVERSITY ID MAPPING
            # --------------------------------------------------
            if uni_id:
                mapping_map = {
                    "u1": "mappings/844445_mapping.json",
                    "u2": "mappings/368519_mapping.json",
                    "u3": "mappings/844445_mapping.json",
                    "u4": "mappings/368519_mapping.json",
                }

                selected_mapping = mapping_map.get(uni_id)

                print("SELECTED MAPPING:", selected_mapping)

                if not selected_mapping:
                    return Response(
                        {"status": "failed", "message": "Invalid university_id"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                full_path = Path(settings.MEDIA_ROOT) / selected_mapping
                print("FULL PATH:", full_path)

                if not full_path.exists():
                    return Response(
                        {
                            "status": "failed",
                            "message": f"Mapping file not found: {full_path}"
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )

                with open(full_path, "r") as f:
                    mapping_data = json.load(f)

            # --------------------------------------------------
            # 2. RAW JSON FALLBACK
            # --------------------------------------------------
            elif raw_mapping_data:
                print("USING RAW MAPPING DATA")
                mapping_data = raw_mapping_data

            # --------------------------------------------------
            # 3. FILE PATH FALLBACK
            # --------------------------------------------------
            elif mapping_file_path:
                print("USING FILE PATH MAPPING")

                full_path = Path(settings.MEDIA_ROOT) / mapping_file_path.lstrip("/")
                print("FULL PATH:", full_path)

                if not full_path.exists():
                    return Response(
                        {"status": "failed", "message": f"File not found: {full_path}"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                with open(full_path, "r") as f:
                    mapping_data = json.load(f)

            else:
                return Response(
                    {
                        "status": "failed",
                        "message": "Provide 'university_id' or 'mapping_file' or 'mapping_data'"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --------------------------------------------------
            # FINAL VALIDATION
            # --------------------------------------------------
            if not mapping_data:
                return Response(
                    {"status": "failed", "message": "Mapping data is empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            print("\n🔥 FINAL MAPPING DATA LOADED")
            print("Keys:", list(mapping_data.keys()))

            # --------------------------------------------------
            # RUN AUTOMATION
            # --------------------------------------------------
            print("\n🚀 STARTING AUTOMATION ENGINE...")

            service = AutomationService()
            result = service.run(mapping_data)

            # --------------------------------------------------
            # DEBUG RESULT
            # --------------------------------------------------
            print("\n🔥 AUTOMATION RESULT:")
            print(json.dumps(result, indent=2, default=str))

            # --------------------------------------------------
            # RESPONSE HANDLING
            # --------------------------------------------------
            if result.get("status") == "failed":
                print("\n❌ AUTOMATION FAILED")
                print("Error:", result.get("message"))
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            print("\n✅ AUTOMATION SUCCESS")
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            print("\n💥 UNEXPECTED ERROR OCCURRED")
            traceback.print_exc()

            return Response(
                {
                    "status": "failed",
                    "message": "A critical error occurred",
                    "details": str(e),
                    "traceback": traceback.format_exc()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
#-----------3-------
# import json
# import traceback
# from pathlib import Path

# from django.conf import settings
# from rest_framework import permissions, status
# from rest_framework.authentication import SessionAuthentication
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .service import AutomationService


# class CsrfExemptSessionAuthentication(SessionAuthentication):
#     def enforce_csrf(self, request):
#         return


# class SubmitApplicationView(APIView):
#     authentication_classes = [CsrfExemptSessionAuthentication]
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         mapping_file_path = request.data.get("mapping_file")
#         raw_mapping_data = request.data.get("mapping_data")
#         uni_id = request.data.get("university_id")

#         mapping_data = None

#         try:
#             # --------------------------------------------------
#             # 1. PRIORITY: university_id
#             # --------------------------------------------------
#             if uni_id:
#                 mapping_map = {
#                     "u1": "mappings/844445_mapping.json",
#                     "u2": "mappings/368519_mapping.json",
#                     "u3": "mappings/844445_mapping.json",
#                     "u4": "mappings/368519_mapping.json",
#                 }

#                 selected_mapping = mapping_map.get(uni_id)

#                 if not selected_mapping:
#                     return Response(
#                         {"status": "failed", "message": "Invalid university_id"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 full_path = Path(settings.MEDIA_ROOT) / selected_mapping

#                 if not full_path.exists():
#                     return Response(
#                         {"status": "failed", "message": f"Mapping file not found: {full_path}"},
#                         status=status.HTTP_404_NOT_FOUND
#                     )

#                 with open(full_path, "r") as f:
#                     mapping_data = json.load(f)

#             # --------------------------------------------------
#             # 2. SECOND: raw JSON
#             # --------------------------------------------------
#             elif raw_mapping_data:
#                 mapping_data = raw_mapping_data

#             # --------------------------------------------------
#             # 3. THIRD: file path
#             # --------------------------------------------------
#             elif mapping_file_path:
#                 full_path = Path(settings.MEDIA_ROOT) / mapping_file_path.lstrip("/")

#                 if not full_path.exists():
#                     return Response(
#                         {"status": "failed", "message": f"Mapping file not found: {full_path}"},
#                         status=status.HTTP_404_NOT_FOUND
#                     )

#                 with open(full_path, "r") as f:
#                     mapping_data = json.load(f)

#             # --------------------------------------------------
#             # 4. NOTHING PROVIDED
#             # --------------------------------------------------
#             else:
#                 return Response(
#                     {
#                         "status": "failed",
#                         "message": "Provide 'university_id' or 'mapping_file' or 'mapping_data'"
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # --------------------------------------------------
#             # 5. VALIDATE FINAL DATA
#             # --------------------------------------------------
#             if not mapping_data:
#                 return Response(
#                     {"status": "failed", "message": "Mapping data could not be loaded"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # --------------------------------------------------
#             # 6. RUN AUTOMATION
#             # --------------------------------------------------
#             print(f"🚀 Starting Automation for App ID: {mapping_data.get('application_id')}")

#             service = AutomationService()
#             result = service.run(mapping_data)

#             # --------------------------------------------------
#             # 7. RESPONSE
#             # --------------------------------------------------
#             if result.get("status") == "failed":
#                 return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

#             return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             traceback.print_exc()
#             return Response(
#                 {
#                     "status": "failed",
#                     "message": "A critical error occurred",
#                     "details": str(e)
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )







    # def post(self, request):
    #     mapping_file_path = request.data.get("mapping_file")
    #     raw_mapping_data = request.data.get("mapping_data")

    #     try:
    #         # 1. IDENTIFY MAPPING SOURCE
    #         if raw_mapping_data:
    #             # Use JSON sent directly in the request body
    #             mapping_data = raw_mapping_data
    #         elif mapping_file_path:
    #             # Use a JSON file stored in the media directory
    #             # lstrip ensures we don't have issues with leading slashes
    #             full_path = Path(settings.MEDIA_ROOT) / mapping_file_path.lstrip('/')

    #             if not full_path.exists():
    #                 return Response(
    #                     {
    #                         "status": "failed", 
    #                         "message": f"Mapping file not found at: {full_path}"
    #                     },
    #                     status=status.HTTP_404_NOT_FOUND
    #                 )

    #             with open(full_path, "r") as f:
    #                 mapping_data = json.load(f)
    #         else:
    #             return Response(
    #                 {"error": "You must provide either 'mapping_file' or 'mapping_data'"},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         # 2. TRIGGER AUTOMATION SERVICE
    #         print(f"🚀 Starting Automation for App ID: {mapping_data.get('application_id')}")
            
    #         service = AutomationService()
    #         # This is where the Selenium magic (and your #nationality error) happens
    #         result = service.run(mapping_data)

    #         # 3. ANALYZE RESULTS
    #         if result.get("status") == "failed":
    #             # Return 422 (Unprocessable Entity) for logic/element failures
    #             return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    #         return Response(result, status=status.HTTP_200_OK)

    #     except json.JSONDecodeError:
    #         return Response(
    #             {"status": "failed", "message": "Invalid JSON format in mapping file."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     except Exception as e:
    #         # CRITICAL: This prints the full Selenium error to your terminal/console
    #         # This is how you'll know if the driver crashed or if the ID was wrong.
    #         traceback.print_exc() 
            
    #         return Response(
    #             {
    #                 "status": "failed",
    #                 "message": "A critical error occurred in the Automation View.",
    #                 "details": str(e)
    #             },
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

