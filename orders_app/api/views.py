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
    POST /api/orders/ – Create a new order from an offer_detail_id.
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
    DELETE /api/orders/{id}/ – Delete an order.
    """
    permission_classes = [IsAuthenticated]

    def get_order(self, pk):
        """Get an order by ID or return None."""
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def check_business_permission(self, request):
        """Return 403 response if user is not a business user, else None."""
        permission = IsBusinessUser()
        if not permission.has_permission(request, self):
            return Response(
                {'detail': 'Only business users can update orders.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def patch(self, request, pk):
        """Update the status of an order. Only business users."""
        order = self.get_order(pk)
        if order is None:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        error = self.check_business_permission(request)
        if error:
            return error
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete an order. Only admin/staff users."""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can delete orders.'},
                status=status.HTTP_403_FORBIDDEN,
            )
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
    Count of in_progress orders for a business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the count of in_progress orders."""
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
    Count of completed orders for a business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the count of completed orders."""
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