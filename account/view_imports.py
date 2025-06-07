from django.shortcuts import render, redirect, get_object_or_404 # Import render to render templates, redirect for navigation
from django.contrib import messages  # Import messages for flash messages
import logging
from django.http import HttpResponse

from django.db.models import Q
from django.db.models import Count
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from account.utils import send_activation_email, send_reset_password_email
from account.models import User, Address
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .forms import (
    RegistrationForm, UserProfileForm, CustomPasswordChangeForm,
    CustomPasswordResetForm, AddressForm, AdminRegistrationForm
)
#from .models import MEAL_CATEGORIES, DIETARY_PREFERENCES, DIFFICULTY_LEVELS, CUISINE_TYPES
from .models import *
from django.urls import reverse_lazy  # Import reverse_lazy for URL redirection
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView  # Import class-based views

from django.core.validators import validate_slug
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User  # Import User model for user-related functionalities

from django.template.loader import render_to_string  # Import render_to_string for rendering templates to strings
from django.utils.html import strip_tags  # Import strip_tags to remove HTML tags from strings
from django.conf import settings  # Import settings to access email configuration
from django.urls import reverse  # Import reverse to generate URLs
import os
import smtplib 
from django.template.exceptions import TemplateDoesNotExist
from django.contrib.auth.decorators import login_required  # Import login_required to protect views
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import razorpay
from product.models import Order
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
# Payment Gateway
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# <-----------decorators-------------------->

from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.decorators import decorator_from_middleware
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

from django.middleware.csrf import CsrfViewMiddleware
