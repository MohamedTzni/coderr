"""
Serializers für die Authentifizierung.
Wandeln JSON-Daten in Python-Objekte um und validieren die Eingaben.
"""

from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer für die Benutzerregistrierung.
    Prüft ob alle Felder vorhanden und gültig sind.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=['customer', 'business'])

    def validate_username(self, value):
        """Prüft ob der Username schon vergeben ist."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Dieser Username ist bereits vergeben.")
        return value

    def validate_email(self, value):
        """Prüft ob die E-Mail schon vergeben ist."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese E-Mail ist bereits vergeben.")
        return value

    def validate(self, data):
        """Prüft ob die beiden Passwörter übereinstimmen."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"repeated_password": "Die Passwörter stimmen nicht überein."}
            )
        return data

    def create(self, validated_data):
        """Erstellt einen neuen User mit den validierten Daten."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer für den Login.
    Erwartet username und password.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)