"""
URL configuration for the offers app.
Defines the paths for offer and offer detail endpoints.
"""

from django.urls import path

from .views import OfferDetailSingleView, OfferDetailView, OfferListCreateView

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path(
        'offerdetails/<int:pk>/',
        OfferDetailSingleView.as_view(),
        name='offerdetail-single',
    ),
]