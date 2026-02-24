"""
Pagination for the offers app.
Controls how many offers are returned per page.
"""

from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """
    Pagination for the offers list.
    The page_size can be set via the 'page_size' query parameter.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50