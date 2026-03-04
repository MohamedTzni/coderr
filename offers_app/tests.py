"""
Tests for the offers app.
Tests offer CRUD, pagination, filters, search, and offer details.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile


class OfferTestSetup(APITestCase):
    """
    Base class with shared setup for all offer tests.
    Creates a business user, customer user, and a sample offer.
    """

    def setUp(self):
        """Create test users, profiles, tokens, and a sample offer."""
        self.client = APIClient()
        # Business user
        self.biz_user = User.objects.create_user(
            username='bizuser', email='biz@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.biz_user, type='business', email='biz@mail.de'
        )
        self.biz_token = Token.objects.create(user=self.biz_user)
        # Customer user
        self.cust_user = User.objects.create_user(
            username='custuser', email='cust@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.cust_user, type='customer', email='cust@mail.de'
        )
        self.cust_token = Token.objects.create(user=self.cust_user)
        # Sample offer
        self.offer = Offer.objects.create(
            user=self.biz_user,
            title='Web Design',
            description='Professional web design service.',
        )
        self.detail_basic = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=2,
            delivery_time_in_days=5, price=100,
            features=['Logo'], offer_type='basic',
        )
        self.detail_standard = OfferDetail.objects.create(
            offer=self.offer, title='Standard', revisions=5,
            delivery_time_in_days=7, price=200,
            features=['Logo', 'Banner'], offer_type='standard',
        )
        self.detail_premium = OfferDetail.objects.create(
            offer=self.offer, title='Premium', revisions=10,
            delivery_time_in_days=10, price=500,
            features=['Logo', 'Banner', 'Flyer'], offer_type='premium',
        )
        # Sample offer data for creating new offers
        self.offer_data = {
            'title': 'Grafik Paket',
            'description': 'Design package.',
            'details': [
                {
                    'title': 'Basic', 'revisions': 2,
                    'delivery_time_in_days': 5, 'price': 50,
                    'features': ['Logo'], 'offer_type': 'basic',
                },
                {
                    'title': 'Standard', 'revisions': 5,
                    'delivery_time_in_days': 7, 'price': 150,
                    'features': ['Logo', 'Banner'], 'offer_type': 'standard',
                },
                {
                    'title': 'Premium', 'revisions': 10,
                    'delivery_time_in_days': 10, 'price': 300,
                    'features': ['Logo', 'Banner', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }


class OfferListTest(OfferTestSetup):
    """Tests for GET /api/offers/."""

    def test_list_offers_no_auth(self):
        """Test listing offers without token returns 200 (public)."""
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_list_offers_has_pagination(self):
        """Test that the response has pagination fields."""
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_list_offers_has_min_price(self):
        """Test that each offer in list has min_price field."""
        response = self.client.get('/api/offers/')
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['min_price'], 100)

    def test_list_offers_has_min_delivery_time(self):
        """Test that each offer in list has min_delivery_time field."""
        response = self.client.get('/api/offers/')
        results = response.data['results']
        self.assertEqual(results[0]['min_delivery_time'], 5)

    def test_list_offers_has_user_details(self):
        """Test that each offer in list has user_details field."""
        response = self.client.get('/api/offers/')
        results = response.data['results']
        self.assertIn('user_details', results[0])
        self.assertEqual(results[0]['user_details']['username'], 'bizuser')

    def test_list_offers_search(self):
        """Test searching offers by title."""
        response = self.client.get('/api/offers/?search=Web')
        results = response.data['results']
        self.assertEqual(len(results), 1)

    def test_list_offers_search_no_results(self):
        """Test searching with no matching results."""
        response = self.client.get('/api/offers/?search=Nothing')
        results = response.data['results']
        self.assertEqual(len(results), 0)


class OfferCreateTest(OfferTestSetup):
    """Tests for POST /api/offers/."""

    def test_create_offer_success(self):
        """Test creating an offer as business user returns 201."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        response = self.client.post(
            '/api/offers/', self.offer_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Grafik Paket')

    def test_create_offer_has_three_details(self):
        """Test that created offer has exactly 3 details."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        response = self.client.post(
            '/api/offers/', self.offer_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['details']), 3)

    def test_create_offer_unauthorized(self):
        """Test creating an offer without token returns 401."""
        response = self.client.post(
            '/api/offers/', self.offer_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_as_customer_forbidden(self):
        """Test creating an offer as customer returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.post(
            '/api/offers/', self.offer_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_missing_details(self):
        """Test creating an offer without details returns 400."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        data = {'title': 'No details', 'description': 'Missing.'}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferDetailTest(OfferTestSetup):
    """Tests for GET, PATCH, DELETE /api/offers/{id}/."""

    def test_get_offer_success(self):
        """Test getting a single offer returns 200."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        url = f'/api/offers/{self.offer.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Web Design')

    def test_get_offer_unauthorized(self):
        """Test getting a single offer without token returns 401."""
        url = f'/api/offers/{self.offer.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_not_found(self):
        """Test getting a non-existent offer returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        response = self.client.get('/api/offers/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_offer_success(self):
        """Test updating own offer returns 200."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        url = f'/api/offers/{self.offer.id}/'
        data = {'title': 'Updated Design'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Design')

    def test_patch_offer_not_creator_forbidden(self):
        """Test updating another user's offer returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/offers/{self.offer.id}/'
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_success(self):
        """Test deleting own offer returns 204."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        url = f'/api/offers/{self.offer.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_offer_not_creator_forbidden(self):
        """Test deleting another user's offer returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/offers/{self.offer.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_unauthorized(self):
        """Test deleting an offer without token returns 401."""
        url = f'/api/offers/{self.offer.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfferDetailSingleTest(OfferTestSetup):
    """Tests for GET /api/offerdetails/{id}/."""

    def test_get_offer_detail_success(self):
        """Test getting an offer detail returns 200 with correct data."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        url = f'/api/offerdetails/{self.detail_basic.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Basic')
        self.assertEqual(response.data['offer_type'], 'basic')
        self.assertEqual(float(response.data['price']), 100.0)

    def test_get_offer_detail_unauthorized(self):
        """Test getting an offer detail without token returns 401."""
        url = f'/api/offerdetails/{self.detail_basic.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_detail_not_found(self):
        """Test getting a non-existent offer detail returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        response = self.client.get('/api/offerdetails/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)