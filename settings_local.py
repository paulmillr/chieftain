# encoding: utf-8
import os.path

MANAGERS = ADMINS = (
    #("Your name", "your_email@example.com"),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add "postgresql_psycopg2",
            #"postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "sqlite3",  # Or path to database file if using sqlite3.
        "USER": "root",  # Not used with sqlite3.
        "PASSWORD": "root",  # Not used with sqlite3.
        "HOST": "",  # Empty string for localhost. Not used with sqlite3.
        "PORT": "",  # Empty string for default. Not used with sqlite3.
    },
    "wakaba": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        "OPTIONS": {
            "MAX_ENTRIES": 10000
        }
    }
}

REDIS_INFO = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 0,
}

GEOIP_PATH = "/var/geoip/"
DISABLE_CAPTCHA = True
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""
SITE_TITLE = u"Chieftain"
SITE_URL = "http://127.0.0.1:8000/"
WAKABA_PATH = "/var/wakaba/"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CACHE_DIR = "cache"
MEDIA_ROOT = os.path.join(BASE_DIR, "files")
MEDIA_URL = "/files/"
STATIC_ROOT = os.path.join(BASE_DIR, "media")
STATIC_URL = "/media/"
SECRET_KEY = "dsafaweihr8932rwefjiaweji"

PUBSUB = {
    "host": "127.0.0.1",
    "port": 9120,
}
