from django.urls import path
from seller.views import seller_dashboard_view,change_password_view

urlpatterns = [
    path('dashboard/', seller_dashboard_view, name='seller_dashboard'),
    path('change-password/', change_password_view, name='s_change_password'),
]
