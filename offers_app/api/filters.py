"""
Filters for the offers app.
Allows filtering offers by creator, price, and delivery time.
"""

import django_filters
from django.db.models import Min

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """
    Filter for the offers list.
    Supports filtering by creator_id, min_price, and max_delivery_time.
    """
    creator_id = django_filters.NumberFilter(field_name='user_id')
    min_price = django_filters.NumberFilter(
        method='filter_min_price',
    )
    max_delivery_time = django_filters.NumberFilter(
        method='filter_max_delivery_time',
    )

    class Meta:
        model = Offer
        fields = ['creator_id']

    def filter_min_price(self, queryset, name, value):
        """Filter offers whose cheapest detail has price >= value."""
        return queryset.filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """Filter offers with delivery time <= value."""
        return queryset.filter(
            details__delivery_time_in_days__lte=value
        ).distinct()