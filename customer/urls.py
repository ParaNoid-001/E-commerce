from django.urls import path
from customer.views import customer_dashboard_view,change_password_view

urlpatterns = [
    path('dashboard/', customer_dashboard_view, name='customer_dashboard'),
    path('change-password/', change_password_view, name='change_password'),
]