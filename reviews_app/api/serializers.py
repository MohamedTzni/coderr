"""
Serializers for the reviews app.
Handles review creation, listing, and updates.
"""

from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for GET /api/reviews/ and response after create/update.
    Endpoint doc success response: id, business_user, reviewer, rating,
    description, created_at, updated_at.
    """

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['reviewer', 'created_at', 'updated_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for POST /api/reviews/.
    Endpoint doc request body: {business_user, rating, description}.
    The reviewer is set automatically from the logged-in user.
    """

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Check that the customer has not already reviewed this business user.
        Endpoint doc: 400 if already reviewed, 403 if not customer.
        """
        reviewer = self.context['request'].user
        business_user = data['business_user']
        if Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user,
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        return data

    def create(self, validated_data):
        """Create a review with the logged-in user as reviewer."""
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH /api/reviews/{id}/.
    Only 'rating' and 'description' are editable.
    Endpoint doc request body: {rating, description}.
    """

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'business_user', 'reviewer',
            'created_at', 'updated_at',
        ]