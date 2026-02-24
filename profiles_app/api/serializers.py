"""
Serializers for the profiles app.
Transform UserProfile data for the API responses.
"""

from rest_framework import serializers

from profiles_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the profile detail view.
    Used for GET /api/profile/{pk}/ and PATCH /api/profile/{pk}/.
    Returns all profile fields including username and email from the User model.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
        read_only_fields = ['user', 'username', 'type', 'created_at']

    def to_representation(self, instance):
        """
        Make sure that empty fields return "" instead of null.
        The endpoint documentation says: fields must never be null.
        """
        data = super().to_representation(instance)
        text_fields = [
            'first_name', 'last_name', 'location',
            'tel', 'description', 'working_hours',
        ]
        for field in text_fields:
            if data[field] is None:
                data[field] = ''
        return data


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer for the business profiles list.
    Used for GET /api/profiles/business/.
    """
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]

    def to_representation(self, instance):
        """Make sure that empty fields return "" instead of null."""
        data = super().to_representation(instance)
        text_fields = [
            'first_name', 'last_name', 'location',
            'tel', 'description', 'working_hours',
        ]
        for field in text_fields:
            if data[field] is None:
                data[field] = ''
        return data


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer for the customer profiles list.
    Used for GET /api/profiles/customer/.
    """
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'type',
        ]

    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

    def to_representation(self, instance):
        """Make sure that empty fields return "" instead of null."""
        data = super().to_representation(instance)
        for field in ['first_name', 'last_name']:
            if data[field] is None:
                data[field] = ''
        return data