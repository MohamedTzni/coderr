"""
URL configuration for the auth app.
Defines the paths for registration and login.
"""

from django.urls import path

from .views import LoginView, RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]