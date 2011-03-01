# encoding: utf-8
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MANAGERS = ADMINS = (
    ('test', 'test@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2',
            #'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test',  # Or path to database file if using sqlite3.
        'USER': 'test',  # Not used with sqlite3.
        'PASSWORD': 'test',  # Not used with sqlite3.
        'HOST': '',  # Empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Empty string for default. Not used with sqlite3.
    }
}

CACHE_BACKEND = 'memcached://127.0.0.1:11211/?max_entries=10000'
PUBSUB = {
    'host': '127.0.0.1',
    'port': 8888,
}
GEOIP_PATH = '/home/klipped/contrib/'

DISABLE_CAPTCHA = True
RECAPTCHA_PUBLIC_KEY = 'r'
RECAPTCHA_PRIVATE_KEY = 'r'
# APPEND_SLASH = False
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Kiev'
LANGUAGE_CODE = 'ru'

SITE_ID = 1
USE_I18N = True
USE_L10N = True

SITE_TITLE = u'Два.ч 2.0 β'
SITE_URL = 'http://2ch.ru/'
FILES_URL = 'http://static.2ch.ru/'
BASE_DIR = os.path.dirname(__file__)
CACHE_DIR = 'cache'
MEDIA_ROOT = os.path.join(BASE_DIR, 'files')
MEDIA_URL = '{0}files/'.format(FILES_URL)
STATIC_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '{0}media/'.format(FILES_URL)

ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'tqaejwiqwjasidjaisjiq43uiiejwajeiqjwie'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'board.middleware.DisableCSRFMiddleware',
    'board.middleware.DenyMiddleware',

    # for debugging
    #'opt.middlewares.StatsMiddleware',
    #'opt.middlewares.SQLLogToConsoleMiddleware',
    #'opt.middlewares.ProfileMiddleware',
)

AUTH_PROFILE_MODULE = 'klipped.board.User'

ROOT_URLCONF = 'klipped.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'board', 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'board.context_processors.settings',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'klipped.board',
    'klipped.api',
    'klipped.modpanel',
    #'klipped.mobile',
)
