"""
URL configuration for the profiles app.
Defines the URL paths for profile endpoints.
"""

from django.urls import path

from .views import (
    BusinessProfileListView,
    CustomerProfileListView,
    UserProfileDetailView,
)

urlpatterns = [
    path('profile/<int:user_id>/', UserProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profiles'),
]