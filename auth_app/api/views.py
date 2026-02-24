"""
Views für die Authentifizierung.
Enthält die Logik für Registration und Login.
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
    Endpoint für die Benutzerregistrierung.
    Erstellt einen neuen User mit Profil und gibt ein Token zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Erstellt einen neuen Benutzer und gibt Token + User-Daten zurück."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        UserProfile.objects.create(
            user=user,
            type=serializer.validated_data['type'],
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
    Endpoint für den Login.
    Authentifiziert den User und gibt ein Token zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Authentifiziert einen Benutzer und gibt Token + User-Daten zurück."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'detail': 'Ungültige Anmeldedaten.'},
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