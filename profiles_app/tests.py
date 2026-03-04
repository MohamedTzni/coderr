"""
Tests for the profiles app.
Tests profile detail, update, and list endpoints.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from profiles_app.models import UserProfile


class ProfileDetailTest(APITestCase):
    """Tests for GET /api/profile/{pk}/ and PATCH /api/profile/{pk}/."""

    def setUp(self):
        """Create test users with profiles and tokens."""
        self.client = APIClient()
        # Create first user with profile
        self.user1 = User.objects.create_user(
            username='user1', email='user1@mail.de', password='pass123'
        )
        self.profile1 = UserProfile.objects.create(
            user=self.user1, type='business', email='user1@mail.de'
        )
        self.token1 = Token.objects.create(user=self.user1)
        # Create second user with profile
        self.user2 = User.objects.create_user(
            username='user2', email='user2@mail.de', password='pass123'
        )
        self.profile2 = UserProfile.objects.create(
            user=self.user2, type='customer', email='user2@mail.de'
        )
        self.token2 = Token.objects.create(user=self.user2)

    def test_get_profile_success(self):
        """Test getting a profile returns 200 with correct data."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = f'/api/profile/{self.user1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
        self.assertEqual(response.data['type'], 'business')

    def test_get_profile_empty_fields_not_null(self):
        """Test that empty text fields return '' and not null."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = f'/api/profile/{self.user1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')

    def test_get_profile_unauthorized(self):
        """Test getting a profile without token returns 401."""
        url = f'/api/profile/{self.user1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):
        """Test getting a non-existent profile returns 404."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = '/api/profile/999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_profile_success(self):
        """Test updating own profile returns 200."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = f'/api/profile/{self.user1.id}/'
        data = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'location': 'Berlin',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')
        self.assertEqual(response.data['last_name'], 'Mustermann')
        self.assertEqual(response.data['location'], 'Berlin')

    def test_patch_other_profile_forbidden(self):
        """Test updating another user's profile returns 403."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        url = f'/api/profile/{self.user1.id}/'
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_unauthorized(self):
        """Test updating a profile without token returns 401."""
        url = f'/api/profile/{self.user1.id}/'
        data = {'first_name': 'NoToken'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BusinessProfileListTest(APITestCase):
    """Tests for GET /api/profiles/business/."""

    def setUp(self):
        """Create business and customer users."""
        self.client = APIClient()
        self.user_biz = User.objects.create_user(
            username='biz', email='biz@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.user_biz, type='business', email='biz@mail.de'
        )
        self.token = Token.objects.create(user=self.user_biz)
        self.user_cust = User.objects.create_user(
            username='cust', email='cust@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.user_cust, type='customer', email='cust@mail.de'
        )

    def test_business_list_success(self):
        """Test listing business profiles returns 200 with only business users."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')

    def test_business_list_unauthorized(self):
        """Test listing business profiles without token returns 401."""
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerProfileListTest(APITestCase):
    """Tests for GET /api/profiles/customer/."""

    def setUp(self):
        """Create business and customer users."""
        self.client = APIClient()
        self.user_biz = User.objects.create_user(
            username='biz', email='biz@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.user_biz, type='business', email='biz@mail.de'
        )
        self.token = Token.objects.create(user=self.user_biz)
        self.user_cust = User.objects.create_user(
            username='cust', email='cust@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.user_cust, type='customer', email='cust@mail.de'
        )

    def test_customer_list_success(self):
        """Test listing customer profiles returns 200 with only customers."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')

    def test_customer_list_unauthorized(self):
        """Test listing customer profiles without token returns 401."""
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)