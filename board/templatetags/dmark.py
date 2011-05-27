from board.dmark import DMark
from django import template
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()


def dmark(value):
    """
    Runs DMark over a given value.

    Syntax::

        {{ value|dmark }}
    """
    return mark_safe(DMark().convert(force_unicode(value)))

dmark.is_safe = True
register.filter(dmark)
