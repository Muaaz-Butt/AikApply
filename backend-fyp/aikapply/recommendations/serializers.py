from rest_framework import serializers
from .models import UserProfile, University, Recommendation


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    academic_level = serializers.CharField(read_only=True, default='intermediate')
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'name', 'email', 'phone',
            'current_city', 'current_province', 'can_move_to_other_cities', 'preferred_cities',
            'interests', 'preferred_field_of_study', 'academic_level', 'intermediate_percentage',
            'fee_affordability', 'scholarship_required',
            'university_type', 'campus_facilities', 'language_preference',
            'additional_requirements',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'academic_level', 'created_at', 'updated_at']


class UniversitySerializer(serializers.ModelSerializer):
    """Serializer for University model"""
    
    class Meta:
        model = University
        fields = [
            'id', 'name', 'city', 'province', 'university_type',
            'website', 'description', 'fee_range', 'programs_offered',
            'achievements', 'facilities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for Recommendation model"""
    user_profile = UserProfileSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'user_profile', 'university', 'university_name',
            'city', 'province', 'recommendation_reason', 'match_score',
            'achievements', 'fee_information', 'programs_available',
            'ai_analysis', 'pros', 'cons', 'rank', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user profiles with validation - only for Intermediate students"""
    academic_level = serializers.CharField(read_only=True, default='intermediate')
    
    class Meta:
        model = UserProfile
        fields = [
            'name', 'email', 'phone',
            'current_city', 'current_province', 'can_move_to_other_cities', 'preferred_cities',
            'interests', 'preferred_field_of_study', 'academic_level', 'intermediate_percentage',
            'fee_affordability', 'scholarship_required',
            'university_type', 'campus_facilities', 'language_preference',
            'additional_requirements'
        ]
        read_only_fields = ['academic_level']
    
    def validate_interests(self, value):
        """Ensure interests is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Interests must be a list.")
        if len(value) == 0:
            raise serializers.ValidationError("At least one interest is required.")
        return value
    
    def create(self, validated_data):
        """Set academic_level to intermediate for all students"""
        validated_data['academic_level'] = 'intermediate'
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Keep academic_level as intermediate"""
        validated_data['academic_level'] = 'intermediate'
        return super().update(instance, validated_data)
    
    def validate_fee_affordability(self, value):
        """Validate fee affordability"""
        valid_choices = ['low', 'medium', 'high', 'very_high']
        if value not in valid_choices:
            raise serializers.ValidationError(f"Fee affordability must be one of: {', '.join(valid_choices)}")
        return value


class FrontendUserProfileSerializer(serializers.Serializer):
    """Serializer that accepts frontend camelCase field names"""
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    currentCity = serializers.CharField()
    currentProvince = serializers.CharField()
    canMove = serializers.BooleanField(required=False, default=False)
    preferredCities = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    interests = serializers.ListField(child=serializers.CharField())
    preferredField = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    interPercentage = serializers.CharField(required=False, allow_blank=True)
    feeAffordability = serializers.CharField()
    scholarshipRequired = serializers.BooleanField(required=False, default=False)
    uniType = serializers.CharField(required=False, default='Any')
    campusFacilities = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    languagePreference = serializers.CharField(required=False, default='English')
    additionalRequirements = serializers.CharField(required=False, allow_blank=True, default='')
    
    def get_mapped_data(self):
        """Convert validated frontend camelCase data to backend snake_case format"""
        validated_data = self.validated_data
        
        # Map frontend field names to backend field names
        mapped_data = {
            'name': validated_data.get('name'),
            'email': validated_data.get('email'),
            'phone': validated_data.get('phone'),
            'current_city': validated_data.get('currentCity'),
            'current_province': validated_data.get('currentProvince'),
            'can_move_to_other_cities': validated_data.get('canMove', False),
            'preferred_cities': validated_data.get('preferredCities', []),
            'interests': validated_data.get('interests', []),
            'preferred_field_of_study': ', '.join(validated_data.get('preferredField', [])) if validated_data.get('preferredField') else '',
            'intermediate_percentage': float(validated_data.get('interPercentage', 0)) if validated_data.get('interPercentage') and validated_data.get('interPercentage').strip() else None,
            'fee_affordability': self._map_fee_affordability(validated_data.get('feeAffordability', '')),
            'scholarship_required': validated_data.get('scholarshipRequired', False),
            'university_type': self._map_university_type(validated_data.get('uniType', 'Any')),
            'campus_facilities': validated_data.get('campusFacilities', []),
            'language_preference': self._map_language_preference(validated_data.get('languagePreference', 'English')),
            'additional_requirements': validated_data.get('additionalRequirements', '')
        }
        return mapped_data
    
    def _map_fee_affordability(self, value):
        """Map frontend fee affordability to backend values"""
        mapping = {
            'Low (under 50k)': 'low',
            'Medium (50k to 150k)': 'medium',
            'High (150k to 300k)': 'high',
            'Above 300k': 'very_high'
        }
        return mapping.get(value, 'medium')
    
    def _map_university_type(self, value):
        """Map frontend university type to backend values"""
        mapping = {
            'Any': 'both',
            'Public': 'public',
            'Private': 'private'
        }
        return mapping.get(value, 'both')
    
    def _map_language_preference(self, value):
        """Map frontend language preference to backend values"""
        mapping = {
            'English': 'english',
            'Urdu': 'urdu',
            'Both': 'both'
        }
        return mapping.get(value, 'both')


class FrontendRecommendationSerializer(serializers.Serializer):
    """Serializer that returns recommendations in frontend-expected format"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()
    province = serializers.CharField()
    matchScore = serializers.FloatField()
    type = serializers.CharField()
    fee = serializers.CharField()
    reason = serializers.CharField()
    pros = serializers.ListField(child=serializers.CharField())
    cons = serializers.ListField(child=serializers.CharField())
    rank = serializers.CharField()
    aiAnalysis = serializers.CharField()

