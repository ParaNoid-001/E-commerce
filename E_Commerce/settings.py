import os
from pathlib import Path
from dotenv import load_dotenv
import logging


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'


ALLOWED_HOSTS = []

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{process:d}] {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '''
                asctime: %(asctime)s
                levelname: %(levelname)s
                process: %(process)d
                module: %(module)s
                message: %(message)s
                pathname: %(pathname)s
                funcName: %(funcName)s
                lineno: %(lineno)d
            ''',
        },
    },
    'handlers': {
        # Development console handler
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # Production console handler
        'production_console': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # Application file handler
        'file_app': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'app.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        # Error file handler
        'file_errors': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        # Admin email handler
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'verbose',
        },
        # JSON log handler (for log aggregation systems)
        'json_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'json.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        # Django framework logs
        'django': {
            'handlers': ['console', 'production_console', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        # Database query logs
        'django.db.backends': {
            'handlers': ['file_app'] if DEBUG else [],  # Only log queries in debug
            'level': 'DEBUG',
            'propagate': False,
        },
        # Request errors
        'django.request': {
            'handlers': ['file_errors', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Security logs
        'django.security': {
            'handlers': ['file_errors', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Your apps
        'accounts': {
            'handlers': ['console', 'file_app', 'json_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'home': {
            'handlers': ['console', 'file_app', 'json_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'vege': {
            'handlers': ['console', 'file_app', 'json_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file_app', 'json_file'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
}

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Api
    'rest_framework',
    # External apps
    'core.apps.CoreConfig',
    'account.apps.AccountConfig',
    'customer.apps.CustomerConfig',
    'seller.apps.SellerConfig',
    'product.apps.ProductConfig',
    'cart.apps.CartConfig',
    'wishlist.apps.WishlistConfig',
    'deepseek_llm.apps.DeepseekLlmConfig',
    
]

AUTH_USER_MODEL = 'account.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'E_Commerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR/'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',  # Add this line to include the cart context processor
            ],
        },
    },
]

WSGI_APPLICATION = 'E_Commerce.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'  #UTC

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

#STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'account.User'  # Custom user model for authentication

# Email configuration
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Replace with your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')  # Replace with your email
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # Replace with your email password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # Replace with your email

SUPPORT_EMAIL = EMAIL_HOST_USER
CONTACT_FORM_RECIPIENT = os.environ.get('EMAIL_HOST_USER')
#EMAIL_USE_TLS = True


COMPANY_NAME = 'MVP Automotive'
COMPANY_ADDRESS = '13 st,Kolkata, 700105'
COMPANY_PHONE = '8101065218'

# Domain and site details
SITE_DOMAIN = 'http://127.0.0.1:8000'
SITE_NAME = 'MVP Automotive'

# Authentication Redirects
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

PASSWORD_RESET_TIME =15   # in minutes

from decouple import config
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = config("RAZORPAY_KEY_SECRET")
RAZORPAY_TEST_MODE = True

RAZORPAY_CALLBACK_URL = "http://127.0.0.1:8000/product/payment-varify/"

#GEMINI_API_KEY="AIzaSyCGURqKFdC5JyfYpn549-48TF7RXohxrIw"

MARKDOWN_EXTENSIONS = ['fenced_code', 'codehilite']

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


JAZZMIN_SETTINGS = {
    # Site Identity
    "site_title": "MVP Automotives Admin",
    "site_header": "MVP Automotives",
    "site_brand": "MVP Automotives",
    "welcome_sign": "Welcome to MVP Automotives Admin Panel",
    "copyright": "MVP Automotives Ltd",
    
    # UI Configuration
    "show_ui_builder": True,
    "related_modal_active": True,
    "custom_css": "css",  # Path to custom CSS
    
    # Icons Configuration
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "account.User": "fas fa-user-tie",
        "wishlist.Wishlist": "fas fa-heart",
        "product.Product": "fa-solid fa-shop",
        "account.Addresses": "fa-duotone fa-regular fa-location-dot",
        "product.Category": "fas fa-tags",
        "order.Order": "fas fa-brands fa-first-order", #<i class="fa-brands fa-first-order"></i>
        "cart.Cart": "fas fa-shopping-cart",
        "payment.Payment": "fas fa-credit-card",
    },
    
    # Top Menu Configuration
    "topmenu_links": [
        # External Links
        {
            "name": "Home", 
            "url": "home", 
            "icon": "fas fa-home",
            "permissions": ["auth.view_user"]
        },
        {
            "name": "Support", 
            "url": "contact_view", 
            "icon": "fas fa-headset"
        },
        {
            "name": "Documentation", 
            "url": "about", 
            "icon": "fas fa-book",
            "new_window": True
        },
        
        {
            "name": "Settings", 
            "url": "account_management", 
            "icon": "fas fa-cog",
            "new_window": True
        },
        
        # App Links (grouped)
        {
            "name": "Applications",
            "icon": "fas fa-th",
            "children": [
                {"name": "Users", "app": "account"},
                {"name": "Products", "app": "product"},
                {"name": "Orders", "app": "order"},
                {"name": "Payments", "app": "payment"},
                {"name": "Wishlists", "app": "wishlist"},
                {"name": "Carts", "app": "cart"},
            ]
        },
    ],
    
    # Sidebar Configuration
    "navigation_expanded": True,
    "show_sidebar": True,
    "show_sidebar_user": True,
    "show_sidebar_search": True,
    "show_sidebar_recent": True,
    "show_sidebar_favorites": True,
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Customization
    "changeform_format": "horizontal_tabs",  # horizontal_tabs or vertical_tabs
    "changeform_format_overrides": {
        "auth.user": "vertical_tabs",
        "auth.group": "vertical_tabs"
    },
    
    # Ordering
    "order_with_respect_to": [
        "product",
        "order",
        "account",
        "wishlist",
        "cart",
        "payment",
    ],
    
    # Search Bar
    "search_model": ["account.User", "product.Product", "order.Order"],
}