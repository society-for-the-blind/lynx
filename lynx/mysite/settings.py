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
import pathlib

# NOTE The  `sops`  command   depends  on  the  3
#      `AZURE_*` environment variables `export`ed
#      from `./secrect/sp.kdbx`.

project_dir =  pathlib.Path(__file__).parent.parent.parent
# This will promptly blow up if the file doesn't exist
secrets_file = (project_dir / 'secrets' / 'lynx_settings.sops.json').resolve(strict=True)
decrypted = subprocess.run(["sops", "--decrypt", str(secrets_file)], capture_output=True)
deployment_environment = os.environ['DEPLOY_ENV']
config = json.loads(decrypted.stdout)[deployment_environment]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# NOTE Removed hard-coded secret {{-
# + pros: More secure.
# + cons: New value on every re-start, thus users existing
#         sessions will be dropped on those occasions.
# }}-
SECRET_KEY = str((subprocess.run(["openssl", "rand", "-hex", "52"], capture_output=True)).stdout, 'utf-8').strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if (deployment_environment == 'dev') else False

ALLOWED_HOSTS = [ os.environ.get('HTTPS_DOMAIN', '') ] + [ 'localhost' ]

# https://stackoverflow.com/a/38842030/1498178
CSRF_TRUSTED_ORIGINS = ['https://lynx.societyfortheblind.org']
# CSRF_TRUSTED_ORIGINS = ['https://lynx.societyfortheblind.org'] + ['http://192.168.64.4:8001']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'crispy_forms',
    "crispy_bootstrap5",
    'mathfilters',
    'reversion',
    'django_filters',
    'django_pgviews',
    'simple_history',
    'django_crontab',
    'lynx'
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

# The default is `True`, but it doesn't  work,  even
# if set explicitly, so set it to `False`.
#
# HISTORICAL NOTE:
#     There was no `settings.py` before I took over,  so
#     no  history  on  this.  Megan's  solution  to  avoid
#     checking secrets into version control was to  simply
#     omit it. The first version of this file  was  pulled
#     from the production server, and  can't  remember  if
#     this setting was there or not.
APPEND_SLASH = False

EMAIL_HOST = 'blizzard.mxrouting.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = config['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
SERVER_EMAIL = EMAIL_HOST_USER
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

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

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

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

DJANGO_DIR = os.environ['DJANGO_DIR']

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(DJANGO_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(DJANGO_DIR, 'media')

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
