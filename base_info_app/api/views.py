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

    def get(self, request):
        """
        Return aggregated platform statistics.
        average_rating is rounded to one decimal place.
        """
        review_count = Review.objects.count()
        average_rating_result = Review.objects.aggregate(
            avg_rating=Avg('rating')
        )
        average_rating = average_rating_result['avg_rating']
        if average_rating is not None:
            average_rating = round(average_rating, 1)
        else:
            average_rating = 0.0
        business_profile_count = UserProfile.objects.filter(
            type='business'
        ).count()
        offer_count = Offer.objects.count()
        return Response(
            {
                'review_count': review_count,
                'average_rating': average_rating,
                'business_profile_count': business_profile_count,
                'offer_count': offer_count,
            },
            status=status.HTTP_200_OK,
        )