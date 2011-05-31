from django.template import Library

register = Library()


@register.filter
def split(str, splitter):
    return str.split(splitter)
