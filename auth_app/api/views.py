"""
Views for authentication.
Contains the logic for registration and login.
"""

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles_app.models import UserProfile
from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """
    POST /api/registration/ – Register a new user.
    Creates a new user with a profile and returns a token.
    No authentication required.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Create a new user, profile, and token."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        UserProfile.objects.create(
            user=user,
            type=serializer.validated_data['type'],
            email=user.email,
        )
        return Response(
            {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/login/ – Log in a user.
    Authenticates the user and returns a token.
    No authentication required.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and return token + user data."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            },
            status=status.HTTP_200_OK,
        )