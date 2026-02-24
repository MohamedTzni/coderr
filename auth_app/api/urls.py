"""
URL-Konfiguration für die auth_app.
Definiert die Pfade für Registration und Login.
"""

from django.urls import path

from .views import LoginView, RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]