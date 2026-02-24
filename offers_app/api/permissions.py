"""
Permissions for the offers app.
Controls who can create, edit, and delete offers.
"""

from rest_framework.permissions import BasePermission


class IsOfferCreator(BasePermission):
    """
    Only the creator of the offer can edit or delete it.
    Any authenticated user can view offers.
    """

    def has_object_permission(self, request, view, obj):
        """Check if the logged-in user is the creator of this offer."""
        if request.method == 'GET':
            return True
        return obj.user == request.user


class IsBusinessUser(BasePermission):
    """
    Only users with type 'business' can create offers.
    Returns 403 if a customer tries to create an offer.
    """

    def has_permission(self, request, view):
        """Check if the user has a business profile."""
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.type == 'business'