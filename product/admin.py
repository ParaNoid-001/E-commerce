from django.contrib import admin
from product.models import Product, Category, Order, OrderItem
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib import admin
from product.models import Product,Category, Order

admin.site.site_header = "E-Commerce Administration"
admin.site.site_title = "E-Commerce Admin Portal"
admin.site.index_title = "Store Management"
# Registerd models 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'display_categories', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('categories', 'is_active', 'created_at')
    filter_horizontal = ('categories',)  # Better UI for many-to-many selection
    list_editable = ('price', 'is_active')  # Allow quick editing
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categories'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_link", "product_display", "amount", "status", "is_paid", "created_at")
    search_fields = ("user__username", "user__email", "product_name", "razorpay_order_id", "razorpay_payment_id")
    list_filter = ("is_paid", "status", "created_at", "email_sent")
    readonly_fields = ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature", "created_at")
    list_select_related = ("user", "product")  # Optimize queries
    actions = ["resend_confirmation_email", "mark_as_paid", "mark_as_shipped"]
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'product', 'status', 'is_paid')
        }),
        ('Payment Details', {
            'fields': ('amount', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse("admin:account_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user'
    
    def product_display(self, obj):
        if obj.product:
            url = reverse("admin:product_product_change", args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return obj.product_name or "No product"
    product_display.short_description = 'Product'
    
    def product_link(self, obj):
        if obj.product:
            url = reverse("admin:product_product_change", args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return obj.product_name
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product'
    
    def resend_confirmation_email(self, request, queryset):
        for order in queryset:
            try:
                order.send_confirmation_email()
                self.message_user(request, f"Confirmation email resent for order {order.id}")
            except Exception as e:
                self.message_user(request, f"Failed to resend email for order {order.id}: {str(e)}", level='error')
    resend_confirmation_email.short_description = "Resend confirmation email"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'product_link', 'quantity', 'price', 'subtotal')
    search_fields = ('order__razorpay_order_id', 'product__name')
    list_filter = ('product__categories',)
    list_select_related = ('order', 'product')
    
    
    def order_link(self, obj):
        url = reverse("admin:product_order_change", args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order'
    
    def product_link(self, obj):
        url = reverse("admin:product_product_change", args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product'
    
    def subtotal(self, obj):
        return obj.quantity * obj.price
    subtotal.short_description = 'Subtotal'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    
    def product_count(self, obj):
        count = obj.products.count()
        url = (
            reverse("admin:product_product_changelist")
            + "?"
            + urlencode({"categories__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, count)
    product_count.short_description = 'Products'
    
    
    
# from django.contrib import admin
# from product.models import Product,Category, Order

# # Register your models here.
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('id','name','price')
#     search_fields = ('name',)
#     list_filter = ('categories',)   
    
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("id","user","amount","is_paid","created_at")
#     search_fields = ("user__username","product__name","razorpay_order_id")
#     list_filter = ("is_paid","created_at")
#     readonly_fields = ("razorpay_order_id","razorpay_payment_id","razorpay_signature")
    

    
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name',)
