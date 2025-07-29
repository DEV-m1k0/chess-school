from rest_framework import serializers
from models.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 
            'last_name', 'first_name', 'patronymic',
            'role', 'bio', 'rating', 'hourly_rate'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'last_name': {'required': True},
            'first_name': {'required': True},
        }

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'patronymic']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            patronymic=validated_data.get('patronymic', ''),
            is_active=True,  # Аккаунт активен, но email не подтвержден
            is_email_verified=False
        )
        return user