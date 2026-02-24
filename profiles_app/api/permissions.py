"""
Permissions for the profiles app.
Controls who can view and edit profiles.
"""

from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """
    Only the owner of the profile can edit it.
    Everyone who is authenticated can view profiles.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the logged-in user is the owner of this profile.
        GET requests are allowed for everyone.
        PATCH requests are only allowed for the owner.
        """
        if request.method == 'GET':
            return True
        return obj.user == request.user