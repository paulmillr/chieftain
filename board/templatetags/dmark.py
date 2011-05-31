from board.dmark import DMark
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.filter
def dmark(value):
    """
        Run DMark over a given value.

        Syntax::

            {{ value|dmark }}
    """
    return mark_safe(DMark().convert(value))

dmark.is_safe = True
