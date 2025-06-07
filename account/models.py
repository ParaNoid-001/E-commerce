from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.core.validators import FileExtensionValidator

# Define a custom manager for the User model.
class UserManager(BaseUserManager):
    """
    A custom manager to handle the creation of users and superusers.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        - email: The user's email address (required).
        - password: The user's password (required).
        - extra_fields: Additional fields to be set for the user (optional).
        """
        if not email:
            raise ValueError("User must have a valid email address")

        # Normalize the email address to a consistent format
        email = self.normalize_email(email)

        # Create an instance of the user model
        user = self.model(email=email, **extra_fields)

        # Set the user's password (hashed internally)
        user.set_password(password)

        # Save the user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        - Superuser must have is_staff=True and is_superuser=True.
        - Additional flags like is_customer and is_seller are also set to True.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_customer', True)
        extra_fields.setdefault('is_seller', True)

        # Ensure required superuser flags are properly set
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if password is None:
            raise ValueError("Superuser must have a password.")

        # Use the create_user method to create a superuser
        return self.create_user(email, password, **extra_fields)
    

# Define a custom User model by extending AbstractBaseUser.
class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom User model that uses email instead of username for authentication.
    """
    # User fields
   
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('full name'), max_length=255)
    profile_picture = models.ImageField(upload_to='profile_photo/',default='profile_photo/default-profile-pic.jpg',blank=True,null=True,
                                        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])  
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True) 
    
    #address = models.CharField(max_length=255, blank=True,null=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    
    is_active = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    
    is_customer = models.BooleanField(default=True) 
    is_seller = models.BooleanField(default=False)  
    
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    # Specify the unique identifier for authentication
    USERNAME_FIELD = 'email'

    # Fields required when creating a superuser (besides USERNAME_FIELD)
    REQUIRED_FIELDS = ['name']

    # Use the custom manager for this model
    objects = UserManager()

    class Meta:
        """
        Meta options for the User model.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        """
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        """
        String representation of the user.
        - Returns the email address as the representation.
        """
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Check if the user has a specific permission.
        - Only superusers have all permissions.
        """
        if self.is_superuser:
            return True
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """
        Check if the user has permissions to view the app identified by `app_label`.
        - Only superusers have access to all apps.
        """
        if self.is_superuser:
            return True
        return super().has_module_perms(app_label)
  
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_name = models.CharField(max_length=150)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    

    country = CountryField(blank_label='(Select country)')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']
        constraints = [
        models.UniqueConstraint(
            fields=['user', 'is_default'],
            condition=models.Q(is_default=True),
            name='unique_default_address'
        )
    ]

    def __str__(self):
        return f"{self.address_name} - {self.street_address}"