from hashlib import md5

from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


def strip(ip):
    return md5(ip).hexdigest()[:5]


@register.filter
def haship(value, arg=""):
    ip = value.split(".")
    return mark_safe(".".join([strip(str(ip[:2]))] + ip[2:]))
