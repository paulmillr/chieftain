# encoding: utf-8
from settings_default import *
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1')
MIDDLEWARE_CLASSES += 'debug_toolbar.middleware.DebugToolbarMiddleware',
INSTALLED_APPS += (
    'pytils',
    'debug_toolbar',
    'django_extensions',
)
