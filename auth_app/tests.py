"""
Tests for the auth app.
Tests registration and login endpoints.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class RegistrationTest(APITestCase):
    """Tests for POST /api/registration/."""

    def setUp(self):
        """Set up test client. Runs before every test method."""
        self.client = APIClient()
        self.url = '/api/registration/'

    def test_registration_success(self):
        """Test successful registration returns 201 and token."""
        data = {
            'username': 'testuser',
            'email': 'test@mail.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@mail.de')

    def test_registration_business_user(self):
        """Test registration with type business."""
        data = {
            'username': 'bizuser',
            'email': 'biz@mail.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'business',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_registration_creates_profile(self):
        """Test that registration also creates a UserProfile."""
        data = {
            'username': 'profiletest',
            'email': 'profile@mail.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='profiletest')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.type, 'customer')

    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords returns 400."""
        data = {
            'username': 'testuser',
            'email': 'test@mail.de',
            'password': 'testpass123',
            'repeated_password': 'wrongpass',
            'type': 'customer',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_username(self):
        """Test registration with existing username returns 400."""
        User.objects.create_user(
            username='existing', email='old@mail.de', password='pass123'
        )
        data = {
            'username': 'existing',
            'email': 'new@mail.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        """Test registration with existing email returns 400."""
        User.objects.create_user(
            username='olduser', email='same@mail.de', password='pass123'
        )
        data = {
            'username': 'newuser',
            'email': 'same@mail.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_fields(self):
        """Test registration with missing fields returns 400."""
        data = {
            'username': 'testuser',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(APITestCase):
    """Tests for POST /api/login/."""

    def setUp(self):
        """Create a test user for login tests."""
        self.client = APIClient()
        self.url = '/api/login/'
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@mail.de',
            password='testpass123',
        )

    def test_login_success(self):
        """Test successful login returns 200 and token."""
        data = {
            'username': 'loginuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'loginuser')
        self.assertEqual(response.data['email'], 'login@mail.de')

    def test_login_wrong_password(self):
        """Test login with wrong password returns 400."""
        data = {
            'username': 'loginuser',
            'password': 'wrongpass',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user returns 400."""
        data = {
            'username': 'nouser',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Test login with missing fields returns 400."""
        data = {
            'username': 'loginuser',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)