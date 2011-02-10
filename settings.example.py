DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('paul', 'pbagwl@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2',
            #'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'klipped',  # Or path to database file if using sqlite3.
        'USER': 'klipped',  # Not used with sqlite3.
        'PASSWORD': 'klipped',  # Not used with sqlite3.
        'HOST': '',  # Empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Empty string for default. Not used with sqlite3.
    }
}

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Kiev'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

SITE_ID = 1
USE_I18N = True
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/klipped/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://2-ch.ru/media/'
STATIC_ROOT = MEDIA_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5akd0aok29i0432jijisaj929001asd'

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
    'opt.StatsMiddleware',
    #'opt.SQLLogToConsoleMiddleware',
)

ROOT_URLCONF = 'klipped.urls'

TEMPLATE_DIRS = (
    '/home/klipped/board/templates',
    # Put strings here, like
    # "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.markup',
    'board',
)
