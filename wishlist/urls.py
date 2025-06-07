from django.urls import path
from .views import *
from .views import WishlistView, ToggleWishlist, WishlistCountView

app_name = 'wishlist'

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist_view'),
    path('toggle/<int:pk>/', ToggleWishlist.as_view(), name='toggle_wishlist'),
    path('count/', WishlistCountView.as_view(), name='wishlist_count'),
]