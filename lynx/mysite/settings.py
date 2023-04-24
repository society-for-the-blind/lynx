"""
Django settings for mysite project.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import json
import subprocess

# The  `sops`  command   depends  on  the  3
# `AZURE_*` environment variables `export`ed
# from `./secrect/sp.kdbx`.
decrypted = subprocess.run(["sops", "--decrypt", "secrets/lynx_settings.sops.json"], capture_output=True)
config = json.loads(decrypted.stdout)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['192.168.1.82', 'localhost', '127.0.0.1', '35.231.66.229', '192.168.1.76', '51.141.168.67']
ALLOWED_HOSTS = config['ALLOWED_HOSTS'] + ['192.168.64.4']

INSTALLED_APPS = [
    'lynx.apps.LynxConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'crispy_forms',
    'mathfilters',
    'reversion',
    'django_filters',
    'django_pgviews',
    'simple_history',
    'django_crontab'
]

SITE_ID=1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# WARNING
# https://www.enterprisedb.com/blog/how-safely-change-postgres-user-password-psql

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':      config['DATABASE']['NAME'],
        'USER':      config['DATABASE']['USER'],
        'PASSWORD':  config['DATABASE']['PASSWORD'],
        'HOST':      config['DATABASE']['HOST'],
        'PORT':      config['DATABASE']['PORT'],
        'OPTIONS': {
            'options': '-c search_path=' +  config['DATABASE']['SCHEMA']
        }
    }
}

# After upgrading from Django 2.2 to 4.1, got this warning (times the number of all existing models):
#
#       account.Account: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
#       HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
#
# Solution:
# https://stackoverflow.com/a/66971813/1498178

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# DataFlair #Logging Information
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'handlers': {
#        'file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': 'lynx-debug.log',
#        },
#        'console': {
#            'class': 'logging.StreamHandler',
#        },
#    },
#    'loggers': {
#        'django': {
#            'handlers': ['file', 'console'],
#            'level': 'DEBUG',
#            'propagate': True,
#            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
#        },
#    },
#    "formatters": {
#        "app": {
#            "format": (
#                u"%(asctime)s [%(levelname)-8s] "
#                "(%(module)s.%(funcName)s) %(message)s"
#            ),
#            "datefmt": "%Y-%m-%d %H:%M:%S",
#        },
#    },
#}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/lynx/'

APPEND_SLASH = False

EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = config['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
#SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True


if DEBUG:
    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    INTERNAL_IPS = ('127.0.0.1', '0.0.0.0')
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = '/var/www/lynx/slate-2/lynx/lynx/static'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
