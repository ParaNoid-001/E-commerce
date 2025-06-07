from django.db import models  # Import Django's models module
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.validators import validate_email

class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)

    email = models.EmailField(validators=[validate_email])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ['created_at']

    def __str__(self):
        return self.name
