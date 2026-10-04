from rest_framework.decorators import api_view
from rest_framework.response import Response
import os


CHROME_PATH = "C:/Users/HP/Downloads/chromedriver-win64/chromedriver.exe"

STUDENT_DATA = {
    "student_name": "Ali Khan",
    "student_cnic": "12345-1111111-1",
    "father_name": "Ahmed Khan"
}

@api_view(["POST"])
def parse_form(request):
    url = request.data.get("url")


@api_view(["POST"])
def map_fields(request):
    fields = request.data.get("fields")
   
 
@api_view(["POST"])
def submit_application(request):
    url = request.data.get("url")
    mappings = request.data.get("mappings")



from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
import requests as http_requests
import uuid
import traceback
from django.conf import settings
from .models import ChatSession, ChatMessage
from .utils import get_university_context

GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'

class ChatbotAPIView(APIView):
    """
    Public chatbot endpoint - no auth/CSRF required.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            session_id = request.query_params.get('session_id')
            if not session_id:
                return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate session_id
            try:
                valid_uuid = str(uuid.UUID(str(session_id)))
            except (ValueError, AttributeError):
                return Response({"error": "Invalid session_id"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve session
            try:
                session = ChatSession.objects.get(id=valid_uuid)
            except ChatSession.DoesNotExist:
                return Response({"messages": []}, status=status.HTTP_200_OK)

            # Retrieve ordered history
            history = session.messages.order_by('timestamp')
            
            # Format output
            data = []
            for msg in history:
                data.append({
                    "id": msg.id,
                    "role": "bot" if msg.role == "model" else "user",
                    "text": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                })
                
            return Response({"messages": data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[CHATBOT GET ERROR] {tb}")
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            session_id = request.data.get('session_id')
            user_message = request.data.get('message', '').strip()

            if not user_message:
                return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate session_id is a valid UUID
            valid_uuid = None
            if session_id:
                try:
                    valid_uuid = str(uuid.UUID(str(session_id)))
                except (ValueError, AttributeError):
                    valid_uuid = None

            # Retrieve or create session
            if valid_uuid:
                session, _ = ChatSession.objects.get_or_create(id=valid_uuid)
            else:
                session = ChatSession.objects.create()

            # Save user message
            ChatMessage.objects.create(session=session, role='user', content=user_message)

            # Build prompt history
            history = list(session.messages.order_by('timestamp'))

            # System instructions
            university_data = get_university_context()
            system_instruction = f"""
You are an empathetic, highly professional Career Counselor and University Advisor. You speak with a warm, encouraging, and human tone—do not sound robotic, mechanical, or like an AI.
Task 1: Provide career consulting based on the user's expressed interests, addressing them thoughtfully and naturally.
Task 2: Recommend the best universities strictly based on the provided dataset. Frame these recommendations as tailored, professional advice to help them succeed.
Task 3: Answer general study, degree, and career-related questions with approachable expertise.
Constraint: If the user asks anything outside of careers, studies, or university recommendations, politely and warmly steer the conversation back to your specific area of expertise, stating it is outside your scope.
Formatting: Weave data naturally into your conversation, but safely use Markdown formatting (bolding, italics, bullet points, and tables) to keep your advice highly readable and structured when comparing universities or career stats.

University Dataset Context:
{university_data}
"""

            # Construct JSON Request for Gemini REST API
            contents = []
            for msg in history[:-1]:  # Exclude the latest user message
                role = "user" if msg.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg.content}]})

            contents.append({"role": "user", "parts": [{"text": user_message}]})

            payload = {
                "system_instruction": {
                    "parts": [{"text": system_instruction}]
                },
                "contents": contents
            }

            api_key = settings.GEMINI_API_KEY
            print(f"[CHATBOT DEBUG] API Key loaded: {'YES (' + api_key[:8] + '...)' if api_key else 'NO - EMPTY!'}")
            print(f"[CHATBOT DEBUG] Session: {session.id}, Message: {user_message[:50]}")

            headers = {'Content-Type': 'application/json'}
            params = {'key': api_key}

            response = http_requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=60)

            print(f"[CHATBOT DEBUG] Gemini response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                ai_text = result['candidates'][0]['content']['parts'][0]['text']

                # Save AI message
                ChatMessage.objects.create(session=session, role='model', content=ai_text)

                return Response({
                    "session_id": str(session.id),
                    "reply": ai_text
                }, status=status.HTTP_200_OK)
            else:
                error_detail = response.text[:500]
                print(f"[CHATBOT ERROR] Gemini returned {response.status_code}: {error_detail}")
                return Response({"error": f"Gemini API Error ({response.status_code}): {error_detail}"}, status=status.HTTP_502_BAD_GATEWAY)

        except Exception as e:
            tb = traceback.format_exc()
            print(f"[CHATBOT FATAL ERROR] {tb}")
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
