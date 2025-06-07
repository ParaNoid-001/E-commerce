from django.urls import path
from .views import *
from . import views
from .views import cart_summary, cart_add, cart_delete, cart_update
from .views import GenerateOrderReceiptPDF,CreateCartOrderView, PaymentCallbackView, OrderSuccessView

app_name = 'cart'

urlpatterns = [
    path('', cart_summary, name='cart_summary'),
    path('add/', cart_add, name='cart_add'),
    path('delete/', cart_delete, name='cart_delete'),
    path('update/', cart_update, name='cart_update'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('create_cart_order/', CreateCartOrderView.as_view(), name='create_cart_order'),
    #path('checkout/<int:pk>/', checkoutView.as_view(), name='checkout'),

    path('payment-callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    path('order-success/', OrderSuccessView.as_view(), name='order_success'),
    path('order/receipt/<int:order_id>/', views.GenerateOrderReceiptPDF.as_view(), name='order-receipt'),
]