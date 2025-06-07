from django.db import models
from account.models import User
from product.models import Product
import datetime
from django.utils import timezone

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now) # New field
    #created_at = models.DateTimeField(default=timezone.now)


    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']  # New ordering

    def __str__(self):
        return f'{self.user} - {self.product}'