"""
Tests for the base_info app.
Tests the platform statistics endpoint.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from offers_app.models import Offer
from profiles_app.models import UserProfile
from reviews_app.models import Review


class BaseInfoTest(APITestCase):
    """Tests for GET /api/base-info/."""

    def setUp(self):
        """Create test data for platform statistics."""
        self.client = APIClient()
        # Business user
        self.biz_user = User.objects.create_user(
            username='bizuser', email='biz@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.biz_user, type='business', email='biz@mail.de'
        )
        # Customer user
        self.cust_user = User.objects.create_user(
            username='custuser', email='cust@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.cust_user, type='customer', email='cust@mail.de'
        )
        # Offer
        Offer.objects.create(
            user=self.biz_user, title='Offer 1', description='Test offer.'
        )
        # Review
        Review.objects.create(
            business_user=self.biz_user,
            reviewer=self.cust_user,
            rating=4,
            description='Good!',
        )

    def test_base_info_no_auth_required(self):
        """Test base-info is public, no token needed, returns 200."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_has_all_fields(self):
        """Test response contains all required fields."""
        response = self.client.get('/api/base-info/')
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)

    def test_base_info_correct_values(self):
        """Test response contains correct values."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['review_count'], 1)
        self.assertEqual(response.data['average_rating'], 4.0)
        self.assertEqual(response.data['business_profile_count'], 1)
        self.assertEqual(response.data['offer_count'], 1)

    def test_base_info_average_rating_rounded(self):
        """Test average_rating is rounded to one decimal."""
        # Add a second review with rating 5
        biz_user2 = User.objects.create_user(
            username='biz2', email='biz2@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=biz_user2, type='business', email='biz2@mail.de'
        )
        Review.objects.create(
            business_user=biz_user2,
            reviewer=self.cust_user,
            rating=5,
            description='Excellent!',
        )
        response = self.client.get('/api/base-info/')
        # Average of 4 and 5 = 4.5
        self.assertEqual(response.data['average_rating'], 4.5)

    def test_base_info_no_reviews(self):
        """Test average_rating is 0.0 when no reviews exist."""
        Review.objects.all().delete()
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0.0)