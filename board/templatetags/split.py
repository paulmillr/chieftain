from django import template
register = template.Library()


@register.filter
def split(str, splitter):
    return str.split(splitter)
