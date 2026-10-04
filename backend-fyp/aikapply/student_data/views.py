
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import StudentProfile
from .serializers import StudentProfileSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Bypasses the CSRF validation

# class StudentProfileSubmitAPIView(APIView):
#     # 2. Use the exempt authentication class
#     authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
#     permission_classes = [permissions.IsAuthenticated]
    
#     # 3. Parsers to handle the files (images/PDFs) you are sending
#     parser_classes = [MultiPartParser, FormParser, JSONParser]

#     def post(self, request):
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import StudentProfile
from .serializers import StudentProfileSerializer

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

class StudentProfileSubmitAPIView(APIView):

    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        try:

            StudentProfile.objects.filter(user=request.user).delete()


            serializer = StudentProfileSerializer(data=request.data)
            
            if serializer.is_valid():

                serializer.save(user=request.user)
                return Response({
                    "message": "Application submitted!",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            print("System Error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            profile = StudentProfile.objects.get(user=request.user)
            return Response(StudentProfileSerializer(profile).data)
        except StudentProfile.DoesNotExist:
            return Response({"message": "Not found"}, status=404)
        


#edit my user using request.user 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import StudentProfile
from .serializers import StudentProfileSerializer

class StudentProfileUpdateAPIView(APIView):
   
    permission_classes = [permissions.IsAuthenticated]

    authentication_classes = [CsrfExemptSessionAuthentication] 

    def get(self, request):
     
        try:
            profile = StudentProfile.objects.get(user=request.user)
            serializer = StudentProfileSerializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

    def patch(self, request):
      
        try:
            profile = StudentProfile.objects.get(user=request.user)
    
            serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Profile updated successfully!",
                    "data": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)