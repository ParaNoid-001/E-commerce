from django.urls import path, include
from product.Api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('product/',views.ProductViewSet, basename='product')

urlpatterns = [
    path('',include(router.urls))
]