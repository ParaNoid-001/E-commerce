# from django.contrib import admin
# from .models import Wishlist

# # Register your models here.

# @admin.register(Wishlist)
# class WishlistAdmin(admin.ModelAdmin):
#     list_display = ('user','product')

from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'product__name')
    autocomplete_fields = ['user', 'product']  # Requires search_fields in User/Product admin
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'product')
    
    actions = ['clear_wishlists']
    
    def clear_wishlists(self, request, queryset):
        queryset.delete()
        self.message_user(request, f"Successfully deleted {queryset.count()} wishlist items")
    clear_wishlists.short_description = "Clear selected wishlists"