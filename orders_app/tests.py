"""
Tests for the orders app.
Tests order CRUD, status updates, counts, and permissions.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profiles_app.models import UserProfile


class OrderTestSetup(APITestCase):
    """
    Base class with shared setup for all order tests.
    Creates users, an offer with details, and a sample order.
    """

    def setUp(self):
        """Create test users, offer, and order."""
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
        # Admin user
        self.admin_user = User.objects.create_user(
            username='admin', email='admin@mail.de', password='pass123',
            is_staff=True,
        )
        UserProfile.objects.create(
            user=self.admin_user, type='customer', email='admin@mail.de'
        )
        self.admin_token = Token.objects.create(user=self.admin_user)
        # Offer with details
        self.offer = Offer.objects.create(
            user=self.biz_user,
            title='Web Design',
            description='Professional web design.',
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=2,
            delivery_time_in_days=5, price=100,
            features=['Logo'], offer_type='basic',
        )
        # Sample order
        self.order = Order.objects.create(
            customer_user=self.cust_user,
            business_user=self.biz_user,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo'],
            offer_type='basic',
            status='in_progress',
        )


class OrderListTest(OrderTestSetup):
    """Tests for GET /api/orders/."""

    def test_list_orders_as_customer(self):
        """Test listing orders as customer returns 200 with own orders."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_orders_as_business(self):
        """Test listing orders as business returns 200 with own orders."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_orders_unauthorized(self):
        """Test listing orders without token returns 401."""
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCreateTest(OrderTestSetup):
    """Tests for POST /api/orders/."""

    def test_create_order_success(self):
        """Test creating an order as customer returns 201."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        data = {'offer_detail_id': self.detail.id}
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Basic')
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.data['customer_user'], self.cust_user.id)
        self.assertEqual(response.data['business_user'], self.biz_user.id)

    def test_create_order_as_business_forbidden(self):
        """Test creating an order as business user returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        data = {'offer_detail_id': self.detail.id}
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_unauthorized(self):
        """Test creating an order without token returns 401."""
        data = {'offer_detail_id': self.detail.id}
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_invalid_detail(self):
        """Test creating an order with invalid offer_detail_id returns 400."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        data = {'offer_detail_id': 999}
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_field(self):
        """Test creating an order without offer_detail_id returns 400."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.post('/api/orders/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderUpdateTest(OrderTestSetup):
    """Tests for PATCH /api/orders/{id}/."""

    def test_update_status_success(self):
        """Test updating order status as business returns 200."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        url = f'/api/orders/{self.order.id}/'
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_update_status_as_customer_forbidden(self):
        """Test updating order status as customer returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/orders/{self.order.id}/'
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_status_unauthorized(self):
        """Test updating order status without token returns 401."""
        url = f'/api/orders/{self.order.id}/'
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order_not_found(self):
        """Test updating non-existent order returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        data = {'status': 'completed'}
        response = self.client.patch('/api/orders/999/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDeleteTest(OrderTestSetup):
    """Tests for DELETE /api/orders/{id}/."""

    def test_delete_order_as_admin(self):
        """Test deleting an order as admin returns 204."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        url = f'/api/orders/{self.order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_order_as_business_forbidden(self):
        """Test deleting an order as business returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.biz_token.key
        )
        url = f'/api/orders/{self.order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_as_customer_forbidden(self):
        """Test deleting an order as customer returns 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/orders/{self.order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_unauthorized(self):
        """Test deleting an order without token returns 401."""
        url = f'/api/orders/{self.order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_not_found(self):
        """Test deleting non-existent order returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        response = self.client.delete('/api/orders/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderCountTest(OrderTestSetup):
    """Tests for GET /api/order-count/{business_user_id}/."""

    def test_order_count_success(self):
        """Test order count returns 200 with correct count."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/order-count/{self.biz_user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_order_count_unauthorized(self):
        """Test order count without token returns 401."""
        url = f'/api/order-count/{self.biz_user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_count_user_not_found(self):
        """Test order count for non-existent user returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.get('/api/order-count/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CompletedOrderCountTest(OrderTestSetup):
    """Tests for GET /api/completed-order-count/{business_user_id}/."""

    def test_completed_count_zero(self):
        """Test completed count returns 0 when no completed orders."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/completed-order-count/{self.biz_user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 0)

    def test_completed_count_with_completed_order(self):
        """Test completed count returns correct number."""
        self.order.status = 'completed'
        self.order.save()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        url = f'/api/completed-order-count/{self.biz_user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_completed_count_unauthorized(self):
        """Test completed count without token returns 401."""
        url = f'/api/completed-order-count/{self.biz_user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_count_user_not_found(self):
        """Test completed count for non-existent user returns 404."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.cust_token.key
        )
        response = self.client.get('/api/completed-order-count/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)