# encoding: utf-8
import os.path

MANAGERS = ADMINS = (
    #('Your name', 'your_email@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2',
            #'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Empty string for default. Not used with sqlite3.
    },
    'wakaba': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'OPTIONS': {
            'MAX_ENTRIES': 10000
        }
    }
}

REDIS_INFO = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
}

GEOIP_PATH = '/var/geoip/'
DISABLE_CAPTCHA = False
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
SITE_TITLE = u'Два.ч'
SITE_URL = 'http://2ch.so/'
WAKABA_PATH = '/var/2ch/'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CACHE_DIR = 'cache'
MEDIA_ROOT = os.path.join(BASE_DIR, 'files')
MEDIA_URL = '{0}files/'.format(BASE_DIR)
STATIC_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '{0}media/'.format(BASE_DIR)
SECRET_KEY = 'dsafaweihr8932rwefjiaweji'

PUBSUB = {
    'host': '127.0.0.1',
    'port': 9120,
}
