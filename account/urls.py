from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView
from .views import (
    register_view, activate_account, login_view,
    password_reset_view, password_reset_confirm_view,
    account_management_view, profile_update_view, password_change_view,
    add_address_view, edit_address, delete_address, delete_account_view,
    admin_registration
    )

# urlpatterns = [
#     path('register/', register_view, name='register'),
#     path('activate/<str:uidb64>/<str:token>/',activate_account, name='activate'),
#     path('login/', login_view, name='login'),
#     path('password_reset/', password_reset_view, name='password_reset'),
#     path('password_reset_confirm/<uidb64>/<token>/',password_reset_confirm_view, name='password_reset_confirm'),
#     path('logout/', LogoutView.as_view(),name='logout'),
#     path('register/admin/', admin_registration, name='admin-register'),
# ]

urlpatterns = [
    # Authentication
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(),name='logout'),
    
    # Password Recovery
    path('password-reset/', password_reset_view, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         password_reset_confirm_view, name='password_reset_confirm'),
    
    # Account Management
    path('account_settings/', account_management_view, name='account_management'),
    path('account_settings/profile/', profile_update_view, name='profile_update'),
    path('account_settings/password/', password_change_view, name='password_change'),
    
    # Address Management
    path('account_settings/address/add/', add_address_view, name='add_address'),
    path('account_settings/address/edit/<int:address_id>/', edit_address, name='edit_address'),
    path('account_settings/address/delete/<int:address_id>/', delete_address, name='delete_address'),
    path('address/set-default/<int:address_id>/', set_default_address, name='set_default_address'),
    
    # Account Deletion
    path('account_settings/delete/', delete_account_view, name='delete_account'),
    #path('account/delete/', delete_account_view, name='delete_account'),
    
    # Admin Registration
    path('admin/register/', admin_registration, name='admin_register'),
]