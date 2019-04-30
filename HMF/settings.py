'''
Created on Jun 12, 2013

@author: Steven
'''

# ===============================================================================
# THIRD_PARTY IMPORTS
# ===============================================================================
import os

# ===============================================================================
# SETUP LOCAL/PRODUCTION SPECIFIC VARIABLES
# ===============================================================================
DEBUG = True
TEMPLATE_DEBUG = DEBUG
CRISPY_FAIL_SILENTLY = not DEBUG

from .secret_settings import *

# ===============================================================================
# THE PROJECT DIRECTORY
# ===============================================================================
# The directory above the one this very file is in (top-level HMFcalc)
ROOT_DIR = os.path.split(os.path.dirname(__file__))[0]

# ===============================================================================
# SOME NON-DEFAULT SETTINGS
# ===============================================================================
# This apparently needs to be here to let people actually access the site?
ALLOWED_HOSTS = '*'

# ===============================================================================
# DATABASE SETTINGS
# ===============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ROOT_DIR + '/db',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}

# ===============================================================================
# INSTALLED APPS
# ===============================================================================
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analytical',
    'crispy_forms',
    'HMFcalc',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# ===============================================================================
# CRISPY SETTINGS
# ===============================================================================

CRISPY_TEMPLATE_PACK = "bootstrap4"

# ===============================================================================
# LOGGING SETUP
# ===============================================================================


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },

    },
    'handlers': {
        'console_dev': {
            'level': os.getenv("LOGLEVEL", "ERROR"),
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler'
        },
        'console_prod': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console_dev', 'console_prod'],
            'level': 'INFO',
            'propagate': True,
        },
        "HMFcalc": {
            'handlers': ['console_dev', 'console_prod'],
            'level': "INFO"
        }
    }
}

# ===============================================================================
# LOCALE SETTINGS
# ===============================================================================
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# ===============================================================================
# HOW TO GET TO MEDIA/STATIC FILES
# ===============================================================================
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ROOT_DIR + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# ===============================================================================
# TEMPLATES ETC.
# ===============================================================================

TEMPLATES = [
    {
        "BACKEND": 'django.template.backends.django.DjangoTemplates',
        "DIRS": [os.path.join(ROOT_DIR, 'templates')],
        "APP_DIRS": True,
    }
]

# # List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
#     #     'django.template.loaders.eggs.Loader',
# )
#
# TEMPLATE_DIRS = (os.path.join(ROOT_DIR, 'templates'),
#                  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
#                  # Always use forward slashes, even on Windows.
#                  # Don't forget to use absolute paths, not relative paths.
#                  )

# TEMPLATE_CONTEXT_PROCESSORS = (
#     "django.core.context_processors.static",
# )
# ===============================================================================
# MISCELLANEOUS
# ===============================================================================

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'HMF.urls'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'HMF.wsgi.application'
SESSION_SAVE_EVERY_REQUEST = True

# ===============================================================================
# EMAIL SETUP
# ===============================================================================
EMAIL_USE_TLS = True  # Whether to use a TLS (secure) connection when talking to the SMTP server.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = HOST_EMAIL
SERVER_EMAIL = HOST_EMAIL
DEFAULT_FROM_EMAIL = SERVER_EMAIL

ADMINS = (
    ('Steven', MY_EMAIL),
)

MANAGERS = ADMINS
CONTACT_RECIPIENTS = MY_EMAIL
