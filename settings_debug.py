# encoding: utf-8
from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ("127.0.0.1",)

try:
    import debug_toolbar
    import django_extensions
    import pytils
except ImportError:
    pass
else:
    INSTALLED_APPS += (
        "pytils",
        "debug_toolbar",
        "django_extensions",
    )

    MIDDLEWARE_CLASSES += (
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
