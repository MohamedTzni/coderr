"""
Views for the base_info app.
Returns aggregated platform statistics.
"""

from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profiles_app.models import UserProfile
from reviews_app.models import Review


class BaseInfoView(APIView):
    """
    GET /api/base-info/ – Platform statistics.
    Returns review count, average rating, business profile count, and offer count.
    Permission: no authentication required (public).
    Status codes: 200 OK.
    """
    permission_classes = [AllowAny]

    def get_average_rating(self):
        """Return average rating rounded to 1 decimal, or 0.0 if no reviews."""
        result = Review.objects.aggregate(avg_rating=Avg('rating'))
        avg = result['avg_rating']
        return round(avg, 1) if avg is not None else 0.0

    def get(self, request):
        """Return aggregated platform statistics."""
        return Response(
            {
                'review_count': Review.objects.count(),
                'average_rating': self.get_average_rating(),
                'business_profile_count': UserProfile.objects.filter(type='business').count(),
                'offer_count': Offer.objects.count(),
            },
            status=status.HTTP_200_OK,
        )