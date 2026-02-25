"""
Models for the orders app.
An order is created when a customer buys an offer detail.
"""

from django.contrib.auth.models import User
from django.db import models


class Order(models.Model):
    """
    A customer order based on an OfferDetail.
    All fields except status are set automatically when the order is created.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_orders',
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='business_orders',
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        """Return the order title and status."""
        return f"{self.title} ({self.status})"