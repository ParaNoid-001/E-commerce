from django.urls import path
from .views import *
from .views import (ProductListView, create_product, update_product, delete_product,add_category,detail_product,
                    PaymentView,PaymentCallbackView,PaymentSuccessView,PaymentFailedView,OrderHistoryView)



urlpatterns = [
    path('list/', ProductListView.as_view(), name='product_list'),
    path('create/', create_product, name='product_create'),
    path('edit/<int:pk>/', update_product, name='product_edit'),
    path('delete/<int:pk>/', delete_product, name='product_delete'),
    path('add-category/', add_category, name='add_category'),
    path('detail/<int:pk>/', detail_product, name='product_detail'),
    
    path('payment/<int:product_id>/', PaymentView.as_view(), name='payment'),
    path('payment-callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    path("payment-success/<str:order_id>/", PaymentSuccessView.as_view(), name='payment_success'),
    path('payment-failed/<str:order_id>/', PaymentFailedView.as_view(), name='payment_failed'),
    path('order-history/', OrderHistoryView.as_view(), name='order_history'),
    path('order/receipt/<int:order_id>/', GenerateOrderReceiptPDF.as_view(), name='order-receipt'),
   
    
]
