from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from account.models import User, Address
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelAdmin(UserAdmin):
    """
    Enhanced admin configuration for the custom User model with additional features.
    """
    model = User
    
    actions = ['activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"
    
    list_display = (
        'id', 
        'email', 
        'name', 
        'profile_picture_preview',
        'is_active', 
        'is_superuser', 
        'is_staff', 
        'user_type',
        'created_at'
    )
    
    list_filter = (
        'is_superuser', 
        'is_staff', 
        'is_active', 
        'is_customer', 
        'is_seller',
        'created_at'
    )
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password'),
            'classes': ('collapse',),
        }),
        ('Personal Info', {
            'fields': (
                'name', 
                'profile_picture',
                'dob',
                'phone_number',
                'gender'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_customer',
                'is_seller',
                'groups',
                'user_permissions'
            ),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'password1',
                'password2',
                'is_active',
                'is_staff'
            ),
        }),
    )
    
    readonly_fields = (
        'last_login',
        'created_at',
        'updated_at',
        'profile_picture_preview'
    )
    
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('-created_at',)
    filter_horizontal = ('groups', 'user_permissions')
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def user_type(self, obj):
        """Display user type in a more readable format"""
        types = []
        if obj.is_customer:
            types.append("Customer")
        if obj.is_seller:
            types.append("Seller")
        if obj.is_superuser:
            types.append("Admin")
        return ", ".join(types) or "None"
    user_type.short_description = 'User Type'
    
    def profile_picture_preview(self, obj):
        """Display a thumbnail preview of the profile picture"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No Image"
    profile_picture_preview.short_description = 'Profile Picture'

class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for the Address model"""
    list_display = (
        'user_email',
        'address_name',
        'city',
        'state',
        'zip_code',
        'country',
        'is_default'
    )
    list_filter = ('country', 'is_default', 'city', 'state')
    search_fields = (
        'user__email',
        'user__name',
        'street_address',
        'city',
        'state',
        'zip_code'
    )
    raw_id_fields = ('user',)
    list_select_related = ('user',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

# Register models with their admin classes
admin.site.register(User, UserModelAdmin)
admin.site.register(Address, AddressAdmin)