from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.decorators import decorator_from_middleware
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

from django.middleware.csrf import CsrfViewMiddleware
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render, redirect, get_object_or_404 # Import render to render templates, redirect for navigation
from django.contrib import messages  # Import messages for flash messages
from .models import Contact # Import the Recipe model
from django.core.validators import validate_slug
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
#from django.contrib.auth.models import User 
from django.core.mail import send_mail
from django.conf import settings
import logging

from django.urls import reverse  # Import reverse to generate URLs
from django.template.loader import render_to_string  # Import render_to_string for rendering templates to strings




