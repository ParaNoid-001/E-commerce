
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # URLs for the core application
    path('account/', include('account.urls')),  # URLs for the account application
    path('customer/', include('customer.urls')),  # URLs for the customer application
    path('seller/', include('seller.urls')),  # URLs for the seller application
    path('product/', include('product.urls')),  # URLs for the wishlist application
    path('cart/', include('cart.urls')),  # URLs for the cart application
    
    #path('payment/', include('payment.urls')), #URLs fo the payment
    
    path('wishlist/', include('wishlist.urls')),  # URLs for the wishlist application
    path('Ai/', include('deepseek_llm.urls')),  # URLs for the AI application
    path('api/', include('product.Api.urls')),  # URLs for the API
    
    
    
]

# Serve static and media files through Django during development (only when DEBUG is True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
