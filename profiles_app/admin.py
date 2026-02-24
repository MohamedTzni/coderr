"""
Admin-Konfiguration für die profiles_app.
Registriert das UserProfile im Django-Admin.
"""

from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin-Ansicht für UserProfile."""
    list_display = ['user', 'type', 'location', 'created_at']
    list_filter = ['type']
    search_fields = ['user__username', 'first_name', 'last_name']