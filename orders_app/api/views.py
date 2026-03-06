"""
Views for the orders app.
Handles order CRUD and order count endpoints.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from .permissions import IsBusinessUser, IsCustomerUser
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)


class OrderListCreateView(APIView):
    """
    GET /api/orders/ – List orders for the logged-in user.
    Returns orders where the user is either customer or business.
    Permission: authenticated users only.
    Status codes: 200 OK, 401 Unauthorized.

    POST /api/orders/ – Create a new order from an offer_detail_id.
    Permission: only customer users.
    Status codes: 201 Created, 400 Bad Request, 401 Unauthorized,
    403 Forbidden, 404 Not Found.
    """

    def get_permissions(self):
        """GET needs auth, POST needs auth + customer type."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get(self, request):
        """Return all orders where the user is customer or business."""
        orders = Order.objects.filter(
            customer_user=request.user
        ) | Order.objects.filter(
            business_user=request.user
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create an order from offer_detail_id."""
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        response_serializer = OrderSerializer(order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    """
    PATCH /api/orders/{id}/ – Update order status.
    Permission: only business users.
    Status codes: 200 OK, 400 Bad Request, 401 Unauthorized,
    403 Forbidden, 404 Not Found.

    DELETE /api/orders/{id}/ – Delete an order.
    Permission: only admin/staff users.
    Status codes: 204 No Content, 401 Unauthorized,
    403 Forbidden, 404 Not Found.
    """

    def get_order(self, pk):
        """Get an order by ID or return None."""
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def patch(self, request, pk):
        """Update the status of an order. Only business users."""
        # Check authentication
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Check business permission
        permission = IsBusinessUser()
        if not permission.has_permission(request, self):
            return Response(
                {'detail': 'Only business users can update orders.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Get order
        order = self.get_order(pk)
        if order is None:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Update status
        serializer = OrderUpdateSerializer(
            order, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = OrderSerializer(order)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """Delete an order. Only admin/staff users."""
        # Check authentication
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Check admin permission
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can delete orders.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Get order
        order = self.get_order(pk)
        if order is None:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCountView(APIView):
    """
    GET /api/order-count/{business_user_id}/ –
    Count of orders with status 'in_progress' for a business user.
    Permission: authenticated users only.
    Status codes: 200 OK, 401 Unauthorized, 404 Not Found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the count of in_progress orders for this business user."""
        if not User.objects.filter(id=business_user_id).exists():
            return Response(
                {'detail': 'Business user not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status='in_progress',
        ).count()
        return Response(
            {'order_count': count},
            status=status.HTTP_200_OK,
        )


class CompletedOrderCountView(APIView):
    """
    GET /api/completed-order-count/{business_user_id}/ –
    Count of orders with status 'completed' for a business user.
    Permission: authenticated users only.
    Status codes: 200 OK, 401 Unauthorized, 404 Not Found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the count of completed orders for this business user."""
        if not User.objects.filter(id=business_user_id).exists():
            return Response(
                {'detail': 'Business user not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status='completed',
        ).count()
        return Response(
            {'completed_order_count': count},
            status=status.HTTP_200_OK,
        )