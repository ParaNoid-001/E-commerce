
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db import models
from account.models import User
from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from io import BytesIO
import logging

from xhtml2pdf import pisa
import os
logger = logging.getLogger(__name__)

current_time = timezone.now()
timezone.now()
class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Product Category'  # Singular name in admin
        verbose_name_plural = 'Product Categories'  # Plural name in admin
        ordering = ['name']  # Default ordering in admin



class Product(models.Model):
    image = models.ImageField(upload_to='products/')
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    categories = models.ManyToManyField(Category, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def delete(self):
        self.is_active = False
        self.save()  # "Deletes" by hiding instead of removing
        
    class Meta:
        verbose_name = 'Store Product'  # Singular name in admin
        verbose_name_plural = 'Store Products'  # Plural name in admin
        ordering = ['-created_at']  # Newest first by default


class Order (models.Model):
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(
        max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(
        max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    product_name = models.CharField(max_length=200, blank=True)  # Backup in case product is deleted
    product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    
    
    def save(self, *args, **kwargs):
        if self.product and not self.product_name:  # Auto-fill product details
            self.product_name = self.product.name
            self.product_price = self.product.price
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Customer Order'  # Singular name in admin
        verbose_name_plural = 'Customer Orders'  # Plural name in admin
        ordering = ['-created_at']  # Newest first by default
        indexes = [
            models.Index(fields=['razorpay_order_id']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        
    def get_total_amount(self):
        """Calculate total amount for all items in the same order"""
        orders = Order.objects.filter(
            razorpay_order_id=self.razorpay_order_id,
            is_paid=True
        )
        return sum(order.amount for order in orders)

    def __str__(self):
        product_name = self.product.name if self.product else self.product_name
        return f'Order {self.id} - {product_name} - {self.amount}'

    def generate_receipt_pdf(self):
        """Generate PDF receipt and return as bytes"""
        template_path = 'emails/order_receipt_pdf.html'
        context = {
            'order': self,
            'items': self.items.all(),
            'date': self.created_at.strftime("%B %d, %Y"),
            'company_name': settings.COMPANY_NAME,  # Add to settings.py
            'company_address': settings.COMPANY_ADDRESS,
        }
        
        html = render_to_string(template_path, context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            return result.getvalue()
        return None

    def send_confirmation_email(self):
        """Send order confirmation email with PDF receipt attached"""
        subject = f"Order Confirmation - #{self.razorpay_order_id}"
        context = {
            'order': self,
            'items': self.items.all(),
            'user': self.user,
            'support_email': settings.SUPPORT_EMAIL,
             'company_name': settings.COMPANY_NAME,
        }
        
        # Render email content
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Generate PDF receipt
        pdf_content = self.generate_receipt_pdf()
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.user.email],
        )
        email.attach_alternative(html_message, "text/html")
        
        if pdf_content:
            email.attach(
                filename=f"Receipt-{self.razorpay_payment_id}.pdf",
                content=pdf_content,
                mimetype="application/pdf"
            )
        
        try:
            email.send()
            self.email_sent = True
            self.save(update_fields=['email_sent'])
            logger.info(f"Order confirmation email sent for order {self.id}")
        except Exception as e:
            logger.error(f"Error sending order confirmation email: {str(e)}")
            raise
    
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)  # String reference
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
    
    class Meta:
        verbose_name = 'Ordered Item'  # Singular name in admin
        verbose_name_plural = 'Ordered Items'  # Plural name in admin

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.db import models
# from account.models import User
# from django.conf import settings
# from django.utils import timezone

# current_time = timezone.now()
# timezone.now()
# class Category(models.Model):
#     name = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class Product(models.Model):
#     image = models.ImageField(upload_to='products/')
#     name = models.CharField(max_length=255)
#     description = models.TextField(max_length=255, blank=True)
#     categories = models.ManyToManyField(Category, related_name='products')
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.name
    
#     def delete(self):
#         self.is_active = False
#         self.save()  # "Deletes" by hiding instead of removing


# class Order (models.Model):
    
#     STATUS_CHOICES = [
#         ('created', 'Created'),
#         ('paid', 'Paid'),
#         ('shipped', 'Shipped'),
#         ('delivered', 'Delivered'),
#         ('cancelled', 'Cancelled'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
#     razorpay_payment_id = models.CharField(
#         max_length=255, blank=True, null=True)
#     razorpay_signature = models.CharField(
#         max_length=255, blank=True, null=True)
#     is_paid = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     email_sent = models.BooleanField(default=False)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
#     product_name = models.CharField(max_length=200, blank=True)  # Backup in case product is deleted
#     product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
#     def save(self, *args, **kwargs):
#         if self.product and not self.product_name:  # Auto-fill product details
#             self.product_name = self.product.name
#             self.product_price = self.product.price
#         super().save(*args, **kwargs)
        
#     class Meta:
#         ordering = ['-created_at']
        
#     def get_total_amount(self):
#         """Calculate total amount for all items in the same order"""
#         orders = Order.objects.filter(
#             razorpay_order_id=self.razorpay_order_id,
#             is_paid=True
#         )
#         return sum(order.amount for order in orders)

#     def __str__(self):
#         return f'order {self.id} - {self.product.name} - {self.amount}'


# # class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey('product.Product', on_delete=models.CASCADE)  # String reference
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
    
    
    



