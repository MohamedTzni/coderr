"""
Permissions for the orders app.
Controls who can create, update, and delete orders.
"""

from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Only users with type 'customer' can create orders.
    Endpoint doc: 403 if user is not type 'customer'.
    """

    def has_permission(self, request, view):
        """Check if the user has a customer profile."""
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.type == 'customer'


class IsBusinessUser(BasePermission):
    """
    Only users with type 'business' can update order status.
    Endpoint doc: 403 if user is not authorized.
    """

    def has_permission(self, request, view):
        """Check if the user has a business profile."""
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.type == 'business'