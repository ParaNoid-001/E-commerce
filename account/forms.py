from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm, 
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm
)
from django.contrib.auth import get_user_model
from account.models import User, Address
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField

User = get_user_model()

class RegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'profile_picture', 'dob', 'gender']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password')

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'placeholder': 'Current password',
            'class': 'form-control'
        })
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'New password',
            'class': 'form-control'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Confirm new password',
            'class': 'form-control'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', "The two password fields didn't match.")
        return cleaned_data

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("There is no account with this email address.")
        return email

class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def clean_is_default(self):
        is_default = self.cleaned_data.get('is_default')
        if is_default and self.user and self.user.addresses.filter(is_default=True).exists():
            if self.instance and self.instance.is_default:
                return is_default
            raise ValidationError("You already have a default address. Please unset it first.")
        return is_default
    
    country = CountryField().formfield()
    class Meta:
        model = Address
        fields = ['address_name', 'street_address', 'city', 'state', 'zip_code', 'country', 'is_default']
        widgets = {
            'address_name': forms.TextInput(attrs={'placeholder': 'e.g., Home, Office'}),
            'street_address': forms.TextInput(attrs={'placeholder': '123 Main St'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'zip_code': forms.TextInput(attrs={'placeholder': 'ZIP/Postal code'}),
            #'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        }

class AdminRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'dob', 'gender', 'phone_number', 'profile_picture']
        help_texts = {
            'email': 'Enter a valid email address',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user