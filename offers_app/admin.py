"""
Admin configuration for the offers app.
Registers Offer and OfferDetail in the Django admin.
"""

from django.contrib import admin

from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Show OfferDetails inline when editing an Offer in admin."""
    model = OfferDetail
    extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin view for Offer with inline details."""
    list_display = ['title', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin view for OfferDetail."""
    list_display = ['title', 'offer', 'offer_type', 'price', 'delivery_time_in_days']
    list_filter = ['offer_type']