"""
Django settings for slotted_need project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import sys
import dj_database_url
import sentry_sdk
if os.path.isfile('env.py'):
    import env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['.herokuapp.com',
                 'localhost',]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'nested_admin',
    'rest_framework',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.apple',
    # project apps
    'products',
    'orders',
    'users'
]

# Sited IDs
if DEBUG:
    SITE_ID = 1
else:
    SITE_ID = 2

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth
]

# django-allauth settings
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
# Allow authentication via username or email
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False
# Automatically logs the user in upon successful email confirmation.
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
# Autoconnect social account to existing matching email user
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
# Do not require email verification when signing up with social account
# as already email is authenticated by invitation
SOCIALACCOUNT_EMAIL_VERIFICATION = False

# Disable public signups (handled via custom adapter)
ACCOUNT_ALLOW_REGISTRATION = False
SOCIALACCOUNT_ALLOW_REGISTRATION = False
SOCIALACCOUNT_AUTO_SIGNUP = False

# Login/Logout redirect
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'account_login'

# Configure social account authentication 3rd party providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_OAUTH_SECRET'),
            'key': ''
        },
        'SCOPE': ['email'],
        'EMAIL_AUTHENTICATION': True,
        'EMAIL_AUTHENTICATION_AUTO_CONNECT': True
    },
    # 'apple': { ... }  # To be configured below
}

# Custom adapter to prevent unauthorised signin/signup
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

# Crispy bootstrap5 templates
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework Configuration
REST_FRAMEWORK = {
    # restrict API access to authenticated users
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    # enable filtering and ordering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    # configure pagination for API responses
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'slotted_need.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'slotted_need.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.parse(os.environ.get("DATABASE_URL"))
}

# Testing database
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_KEY")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_EMAIL")
SERVER_EMAIL = os.environ.get("DEFAULT_EMAIL")

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LOGGING CONFIGURATIONS
ADMINS = [
    ("Dimis", os.environ.get("DEFAULT_EMAIL")),
]

# Ensure the 'logs' directory exists (only needed for development)
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{asctime} {levelname} {message}",
            "style": "{",
        },
        "notification": {
            "format": "{levelname} {asctime}",
            "style": "{"
        }
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
        "file_log": {
            "level": "WARNING",
            "filters": ["require_debug_true"],
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, 'app.log'),
            "formatter": "verbose"
        },
        "mail_admins": {
            "level": "ERROR",
            # customised AdminEmailHandler
            "class": "slotted_need.logging_handlers.SimpleAdminEmailHandler",
            "formatter": "notification"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG"
    },
    "loggers": {
        "slotted_need": {
            "handlers": ["console", "file_log", "mail_admins"],
            "propagate": False,
            "level": "DEBUG"
        }
    }
}

# SENTRY config for production
sentry_sdk.init(
    dsn="https://1b05ed7470064c70d9b4fdcced9de681@o4508116014989312.ingest.de.sentry.io/4508116019707984",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
