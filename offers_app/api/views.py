"""
Views for the offers app.
Handles all offer CRUD endpoints and offer detail retrieval.
"""

from rest_framework import generics, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from offers_app.models import Offer, OfferDetail
from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferCreator
from .serializers import (
    OfferCreateResponseSerializer,
    OfferCreateSerializer,
    OfferDetailSingleSerializer,
    OfferDetailViewSerializer,
    OfferListSerializer,
    OfferUpdateSerializer,
)


class OfferListCreateView(generics.ListCreateAPIView):
    """
    GET /api/offers/ – List all offers (public, paginated, filterable).
    POST /api/offers/ – Create a new offer (business users only).
    """
    queryset = Offer.objects.all()
    pagination_class = OfferPagination
    filterset_class = OfferFilter
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_permissions(self):
        """
        GET requests are public (no auth needed).
        POST requests require authentication and business profile.
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]

    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        """Set the offer creator to the logged-in user."""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create an offer and return the detail view response.
        The response shows the offer with detail links (not the raw input).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        offer = serializer.instance
        response_serializer = OfferCreateResponseSerializer(
            offer, context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/offers/{id}/ – Get a single offer.
    PATCH /api/offers/{id}/ – Update an offer (creator only).
    DELETE /api/offers/{id}/ – Delete an offer (creator only).
    """
    queryset = Offer.objects.all()

    def get_permissions(self):
        """
        GET requests need authentication.
        PATCH/DELETE requests need authentication + creator check.
        """
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOfferCreator()]

    def get_serializer_class(self):
        """Use different serializers for get, update."""
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return OfferDetailViewSerializer

    def update(self, request, *args, **kwargs):
        """
        Update an offer and return the detail view response.
        Uses partial=True because PATCH only sends changed fields.
        """
        instance = self.get_object()
        serializer = OfferUpdateSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = OfferDetailViewSerializer(
            instance, context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class OfferDetailSingleView(generics.RetrieveAPIView):
    """
    GET /api/offerdetails/{id}/ – Get a single offer detail.
    Returns the full data of one detail (basic, standard, or premium).
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSingleSerializer
    permission_classes = [IsAuthenticated]