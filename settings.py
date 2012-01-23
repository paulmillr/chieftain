# encoding: utf-8
try:
    from settings_local import *
except ImportError:
    print "Cannot import local settings"
    raise

DEBUG = False
TEMPLATE_DEBUG = DEBUG

MANAGERS = ADMINS = (
    # ("Your Name", "your_email@domain.com"),
)


#APPEND_SLASH = False
TIME_ZONE = "Europe/Kiev"
LANGUAGE_CODE = "en"

SITE_ID = 1
USE_I18N = True
USE_L10N = True

ADMIN_MEDIA_PREFIX = "/admin-media/"

TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",

    # enable this in production environment
    #("django.template.loaders.cached.Loader", (
    #    "django.template.loaders.filesystem.Loader",
    #    "django.template.loaders.app_directories.Loader",
    #)),
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "board.middleware.DisableCSRFMiddleware",
    "board.middleware.SessionDefaultsMiddleware",
    "board.middleware.DenyMiddleware",

    # for debugging
    #"opt.middlewares.StatsMiddleware",
    #"opt.middlewares.SQLLogToConsoleMiddleware",
    #"opt.middlewares.ProfileMiddleware",
)

AUTH_PROFILE_MODULE = "chieftain.board.User"

ROOT_URLCONF = "chieftain.urls"

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.media",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "board.context_processors.settings",
    "board.context_processors.session",
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.admin",
    "djangorestframework",
    "django_nose",
    "chieftain.board",
    "chieftain.converter",
    "chieftain.api1",
)

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
