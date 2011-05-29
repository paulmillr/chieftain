from django import template
from django.utils.safestring import mark_safe
from hashlib import md5

register = template.Library()


def strip(ip):
    return md5(ip).hexdigest()[:5]


def haship(value, arg=''):
    """Hashes first two blocks if IP address."""
    ip = value.split('.')
    return mark_safe('.'.join([strip(str(ip[:2]))] + ip[2:]))

register.filter(haship)
