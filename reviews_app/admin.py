"""
Admin configuration for the reviews app.
Registers Review in the Django admin.
"""

from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin view for Review."""
    list_display = [
        'reviewer', 'business_user', 'rating',
        'created_at', 'updated_at',
    ]
    list_filter = ['rating', 'created_at']
    search_fields = [
        'reviewer__username',
        'business_user__username',
        'description',
    ]