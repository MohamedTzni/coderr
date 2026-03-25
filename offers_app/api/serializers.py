"""
Serializers for the offers app.
Handles offer list, detail, create, and update with nested OfferDetails.
"""

from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for a single OfferDetail.
    Used for GET /api/offerdetails/{id}/ and nested inside offer responses.
    """

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for the offer list and detail response.
    Shows only id and url for each detail (not the full data).
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Build the URL for this offer detail."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/offerdetails/{obj.id}/')
        return f'/api/offerdetails/{obj.id}/'


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for GET /api/offers/ (list view).
    Includes min_price, min_delivery_time, and user_details.
    """
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details',
        ]

    def get_min_price(self, obj):
        """Return the lowest price from all offer details."""
        details = obj.details.all()
        if details.exists():
            return min(detail.price for detail in details)
        return None

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time from all offer details."""
        details = obj.details.all()
        if details.exists():
            return min(detail.delivery_time_in_days for detail in details)
        return None

    def get_user_details(self, obj):
        """Return basic info about the offer creator."""
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username,
        }


class OfferDetailViewSerializer(serializers.ModelSerializer):
    """
    Serializer for GET /api/offers/{id}/ (single offer detail view).
    Shows details as links, plus min_price and min_delivery_time.
    """
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
        ]

    def get_min_price(self, obj):
        """Return the lowest price from all offer details."""
        details = obj.details.all()
        if details.exists():
            return min(detail.price for detail in details)
        return None

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time from all offer details."""
        details = obj.details.all()
        if details.exists():
            return min(detail.delivery_time_in_days for detail in details)
        return None


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for POST /api/offers/.
    Creates an offer with exactly 3 nested details.
    """
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]

    def validate_details(self, value):
        """Check that exactly 3 details are provided."""
        if len(value) != 3:
            raise serializers.ValidationError(
                "An offer must have exactly 3 details (basic, standard, premium)."
            )
        return value

    def create(self, validated_data):
        """
        Create the offer and all 3 details in one step.
        The user is set from the request (not from the body).
        """
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer


class OfferCreateResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for the POST /api/offers/ response.
    Returns the full offer with all nested detail objects.
    """
    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]


class OfferUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH /api/offers/{id}/.
    Updates the offer and optionally its details.
    Details are matched by offer_type to keep their IDs.
    """
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]

    def update_detail(self, detail, data):
        """Update a single OfferDetail with the given data."""
        detail.title = data.get('title', detail.title)
        detail.revisions = data.get('revisions', detail.revisions)
        detail.delivery_time_in_days = data.get('delivery_time_in_days', detail.delivery_time_in_days)
        detail.price = data.get('price', detail.price)
        detail.features = data.get('features', detail.features)
        detail.save()

    def update_details(self, instance, details_data):
        """Update all provided details matched by offer_type."""
        for detail_data in details_data:
            detail = instance.details.filter(offer_type=detail_data.get('offer_type')).first()
            if detail:
                self.update_detail(detail, detail_data)

    def update(self, instance, validated_data):
        """Update the offer fields and optionally its details."""
        details_data = validated_data.pop('details', None)
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        if details_data is not None:
            self.update_details(instance, details_data)
        return instance


class OfferDetailSingleSerializer(serializers.ModelSerializer):
    """
    Serializer for GET /api/offerdetails/{id}/.
    Returns the full data of a single offer detail.
    """

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]