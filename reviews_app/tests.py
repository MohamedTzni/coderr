"""
Tests for the reviews app.
Tests review CRUD, unique constraint, filters, and permissions.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from profiles_app.models import UserProfile
from reviews_app.models import Review


class ReviewTestSetup(APITestCase):
    """
    Base class with shared setup for all review tests.
    Creates a business user and a customer user.
    """

    def setUp(self):
        """Create test users, profiles, and tokens."""
        self.client = APIClient()
        # Business user
        self.biz_user = User.objects.create_user(
            username='bizuser', email='biz@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.biz_user, type='business', email='biz@mail.de'
        )
        self.biz_token = Token.objects.create(user=self.biz_user)
        # Second business user
        self.biz_user2 = User.objects.create_user(
            username='bizuser2', email='biz2@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.biz_user2, type='business', email='biz2@mail.de'
        )
        # Customer user
        self.cust_user = User.objects.create_user(
            username='custuser', email='cust@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.cust_user, type='customer', email='cust@mail.de'
        )
        self.cust_token = Token.objects.create(user=self.cust_user)
        # Second customer user
        self.cust_user2 = User.objects.create_user(
            username='custuser2', email='cust2@mail.de', password='pass123'
        )
        UserProfile.objects.create(
            user=self.cust_user2, type='customer', email='cust2@mail.de'
        )
        self.cust_token2 = Token.objects.create(user=self.cust_user2)
        # Sample review
        self.review = Review.objects.create(
            business_user=self.biz_user,
            reviewer=self.cust_user,
            rating=4,
            description='Great service!',
        )


class ReviewListTest(ReviewTestSetup):
    """Tests for GET /api/reviews/."""

    def test_list_reviews_success(self):
        """Test listing reviews returns 200 with correct data."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rating'], 4)

    def test_list_reviews_unauthorized(self):
        """Test listing reviews without token returns 401."""
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews_filter_business_user(self):
        """Test filtering reviews by business_user_id."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/reviews/?business_user_id={self.biz_user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_reviews_filter_no_results(self):
        """Test filtering with non-matching business_user_id returns empty."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.get('/api/reviews/?business_user_id=999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_reviews_filter_reviewer(self):
        """Test filtering reviews by reviewer_id."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/reviews/?reviewer_id={self.cust_user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_reviews_ordering_rating(self):
        """Test ordering reviews by rating."""
        Review.objects.create(
            business_user=self.biz_user2,
            reviewer=self.cust_user,
            rating=5,
            description='Excellent!',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.get('/api/reviews/?ordering=rating')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['rating'], 4)
        self.assertEqual(response.data[1]['rating'], 5)


class ReviewCreateTest(ReviewTestSetup):
    """Tests for POST /api/reviews/."""

    def test_create_review_success(self):
        """Test creating a review as customer returns 201."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        data = {
            'business_user': self.biz_user2.id,
            'rating': 5,
            'description': 'Excellent work!',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['reviewer'], self.cust_user.id)

    def test_create_review_duplicate_returns_400(self):
        """Test creating a second review for same business returns 400."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        data = {
            'business_user': self.biz_user.id,
            'rating': 5,
            'description': 'Again!',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_as_business_forbidden(self):
        """Test creating a review as business user returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        data = {
            'business_user': self.biz_user2.id,
            'rating': 4,
            'description': 'Nope.',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_unauthorized(self):
        """Test creating a review without token returns 401."""
        data = {
            'business_user': self.biz_user.id,
            'rating': 4,
            'description': 'No token.',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewUpdateTest(ReviewTestSetup):
    """Tests for PATCH /api/reviews/{id}/."""

    def test_update_review_success(self):
        """Test updating own review returns 200."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/reviews/{self.review.id}/'
        data = {'rating': 5, 'description': 'Even better!'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Even better!')

    def test_update_review_not_creator_forbidden(self):
        """Test updating another user's review returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token2.key
        )
        url = f'/api/reviews/{self.review.id}/'
        data = {'rating': 1}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review_unauthorized(self):
        """Test updating a review without token returns 401."""
        url = f'/api/reviews/{self.review.id}/'
        data = {'rating': 1}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_not_found(self):
        """Test updating non-existent review returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        data = {'rating': 5}
        response = self.client.patch('/api/reviews/999/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReviewDeleteTest(ReviewTestSetup):
    """Tests for DELETE /api/reviews/{id}/."""

    def test_delete_review_success(self):
        """Test deleting own review returns 204."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/reviews/{self.review.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_not_creator_forbidden(self):
        """Test deleting another user's review returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token2.key
        )
        url = f'/api/reviews/{self.review.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_unauthorized(self):
        """Test deleting a review without token returns 401."""
        url = f'/api/reviews/{self.review.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_not_found(self):
        """Test deleting non-existent review returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.delete('/api/reviews/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)