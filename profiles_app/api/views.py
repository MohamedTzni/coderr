"""
Views for the profiles app.
Handles profile detail, update, and list endpoints.
"""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profiles_app.models import UserProfile
from .permissions import IsProfileOwner
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    UserProfileSerializer,
)


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/profile/{pk}/ – Get profile details.
    PATCH /api/profile/{pk}/ – Update own profile.
    Only the profile owner can edit. Any authenticated user can view.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]
    lookup_field = 'pk'


class BusinessProfileListView(generics.ListAPIView):
    """
    GET /api/profiles/business/ – List all business profiles.
    Only authenticated users can access this endpoint.
    """
    queryset = UserProfile.objects.filter(type='business')
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    """
    GET /api/profiles/customer/ – List all customer profiles.
    Only authenticated users can access this endpoint.
    """
    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]