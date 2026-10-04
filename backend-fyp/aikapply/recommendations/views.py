from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import models
from .models import UserProfile, University, Recommendation
from .serializers import (
    UserProfileSerializer, 
    UserProfileCreateSerializer,
    UniversitySerializer, 
    RecommendationSerializer,
    FrontendUserProfileSerializer,
    FrontendRecommendationSerializer
)
from .services import GeminiRecommendationService
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles
    """
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = UserProfile.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserProfileCreateSerializer
        return UserProfileSerializer
    
    @action(detail=True, methods=['get', 'post'], url_path='get-recommendations')
    def get_recommendations(self, request, pk=None):
        """
        Generate recommendations for a user profile using Gemini AI
        GET or POST /api/user-profiles/{id}/get-recommendations/
        Returns list of recommended universities
        """
        user_profile = get_object_or_404(UserProfile, pk=pk)
        
        # Check if recommendations already exist
        existing_recommendations = Recommendation.objects.filter(user_profile=user_profile)
        
        # If recommendations exist and it's a GET request, return them
        if request.method == 'GET' and existing_recommendations.exists():
            serializer = RecommendationSerializer(existing_recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Generate new recommendations (for POST or if no existing recommendations on GET)
        try:
            # Delete old recommendations if generating new ones via POST
            if request.method == 'POST':
                existing_recommendations.delete()
            
            # Initialize Gemini service
            gemini_service = GeminiRecommendationService()
            
            # Generate recommendations
            recommendations_data = gemini_service.generate_recommendations(user_profile)
            
            # Save recommendations to database
            saved_recommendations = []
            for rec_data in recommendations_data:
                recommendation = Recommendation.objects.create(**rec_data)
                saved_recommendations.append(recommendation)
            
            # Serialize and return
            serializer = RecommendationSerializer(saved_recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error generating recommendations: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='recommendations')
    def list_recommendations(self, request, pk=None):
        """
        Get all recommendations for a user profile
        GET /api/user-profiles/{id}/recommendations/
        """
        user_profile = get_object_or_404(UserProfile, pk=pk)
        recommendations = Recommendation.objects.filter(user_profile=user_profile)
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='submit-and-recommend')
    def submit_and_recommend(self, request):
        """
        Accept frontend form data, create/update user profile, and return recommendations
        POST /api/user-profiles/submit-and-recommend/
        Returns recommendations in frontend-expected format
        """
        print("DATA RECEIVED:", request.data)
        try:
            # Validate and transform frontend data
            frontend_serializer = FrontendUserProfileSerializer(data=request.data)
            if not frontend_serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid data',
                    'details': frontend_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get transformed data (mapped from camelCase to snake_case)
            transformed_data = frontend_serializer.get_mapped_data()
            
            # Create or update user profile (based on email)
            user_profile, created = UserProfile.objects.update_or_create(
                email=transformed_data['email'],
                defaults=transformed_data
            )
            
            # Delete old recommendations if they exist
            Recommendation.objects.filter(user_profile=user_profile).delete()
            
            # Generate new recommendations
            gemini_service = GeminiRecommendationService()
            recommendations_data = gemini_service.generate_recommendations(user_profile)
            
            # Save recommendations to database
            saved_recommendations = []
            for rec_data in recommendations_data:
                recommendation = Recommendation.objects.create(**rec_data)
                saved_recommendations.append(recommendation)
            
            # Transform recommendations to frontend format
            frontend_recommendations = []
            for rec in saved_recommendations:
                # Map university_type to frontend format
                # First check if university object exists and has type
                if rec.university and rec.university.university_type:
                    uni_type = 'Public' if rec.university.university_type == 'public' else 'Private'
                else:
                    # Infer from university name
                    uni_name_lower = (rec.university_name or '').lower()
                    public_keywords = ['uet', 'nust', 'punjab university', 'comsats', 'qau', 'ned', 'karachi university', 'quaid', 'air university', 'gcu', 'nca']
                    private_keywords = ['lums', 'fast', 'iba', 'szabist', 'bnu', 'umt', 'bahria', 'riphah', 'habib']
                    
                    if any(keyword in uni_name_lower for keyword in public_keywords):
                        uni_type = 'Public'
                    elif any(keyword in uni_name_lower for keyword in private_keywords):
                        uni_type = 'Private'
                    else:
                        # Default to Public if unclear
                        uni_type = 'Public'
                
                # Format fee information
                fee_display = rec.fee_information or 'Contact university for details'
                
                # Format rank
                rank_display = f"#{rec.rank}" if rec.rank else "N/A"
                
                frontend_rec = {
                    'id': rec.id,
                    'name': rec.university_name,
                    'city': rec.city,
                    'province': rec.province,
                    'matchScore': round(rec.match_score, 1),
                    'type': uni_type,
                    'fee': fee_display,
                    'reason': rec.recommendation_reason,
                    'pros': rec.pros if isinstance(rec.pros, list) else [],
                    'cons': rec.cons if isinstance(rec.cons, list) else [],
                    'rank': rank_display,
                    'aiAnalysis': rec.ai_analysis or ''
                }
                frontend_recommendations.append(frontend_rec)
            
            return Response(frontend_recommendations, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print("------- BACKEND CRASH LOG -------")
            print(traceback.format_exc()) # This will print the EXACT line and reason in your terminal
            print("---------------------------------")
            return Response({
                'success': False,
                'error': f'Error processing request: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing universities (read-only)
    """
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search universities by name, city, or province
        GET /api/universities/search/?q=search_term
        """
        query = request.query_params.get('q', '')
        if query:
            universities = University.objects.filter(
                models.Q(name__icontains=query) |
                models.Q(city__icontains=query) |
                models.Q(province__icontains=query)
            )
        else:
            universities = University.objects.all()
        
        serializer = self.get_serializer(universities, many=True)
        return Response(serializer.data)


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing recommendations (read-only)
    """
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Optionally filter by user_profile_id
        """
        queryset = Recommendation.objects.all()
        user_profile_id = self.request.query_params.get('user_profile_id', None)
        if user_profile_id:
            queryset = queryset.filter(user_profile_id=user_profile_id)
        return queryset

