from django import template
from django.conf import settings
register = template.Library()


@register.simple_tag
def setting(name):
    return unicode(settings.__getattr__(name))
