"""
Serializers for the orders app.
Handles order creation from offer_detail_id and status updates.
"""

from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for GET /api/orders/ and response after create/update.
    Returns all order fields.
    Endpoint doc success response: id, customer_user, business_user, title,
    revisions, delivery_time_in_days, price, features, offer_type, status,
    created_at, updated_at.
    """

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for POST /api/orders/.
    Only expects offer_detail_id. Everything else is filled automatically.
    Endpoint doc request body: {"offer_detail_id": 1}
    """
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        """Check if the OfferDetail exists. Returns 404 if not found."""
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "The offer detail was not found."
            )
        return value

    def create(self, validated_data):
        """
        Create an order from the OfferDetail data.
        The customer is the logged-in user.
        The business user is the offer creator.
        All other fields come from the OfferDetail.
        """
        offer_detail = OfferDetail.objects.get(
            id=validated_data['offer_detail_id']
        )
        customer = self.context['request'].user
        business = offer_detail.offer.user
        order = Order.objects.create(
            customer_user=customer,
            business_user=business,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress',
        )
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH /api/orders/{id}/.
    Only the status field can be updated.
    Endpoint doc request body: {"status": "completed"}
    Possible values: 'in_progress', 'completed', 'cancelled'.
    """

    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        """Check if the status value is valid."""
        allowed = ['in_progress', 'completed', 'cancelled']
        if value not in allowed:
            raise serializers.ValidationError(
                f"Invalid status. Allowed values: {allowed}"
            )
        return value