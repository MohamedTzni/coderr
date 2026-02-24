"""
Models für die profiles_app.
Definiert das UserProfile mit allen Feldern laut Endpoint-Dokumentation.
"""

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Benutzerprofil – wird bei der Registration automatisch erstellt.
    Erweitert den Django-User um zusätzliche Felder.
    """
    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    file = models.FileField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        """Gibt den Username und den Typ zurück."""
        return f"{self.user.username} ({self.type})"