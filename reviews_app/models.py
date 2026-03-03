"""
Models for the reviews app.
A customer can leave one review per business user.
"""

from django.contrib.auth.models import User
from django.db import models


class Review(models.Model):
    """
    A review from a customer for a business user.
    Each customer can only leave one review per business user.
    """
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews',
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews',
    )
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['business_user', 'reviewer']

    def __str__(self):
        """Return reviewer, business user, and rating."""
        return f"Review by {self.reviewer.username} for {self.business_user.username} ({self.rating}/5)"