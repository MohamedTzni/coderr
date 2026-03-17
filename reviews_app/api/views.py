"""
Views for the reviews app.
Handles review CRUD with filtering and ordering.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews_app.models import Review
from .permissions import IsCustomerUser, IsReviewCreator
from .serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
    ReviewUpdateSerializer,
)


class ReviewListCreateView(APIView):
    """
    GET /api/reviews/ – List all reviews.
    Supports query parameters: business_user_id, reviewer_id, ordering.
    Ordering values: 'updated_at', 'rating', '-updated_at', '-rating'.
    Permission: authenticated users only.
    Status codes: 200 OK, 401 Unauthorized.

    POST /api/reviews/ – Create a new review.
    Only customer users can create reviews.
    One review per customer per business user.
    Permission: authenticated customer users only.
    Status codes: 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden.
    """

    def get_permissions(self):
        """GET needs auth, POST needs auth + customer type."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def apply_filters(self, reviews, params):
        """Filter reviews by business_user_id and reviewer_id if provided."""
        if params.get('business_user_id'):
            reviews = reviews.filter(business_user_id=params['business_user_id'])
        if params.get('reviewer_id'):
            reviews = reviews.filter(reviewer_id=params['reviewer_id'])
        ordering = params.get('ordering')
        if ordering in ['updated_at', '-updated_at', 'rating', '-rating']:
            reviews = reviews.order_by(ordering)
        return reviews

    def get(self, request):
        """Return all reviews with optional filtering and ordering."""
        reviews = self.apply_filters(Review.objects.all(), request.query_params)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new review. Reviewer is set to the logged-in user."""
        serializer = ReviewCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewDetailView(APIView):
    """
    PATCH /api/reviews/{id}/ – Update a review (rating and description only).
    Permission: only the review creator.
    Status codes: 200 OK, 400 Bad Request, 401 Unauthorized,
    403 Forbidden, 404 Not Found.

    DELETE /api/reviews/{id}/ – Delete a review.
    Permission: only the review creator.
    Status codes: 204 No Content, 401 Unauthorized,
    403 Forbidden, 404 Not Found.
    """
    permission_classes = [IsAuthenticated]

    def get_review(self, pk):
        """Get a review by ID or return None."""
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return None

    def get_review_or_error(self, pk):
        """Return (review, None) or (None, 404 response)."""
        review = self.get_review(pk)
        if review is None:
            return None, Response(
                {'detail': 'Review not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return review, None

    def check_creator_permission(self, request, review, action):
        """Return 403 response if user is not the review creator, else None."""
        permission = IsReviewCreator()
        if not permission.has_object_permission(request, self, review):
            return Response(
                {'detail': f'You can only {action} your own reviews.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def patch(self, request, pk):
        """Update rating and description of a review."""
        review, error = self.get_review_or_error(pk)
        if error:
            return error
        error = self.check_creator_permission(request, review, 'edit')
        if error:
            return error
        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete a review."""
        review, error = self.get_review_or_error(pk)
        if error:
            return error
        error = self.check_creator_permission(request, review, 'delete')
        if error:
            return error
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)