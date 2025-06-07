from django.contrib import admin
from .models import Cart, CartItem
from django.contrib.admin import display

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'total_price']
    
    def total_price(self, obj):
        return f"₹ {obj.total_price}"
    total_price.short_description = 'Total Price'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    @display(description="Created At")
    def formatted_created_at(self, obj):
        return obj.created_at.strftime("%d %b %Y %H:%M")
    
    list_display = ['user', 'formatted_created_at', 'created_at', 'updated_at', 'total_items', 'total_price']
    list_filter = ['created_at', 'updated_at']
    list_select_related = ['user'] 
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    inlines = [CartItemInline]
    list_display_links = ['user']
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Items'
    
    def total_price(self, obj):
        return f"₹ {obj.total_price}"
    total_price.short_description = 'Total Price'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['product__name', 'cart__user__username']
    readonly_fields = ['total_price']
    raw_id_fields = ['product']
    
    def total_price(self, obj):
        return f"₹ {obj.total_price}"
    total_price.short_description = 'Total Price'