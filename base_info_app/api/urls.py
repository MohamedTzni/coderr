"""
URL configuration for the base_info app.
Defines the path for the platform statistics endpoint.
"""

from django.urls import path

from .views import BaseInfoView

urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]