from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import User
from .models import Cart

from product.models import Order
from cart.models import Cart

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        
@receiver(post_save, sender=Order)
def delete_cart_after_payment(sender, instance, created, **kwargs):
    """
    Delete the user's cart when an order is marked as paid
    """
    if instance.is_paid and not created:  # Only when updating to paid status
        Cart.objects.filter(user=instance.user).delete()