from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model() 

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'password','portal_email',
    'portal_password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            phone=validated_data.get('phone', ''),
            portal_email = validated_data.get('portal_email', ''),
            portal_password = validated_data.get('portal_password', ''),
        )
        return user
