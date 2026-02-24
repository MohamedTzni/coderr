"""
Models for the offers app.
Defines Offer and OfferDetail for the marketplace.
"""

from django.contrib.auth.models import User
from django.db import models


class Offer(models.Model):
    """
    A service offer created by a business user.
    Each offer has exactly 3 details (basic, standard, premium).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def __str__(self):
        """Return the offer title and creator username."""
        return f"{self.title} by {self.user.username}"


class OfferDetail(models.Model):
    """
    A detail tier for an offer (basic, standard, or premium).
    Each offer has exactly 3 details with different prices and features.
    """
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='details',
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)

    class Meta:
        ordering = ['id']
        verbose_name = 'Offer Detail'
        verbose_name_plural = 'Offer Details'

    def __str__(self):
        """Return the detail title and offer type."""
        return f"{self.title} ({self.offer_type})"