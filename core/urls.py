from django.urls import path
from core.views import home , about, contact_view
from core.view_imports import *

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact_view, name='contact_view'),
]
