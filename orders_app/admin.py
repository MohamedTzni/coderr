"""
Admin configuration for the orders app.
Registers Order in the Django admin.
"""

from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin view for Order."""
    list_display = [
        'title', 'customer_user', 'business_user',
        'status', 'price', 'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['title']