"""
Permissions for the reviews app.
Controls who can create, edit, and delete reviews.
"""

from rest_framework.permissions import BasePermission


class IsReviewCreator(BasePermission):
    """
    Only the creator of the review can edit or delete it.
    Endpoint doc: 403 Forbidden if user is not the creator.
    """

    def has_object_permission(self, request, view, obj):
        """Check if the logged-in user created this review."""
        return obj.reviewer == request.user


class IsCustomerUser(BasePermission):
    """
    Only users with type 'customer' can create reviews.
    Endpoint doc: 401 Unauthorized if not customer profile.
    """

    def has_permission(self, request, view):
        """Check if the user has a customer profile."""
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.type == 'customer'