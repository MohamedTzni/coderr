"""
Serializers for authentication.
Handles validation for registration and login data.
"""

from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    Validates that all required fields are present and correct.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=['customer', 'business'])

    def validate_username(self, value):
        """Check if the username is already taken."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        """Check if the email is already taken."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate(self, data):
        """Check if both passwords match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"repeated_password": "The passwords do not match."}
            )
        return data

    def create(self, validated_data):
        """Create a new user with the validated data."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Expects username and password.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)