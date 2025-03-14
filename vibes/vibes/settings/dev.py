from .base import *
import os
import socket  # only if you haven't already imported this

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SQLITE = os.getenv('SQLITE', False)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


INSTALLED_APPS = INSTALLED_APPS + [
    "debug_toolbar",
]

MIDDLEWARE = MIDDLEWARE + [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if SQLITE == "True":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
            'TEST': {
                'CHARSET': None,
                'COLLATION': None,
                'NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
                'MIRROR': None
            }
        }
    }



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-y^6hxareml6)cz81@z6(7a--fof^09wb24%e)vcj-$4#n91^bs"


# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# # See https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

AWS_S3_FILE_OVERWRITE = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",  # Example: S3 storage
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# staticfiles
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

EMAIL_VALIDATOR_TEST_ENV=True

# pwa
PWA_APP_ICONS = [
    {
        'src': '/static/images/sandp.png',
        'sizes': '160x160'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/images/sandp.png',
        'sizes': '160x160'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/sandp.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_SCREENSHOTS = [
    {
      'src': '/static/images/sandp.png',
      'sizes': '750x1334',
      "type": "image/png"
    }
]


GOOGLE_ANALYTICS_CODE = False
GOOGLE_ANALYTICS_ENABLE = False
